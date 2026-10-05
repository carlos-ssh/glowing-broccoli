// Fase 2: driver en espacio de usuario del Maschine MK1 -> puerto MIDI virtual (CoreMIDI).
//
//   ./mk1midi              abre el MK1 y publica el puerto "Maschine MK1"
//   ./mk1midi --selftest   no necesita hardware: comprueba que CoreMIDI funciona
//   ./mk1midi --debug      ademas imprime cada evento crudo que llega del MK1
//
// Formatos (de sound/usb/caiaq del kernel de Linux, SIN verificar aun con hardware):
//   EP1 0x81, cmd 0x04 READ_IO : bitmap de 42 botones (bit i = boton i)
//   EP1 0x81, cmd 0x02 READ_ERP: 22 bytes, 11 knobs sin fin de dos fases (a,b) -> posicion 0..999
//   EP4 0x84                   : 16 x u16 LE; bits 15..12 = id del pad, 11..0 = presion
//
// Mapeo MIDI por defecto (generico, sirve en Ableton y cualquier DAW):
//   pads     canal 1  notas 36..51  (velocity segun presion)
//   botones  canal 2  nota = numero de bit (0..41)
//   knobs    canal 1  CC 20..27 (K1..K8)  y CC 28..30 (VOLUME, TEMPO, SWING), RELATIVOS (1 = +, 127 = -)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <CoreFoundation/CoreFoundation.h>
#include <CoreMIDI/CoreMIDI.h>
#include <IOKit/IOKitLib.h>
#include <IOKit/IOCFPlugIn.h>
#include <IOKit/usb/IOUSBLib.h>
#include <IOKit/usb/USB.h>

static int g_debug;
static MIDIClientRef g_client;
static MIDIEndpointRef g_src;
static pthread_mutex_t g_mu = PTHREAD_MUTEX_INITIALIZER;

// ------------------------------------------------------------------ MIDI out
static void midi_send(UInt8 status, UInt8 d1, UInt8 d2) {
    Byte buf[64];
    MIDIPacketList *pl = (MIDIPacketList *)buf;
    MIDIPacket *pk = MIDIPacketListInit(pl);
    Byte msg[3] = {status, d1, d2};
    pk = MIDIPacketListAdd(pl, sizeof buf, pk, 0, 3, msg);
    pthread_mutex_lock(&g_mu);
    if (pk) MIDIReceived(g_src, pl);
    pthread_mutex_unlock(&g_mu);
}

// ------------------------------------------------------------------ botones
// Orden de bits tal como el driver de Linux (keycode_maschine). Los nombres marcados con ? son dudosos.
static const char *BTN_NAME[42] = {
    "MUTE", "SOLO", "SELECT", "DUPLICATE", "NAVIGATE", "PAD MODE", "PATTERN", "SCENE", "(libre)",
    "REC", "ERASE", "SHIFT", "GRID", "TRANSPORT >", "TRANSPORT <", "RESTART",
    "E", "F", "G", "H", "D", "C", "B", "A",
    "CONTROL", "BROWSE", "PAGE <?", "F1?", "F2?", "PAGE >?", "SAMPLING", "STEP",
    "KEY 8", "KEY 7", "KEY 6", "KEY 5", "KEY 4", "KEY 3", "KEY 2", "KEY 1",
    "NOTE REPEAT", "PLAY"
};
static UInt8 g_btn_prev[6];

static void on_buttons(const UInt8 *b, int len) {
    for (int i = 0; i < 42 && i < len * 8; i++) {
        int now = (b[i / 8] >> (i % 8)) & 1, was = (g_btn_prev[i / 8] >> (i % 8)) & 1;
        if (now == was) continue;
        if (g_debug) printf("boton %2d %-12s %s\n", i, BTN_NAME[i], now ? "ON" : "off");
        midi_send(now ? 0x91 : 0x81, (UInt8)i, now ? 127 : 0);
    }
    memcpy(g_btn_prev, b, len < 6 ? len : 6);
}

// ------------------------------------------------------------------ knobs sin fin
// decode_erp: copia del algoritmo del driver de Linux (dos tapers desfasados 90 grados).
static unsigned decode_erp(unsigned char a, unsigned char b) {
    const int HIGH = 268, LOW = -7, range = HIGH - LOW;
    const int D90 = range / 2, D180 = range, D270 = D90 + D180, D360 = D180 * 2;
    int mid = (HIGH + LOW) / 2, wb = abs(mid - a) - (range / 2 - 100) / 2, pa, pb;
    if (wb < 0) wb = 0;
    if (wb > 100) wb = 100;
    int wa = 100 - wb;
    if (a < mid) { pb = b - LOW + D270; if (pb >= D360) pb -= D360; } else pb = HIGH - b + D90;
    if (b > mid) pa = a - LOW; else pa = HIGH - a + D180;
    int ret = (pa * wa + pb * wb) * 10 / D360;
    if (ret < 0) ret += 1000;
    if (ret >= 1000) ret -= 1000;
    return (unsigned)ret;
}

// indice 0..7 = K1..K8, 8..10 = VOLUME, TEMPO, SWING; pares (a,b) en el buffer de 22 bytes
static const int ERP_AB[11][2] = {
    {21, 20}, {15, 14}, {9, 8}, {3, 2},     // bajo la pantalla izquierda
    {19, 18}, {13, 12}, {7, 6}, {1, 0},     // bajo la pantalla derecha
    {17, 16}, {11, 10}, {5, 4},             // volume, tempo, swing
};
#define TICK 10     // unidades (de 1000 por vuelta) por cada paso relativo
static int g_erp_last[11], g_erp_rem[11], g_erp_init;

static void on_erp(const UInt8 *b, int len) {
    if (len < 22) return;
    for (int k = 0; k < 11; k++) {
        int cur = (int)decode_erp(b[ERP_AB[k][0]], b[ERP_AB[k][1]]);
        if (!g_erp_init) { g_erp_last[k] = cur; continue; }
        int d = cur - g_erp_last[k];
        if (d > 500) d -= 1000; else if (d < -500) d += 1000;
        g_erp_last[k] = cur;
        d += g_erp_rem[k];
        int steps = d / TICK;
        g_erp_rem[k] = d - steps * TICK;
        if (steps == 0) continue;
        if (g_debug) printf("knob %2d %+d pasos (pos %d)\n", k, steps, cur);
        UInt8 cc = (UInt8)(20 + k), val = steps > 0 ? 1 : 127;
        for (int n = abs(steps) > 16 ? 16 : abs(steps); n > 0; n--) midi_send(0xB0, cc, val);
    }
    g_erp_init = 1;
}

// ------------------------------------------------------------------ pads
#define PAD_ON  0x080   // presion para NoteOn
#define PAD_OFF 0x040   // presion para NoteOff
static int g_pad_on[16], g_pad_peak[16];

static void on_pads(const UInt8 *b, int len) {
    if (len < 32) return;
    for (int i = 0; i < 16; i++) {
        unsigned v = b[2 * i] | (b[2 * i + 1] << 8);
        int id = v >> 12, p = v & 0xFFF;
        if (g_pad_on[id]) {
            if (p > g_pad_peak[id]) g_pad_peak[id] = p;
            if (p < PAD_OFF) {
                g_pad_on[id] = 0;
                if (g_debug) printf("pad %2d off\n", id);
                midi_send(0x80, (UInt8)(36 + id), 0);
            }
        } else if (p > PAD_ON) {
            g_pad_on[id] = 1; g_pad_peak[id] = p;
            int vel = 1 + p * 126 / 0xFFF;
            if (g_debug) printf("pad %2d ON  presion=%d vel=%d\n", id, p, vel);
            midi_send(0x90, (UInt8)(36 + id), (UInt8)vel);
        }
    }
}

// ------------------------------------------------------------------ USB
static IOUSBInterfaceInterface300 **itf;
static UInt8 pipe_of[256];

static void *ep1_reader(void *arg) {
    (void)arg; UInt8 buf[512];
    for (;;) {
        UInt32 n = sizeof buf;
        IOReturn r = (*itf)->ReadPipe(itf, pipe_of[0x81], buf, &n);
        if (r) { fprintf(stderr, "EP1 error 0x%08X\n", r); sleep(1); continue; }
        if (n < 1) continue;
        if (g_debug > 1) { printf("EP1 cmd %02X len %u\n", buf[0], n); }
        if (buf[0] == 0x04) on_buttons(buf + 1, (int)n - 1);
        else if (buf[0] == 0x02) on_erp(buf + 1, (int)n - 1);
    }
    return NULL;
}

static void *ep4_reader(void *arg) {
    (void)arg; UInt8 buf[512];
    for (;;) {
        UInt32 n = sizeof buf;
        IOReturn r = (*itf)->ReadPipe(itf, pipe_of[0x84], buf, &n);
        if (r) { fprintf(stderr, "EP4 error 0x%08X\n", r); sleep(1); continue; }
        on_pads(buf, (int)n);
    }
    return NULL;
}

static IOReturn ep1_send(UInt8 cmd, const UInt8 *args, int len) {
    UInt8 b[64] = {cmd};
    if (len) memcpy(b + 1, args, len);
    return (*itf)->WritePipe(itf, pipe_of[0x01], b, len + 1);
}

static int open_mk1(void) {
    int vid = 0x17CC, pid = 0x0808;
    CFMutableDictionaryRef m = IOServiceMatching(kIOUSBDeviceClassName);
    CFNumberRef v = CFNumberCreate(NULL, kCFNumberIntType, &vid), p = CFNumberCreate(NULL, kCFNumberIntType, &pid);
    CFDictionarySetValue(m, CFSTR(kUSBVendorID), v);
    CFDictionarySetValue(m, CFSTR(kUSBProductID), p);
    io_service_t dev = IOServiceGetMatchingService(0, m);
    if (!dev) { fputs("MK1 no encontrado (conectado por USB?)\n", stderr); return 1; }
    IOCFPlugInInterface **plug; SInt32 score;
    IOCreatePlugInInterfaceForService(dev, kIOUSBDeviceUserClientTypeID, kIOCFPlugInInterfaceID, &plug, &score);
    IOUSBDeviceInterface320 **d;
    (*plug)->QueryInterface(plug, CFUUIDGetUUIDBytes(kIOUSBDeviceInterfaceID320), (LPVOID *)&d);
    IOReturn r = (*d)->USBDeviceOpenSeize(d);
    if (r) { fprintf(stderr, "USBDeviceOpenSeize fallo 0x%08X\n", r); return 2; }
    (*d)->SetConfiguration(d, 1);
    IOUSBFindInterfaceRequest req = { kIOUSBFindInterfaceDontCare, kIOUSBFindInterfaceDontCare,
                                      kIOUSBFindInterfaceDontCare, kIOUSBFindInterfaceDontCare };
    io_iterator_t it; (*d)->CreateInterfaceIterator(d, &req, &it);
    io_service_t is = IOIteratorNext(it);
    if (!is) { fputs("sin interfaz USB\n", stderr); return 3; }
    IOCreatePlugInInterfaceForService(is, kIOUSBInterfaceUserClientTypeID, kIOCFPlugInInterfaceID, &plug, &score);
    (*plug)->QueryInterface(plug, CFUUIDGetUUIDBytes(kIOUSBInterfaceInterfaceID300), (LPVOID *)&itf);
    r = (*itf)->USBInterfaceOpen(itf);
    if (r) {
        fprintf(stderr, "USBInterfaceOpen fallo 0x%08X%s\n", r,
                r == (IOReturn)0xE00002C5 ? " (el kext de NI sigue reclamando el dispositivo: ver README)" : "");
        return 4;
    }
    (*itf)->SetAlternateInterface(itf, 1);
    UInt8 n; (*itf)->GetNumEndpoints(itf, &n);
    for (UInt8 pr = 1; pr <= n; pr++) {
        UInt8 dir, num, type, intv; UInt16 maxp;
        (*itf)->GetPipeProperties(itf, pr, &dir, &num, &type, &maxp, &intv);
        pipe_of[num | (dir == kUSBIn ? 0x80 : 0)] = pr;
    }
    if (!pipe_of[0x81] || !pipe_of[0x84] || !pipe_of[0x01]) { fputs("faltan endpoints\n", stderr); return 5; }
    return 0;
}

// ------------------------------------------------------------------ selftest
static volatile int g_selftest_got;
static void selftest_read(const MIDIPacketList *pl, void *rc, void *src) {
    (void)rc; (void)src;
    const MIDIPacket *pk = &pl->packet[0];
    for (UInt32 i = 0; i < pl->numPackets; i++, pk = MIDIPacketNext(pk))
        for (UInt16 j = 0; j + 2 < pk->length; j += 3) {   // CoreMIDI puede agrupar varios mensajes en un paquete
            printf("  recibido: %02X %02X %02X\n", pk->data[j], pk->data[j + 1], pk->data[j + 2]);
            g_selftest_got++;
        }
}

int main(int argc, char **argv) {
    int selftest = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--selftest")) selftest = 1;
        else if (!strcmp(argv[i], "--debug")) g_debug++;
        else { fprintf(stderr, "uso: %s [--selftest] [--debug]\n", argv[0]); return 64; }
    }
    MIDIClientCreate(CFSTR("Maschine MK1"), NULL, NULL, &g_client);
    OSStatus s = MIDISourceCreate(g_client, CFSTR("Maschine MK1"), &g_src);
    if (s) { fprintf(stderr, "MIDISourceCreate fallo %d\n", (int)s); return 10; }

    if (selftest) {
        MIDIPortRef in; MIDIInputPortCreate(g_client, CFSTR("selftest"), selftest_read, NULL, &in);
        MIDIPortConnectSource(in, g_src, NULL);
        puts("selftest: enviando NoteOn/NoteOff/CC por el puerto virtual 'Maschine MK1'");
        midi_send(0x90, 36, 100); midi_send(0x80, 36, 0); midi_send(0xB0, 20, 1); midi_send(0xB0, 20, 127);
        CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.5, false);
        printf("selftest: %s (%d/4 mensajes)\n", g_selftest_got == 4 ? "OK" : "FALLO", g_selftest_got);
        return g_selftest_got == 4 ? 0 : 1;
    }

    int rc = open_mk1();
    if (rc) return rc;
    pthread_t t1, t2;
    pthread_create(&t1, NULL, ep1_reader, NULL);
    pthread_create(&t2, NULL, ep4_reader, NULL);
    ep1_send(0x01, NULL, 0);                 // GET_DEVICE_INFO
    usleep(200000);
    UInt8 am[3] = {1, 10, 10};               // AUTO_MSG: digital, analog, erp
    ep1_send(0x0b, am, 3);
    printf("Puerto MIDI 'Maschine MK1' activo. Ctrl+C para salir.\n");
    fflush(stdout);
    CFRunLoopRun();
    return 0;
}

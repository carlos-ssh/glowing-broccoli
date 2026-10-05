// Fase 1b: abre el MK1 en espacio de usuario, activa alt 1 y vuelca lo que llega por EP1 (0x81) y EP4 (0x84).
// Requiere que el kext de NI no tenga el dispositivo: sudo kextunload -b com.caiaq.driver.NIUSBMaschineControllerDriver
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <CoreFoundation/CoreFoundation.h>
#include <IOKit/IOKitLib.h>
#include <IOKit/IOCFPlugIn.h>
#include <IOKit/usb/IOUSBLib.h>
#include <IOKit/usb/USB.h>

static IOUSBInterfaceInterface300 **itf;
static UInt8 pipe_of[256];   // endpoint address -> pipeRef

static void hexdump(const char *tag, const UInt8 *b, UInt32 n) {
    printf("%s [%u]:", tag, n);
    for (UInt32 i = 0; i < n && i < 64; i++) printf(" %02X", b[i]);
    puts(n > 64 ? " ..." : "");
    fflush(stdout);
}

static void *reader(void *arg) {
    UInt8 ep = (UInt8)(uintptr_t)arg, buf[512], last[512] = {0};
    UInt32 lastn = 0;
    char tag[16]; snprintf(tag, sizeof tag, "EP%02X", ep);
    for (;;) {
        UInt32 n = sizeof buf;
        IOReturn r = (*itf)->ReadPipe(itf, pipe_of[ep], buf, &n);
        if (r) { printf("%s error 0x%08X\n", tag, r); sleep(1); continue; }
        if (ep == 0x84 && n == lastn && !memcmp(buf, last, n)) continue;  // pads: solo cambios
        memcpy(last, buf, n); lastn = n;
        hexdump(tag, buf, n);
    }
    return NULL;
}

static IOReturn send(UInt8 cmd, const UInt8 *args, int len) {
    UInt8 b[64] = {cmd};
    if (len) memcpy(b + 1, args, len);
    return (*itf)->WritePipe(itf, pipe_of[0x01], b, len + 1);
}

int main(void) {
    int vid = 0x17CC, pid = 0x0808;
    CFMutableDictionaryRef m = IOServiceMatching(kIOUSBDeviceClassName);
    CFNumberRef v = CFNumberCreate(NULL, kCFNumberIntType, &vid), p = CFNumberCreate(NULL, kCFNumberIntType, &pid);
    CFDictionarySetValue(m, CFSTR(kUSBVendorID), v);
    CFDictionarySetValue(m, CFSTR(kUSBProductID), p);
    io_service_t dev = IOServiceGetMatchingService(0, m);
    if (!dev) { puts("MK1 no encontrado"); return 1; }
    IOCFPlugInInterface **plug; SInt32 score;
    IOCreatePlugInInterfaceForService(dev, kIOUSBDeviceUserClientTypeID, kIOCFPlugInInterfaceID, &plug, &score);
    IOUSBDeviceInterface320 **d;
    (*plug)->QueryInterface(plug, CFUUIDGetUUIDBytes(kIOUSBDeviceInterfaceID320), (LPVOID *)&d);
    IOReturn r = (*d)->USBDeviceOpenSeize(d);
    if (r) { printf("USBDeviceOpenSeize fallo 0x%08X (el kext de NI sigue reclamando el dispositivo?)\n", r); return 2; }
    (*d)->SetConfiguration(d, 1);

    IOUSBFindInterfaceRequest req = { kIOUSBFindInterfaceDontCare, kIOUSBFindInterfaceDontCare, kIOUSBFindInterfaceDontCare, kIOUSBFindInterfaceDontCare };
    io_iterator_t it; (*d)->CreateInterfaceIterator(d, &req, &it);
    io_service_t is = IOIteratorNext(it);
    if (!is) { puts("sin interfaz"); return 3; }
    IOCreatePlugInInterfaceForService(is, kIOUSBInterfaceUserClientTypeID, kIOCFPlugInInterfaceID, &plug, &score);
    (*plug)->QueryInterface(plug, CFUUIDGetUUIDBytes(kIOUSBInterfaceInterfaceID300), (LPVOID *)&itf);
    r = (*itf)->USBInterfaceOpen(itf);
    if (r) { printf("USBInterfaceOpen fallo 0x%08X\n", r); return 4; }
    r = (*itf)->SetAlternateInterface(itf, 1);
    printf("SetAlternateInterface(1): 0x%08X\n", r);

    UInt8 n; (*itf)->GetNumEndpoints(itf, &n);
    for (UInt8 pr = 1; pr <= n; pr++) {
        UInt8 dir, num, type, intv; UInt16 maxp;
        (*itf)->GetPipeProperties(itf, pr, &dir, &num, &type, &maxp, &intv);
        UInt8 addr = num | (dir == kUSBIn ? 0x80 : 0);
        pipe_of[addr] = pr;
        printf("pipe %u -> endpoint 0x%02X maxPacket=%u\n", pr, addr, maxp);
    }
    pthread_t t1, t2;
    pthread_create(&t1, NULL, reader, (void *)(uintptr_t)0x81);
    pthread_create(&t2, NULL, reader, (void *)(uintptr_t)0x84);

    send(0x01, NULL, 0);                     // GET_DEVICE_INFO
    usleep(200000);
    UInt8 auto_msg[3] = {1, 10, 10};         // digital, analog, erp (intervalos)
    printf("AUTO_MSG: 0x%08X\n", send(0x0b, auto_msg, 3));
    puts("Escuchando 30 s: toca pads, botones y knobs...");
    sleep(30);
    return 0;
}

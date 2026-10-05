// Fase 1: lista descriptores USB del Maschine MK1 (17CC:0808). No abre el dispositivo.
#include <stdio.h>
#include <CoreFoundation/CoreFoundation.h>
#include <IOKit/IOKitLib.h>
#include <IOKit/IOCFPlugIn.h>
#include <IOKit/usb/IOUSBLib.h>
#include <IOKit/usb/USB.h>

int main(void) {
    CFMutableDictionaryRef m = IOServiceMatching(kIOUSBDeviceClassName);
    int vid = 0x17CC, pid = 0x0808;
    CFNumberRef v = CFNumberCreate(NULL, kCFNumberIntType, &vid), p = CFNumberCreate(NULL, kCFNumberIntType, &pid);
    CFDictionarySetValue(m, CFSTR(kUSBVendorID), v);
    CFDictionarySetValue(m, CFSTR(kUSBProductID), p);
    io_service_t dev = IOServiceGetMatchingService(0, m);
    if (!dev) { puts("Maschine MK1 no encontrado"); return 1; }
    IOCFPlugInInterface **plug; SInt32 score;
    if (IOCreatePlugInInterfaceForService(dev, kIOUSBDeviceUserClientTypeID, kIOCFPlugInInterfaceID, &plug, &score)) { puts("no plugin"); return 2; }
    IOUSBDeviceInterface320 **d;
    (*plug)->QueryInterface(plug, CFUUIDGetUUIDBytes(kIOUSBDeviceInterfaceID320), (LPVOID *)&d);
    IOUSBConfigurationDescriptorPtr cfg;
    if ((*d)->GetConfigurationDescriptorPtr(d, 0, &cfg)) { puts("sin descriptor"); return 3; }
    printf("Configuracion: totalLength=%u interfaces=%u value=%u\n", cfg->wTotalLength, cfg->bNumInterfaces, cfg->bConfigurationValue);
    const UInt8 *b = (const UInt8 *)cfg, *end = b + cfg->wTotalLength;
    while (b < end && b[0]) {
        if (b[1] == 4) printf(" Interface %u alt %u: eps=%u class=%u sub=%u proto=%u\n", b[2], b[3], b[4], b[5], b[6], b[7]);
        if (b[1] == 5) printf("   Endpoint 0x%02X attr=0x%02X (%s) maxPacket=%u interval=%u\n", b[2], b[3],
               (b[3]&3)==2?"bulk":(b[3]&3)==3?"interrupt":(b[3]&3)==1?"iso":"ctrl", b[4]|(b[5]<<8), b[6]);
        b += b[0];
    }
    return 0;
}

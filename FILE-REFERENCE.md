# CarrotOS File Reference Guide

| المجلد | الملف | النوع | الوظيفة |
|------|------|------|---------|
| boot/ | bootloader.c | C | Multiboot2 متوافق bootloader |
| boot/ | grub-build.cfg | Config | إعدادات بناء GRUB |
| boot/efi/ | boot.cfg | Config | إعدادات UEFI/BIOS |
| kernel/ | kernel.h | C Header | تعريفات kernel الأساسية |
| kernel/ | main.c | C | نقطة دخول kernel |
| kernel/ | kernel-build.cfg | Config | إعدادات بناء kernel |
| core/init/ | init.h | C Header | تعريفات init system |
| core/init/src/ | main.c | C | عملية init (PID 1) |
| core/ipc/src/ | ipc.h | C Header | آليات IPC |
| core/logging/src/ | logging.h | C Header | نظام الدخول |
| core/session/src/ | session.h | C Header | إدارة الجلسات |
| services/system/ | services.yaml | YAML | تعريفات الخدمات |
| services/system/ | display.service.yaml | YAML | خدمة العرض |
| services/system/ | network.service.yaml | YAML | خدمة الشبكة |
| services/system/ | update.service.yaml | YAML | خدمة التحديثات |
| desktop/compositor/ | compositor.h | C Header | واجهة compositor |
| desktop/shell/src/ | shell.h | C Header | واجهة shell |
| desktop/shell/src/ | main.cpp | C++ | تطبيق shell الرئيسي |
| desktop/shell/ui/ | shell.conf | Config | إعدادات shell |
| apps/files/ | file-manager.h | C Header | مدير الملفات |
| apps/terminal/ | terminal.h | C Header | محاكي الطرفية |
| apps/settings/ | settings.h | C Header | تطبيق الإعدادات |
| apps/software-center/ | software-center.h | C Header | مركز البرامج |
| security/ | security.h | C Header | نظام الأمان |
| security/policies/ | firewall-default.policy | Policy | سياسة جدار الحماية |
| security/policies/apparmor/ | carrot-profiles.aa | AppArmor | ملفات تعريف AppArmor |
| overlays/ | overlay.h | C Header | نظام overlay |
| overlays/src/ | overlay_resolver.py | Python | محلل OverlayFS |
| build/manifests/ | system-manifest.yaml | YAML | بيان النظام الشامل |
| build/manifests/ | overlay-order.yaml | YAML | ترتيب الطبقات |
| build/ | build-manifest.yaml | YAML | بيان البناء |
| tools/scripts/ | build.py | Python | أداة البناء الرئيسية |
| tools/scripts/ | package.py | Python | مدير الحزم |
| tools/scripts/ | overlay_resolver.py | Python | محلل overlay |
| rootfs/base/etc/ | carrot-release | Text | معلومات الإصدار |
| rootfs/base/etc/ | os-release | Text | معلومات نظام التشغيل |

## لغات البرمجة المستخدمة:

### 🔴 C (طبقات منخفضة)
- Bootloader
- Kernel
- Init system
- Core subsystems (IPC, logging, sessions)
- Security modules
- Device drivers

### 🟠 C++ (مكونات الواجهة والتطبيقات الثقيلة)
- Desktop Shell
- Compositor extensions
- GUI applications
- System tools

### 🟡 Python (أدوات البناء والإدارة)
- Build system
- Package manager
- Overlay resolver
- System configuration utilities
- Installation scripts

### 🟢 YAML/Config (الإعدادات والتكوينات)
- Service definitions
- Build manifests
- System manifests
- Overlay configurations
- Security policies

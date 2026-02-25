# 🔥 دليل حرق CarrotOS على فلاشة USB

## المتطلبات:
- فلاشة USB بـ 2GB على الأقل
- ملف ISO: carrotos-1.0-bare-metal.iso
- أداة الحرق: الخيارات أدناه

---

## الطريقة 1: استخدام Rufus (الأسهل على Windows)

### الخطوات:
1. **تحميل Rufus**
   - اذهب إلى: https://rufus.ie/
   - حمل آخر نسخة

2. **فتح Rufus**
   - شغل البرنامج
   - لا تحتاج إلى تثبيت

3. **الإعدادات**
   - أجهزة: اختر فلاشتك (تأكد من البيانات!)
   - نوع الإقلاع: اختر ملف ISO
   - اضغط على أيقونة القرص
   - اختر: carrotos-1.0-bare-metal.iso
   
4. **إعدادات متقدمة**
   ```
   - نظام الملفات: MBR
   - معيار الإقلاع: BIOS or UEFI
   - الخيارات: افتراضية
   ```

5. **الحرق**
   - اضغط "START"
   - انتظر (2-5 دقائق)
   - إذا ظهرت تحذيرات: اضغط نعم

6. **جاهز!**
   - أخرج الفلاشة
   - اختبر على جهاز قديم أولاً

---

## الطريقة 2: استخدام Balena Etcher (الأكثر أماناً)

### الخطوات:
1. **تحميل Etcher**
   - https://www.balena.io/etcher/

2. **التثبيت والتشغيل**
   - تثبيت سريع
   - شغل البرنامج

3. **الحرق (3 خطوات فقط)**
   ```
   Select Image    → اختر ISO
   Select Drive    → فلاشتك
   Flash           → اضغط الزر
   ```

4. **يتم التحقق تلقائياً من الحرق**

---

## الطريقة 3: استخدام Command Line (Linux/macOS/WSL)

```bash
# 1. البحث عن الفلاشة
lsblk  # أو diskutil list

# 2. فصل الفلاشة (إن كانت مثبتة)
sudo umount /dev/sdX*

# 3. الحرق
sudo dd if=carrotos-1.0-bare-metal.iso of=/dev/sdX bs=4M
sudo sync

# 4. نجاح ✅
```

**تحذير:** عوض `sdX` بحرف صحيح (مثل sdb، sdc)

---

## الطريقة 4: Windows PowerShell (متقدم)

```powershell
# 1. أحذر: حدد الفلاشة بدقة
Get-Disk

# 2. الحرق (مع Admin)
$iso = "carrotos-1.0-bare-metal.iso"
$drive = @(Get-Disk | Where bustype -eq usb)[0]

dd if=$iso of=\\?\PhysicalDrive{number} bs=4MB --progress
```

---

## اختبار الإقلاع

### على جهاز حقيقي:
1. **فجر الفلاشة في USB port**
2. **أعد تشغيل الجهاز**
3. **اضغط مفتاح الإقلاع (Boot Key)**
   - Dell: F12
   - HP: ESC أو F9
   - Lenovo: F12
   - ASUS: DEL أو F2
   - Acer: F12
   - Asus: F2
4. **اختر الفلاشة من القائمة**
5. **انتظر تحميل بواسطة GRUB**

### النتيجة المتوقعة:
```
     GNU GRUB  version 2.04

 ┌────────────────────────────────────────────┐
 │  CarrotOS 1.0 - Bare Metal               │
 │  CarrotOS 1.0 - Safe Mode                │
 │  Boot from Hard Drive                    │
 │  GRUB Command Line                       │
 └────────────────────────────────────────────┘

      Use the ↑ and ↓ keys to select.
      Press Enter to boot the selected OS.
      Press 'e' to edit the selected item,
      or 'c' for a command-line prompt.
```

---

## استكشاف الأخطاء

### المشكلة: "لا يقلع من الفلاشة"
**الحل:**
- تأكد من BIOS أن USB-Boot مفعل
- جرب Rufus بإعدادات مختلفة
- قد تحتاج فلاشة قديمة الطراز

### المشكلة: "Grub بدون قرص صلب"
**الحل:**
- هذا طبيعي في الوهم الأول
- اضغط Enter للمتابعة
- النظام سيحاول التمهيد

### المشكلة: "شاشة سوداء"
**الحل:**
- قد يكون بطيء التحميل (انتظر 10 ثواني)
- اضغط أي مفتاح
- جرب Safe Mode

---

## للمتقدمين: تعديل GRUB

1. **عند شاشة GRUB:**
   - اضغط `c` للدخول إلى command line
   - `ls` لترى الأقراص المتاحة
   - `set root=(hd0,msdos1)`
   - `boot`

2. **للإقلاع من القرص الصلب:**
   - اختر "Boot from Hard Drive"
   - أو في الكمبيوتر بدء جديد GRUB

---

## الخطوة التالية بعد الإقلاع

عند دخولك إلى CarrotOS:
1. تسجيل دخول (root/carrot)
2. تشغيل اللغة العربية: `carrot-setup locale ar_SA`
3. تثبيت التطبيقات: `carrot-installer`
4. متمتع! 🎉

---

## معايير الأداء المتوقعة

| المعيار | الأداء |
|--------|---------|
| وقت الإقلاع | 15-30 ثانية |
| استهلاك الذاكرة | 256-512 MB |
| دعم الـ USB | ✅ كامل |
| الرسوميات | ✅ VESA |
| الشبكة | ✅ متوفرة |

---

## نصائح إضافية

### لـ Virtualization:
```bash
# VirtualBox
VBoxManage createvm --name CarrotOS_VM --ostype Linux --register
# اختر ISO في الإعدادات

# QEMU
qemu-system-x86_64 -cdrom carrotos-1.0-bare-metal.iso -m 2G
```

### لـ Production:
- استخدم dvd أيضاً (أكثر موثوقية)
- احتفظ بـ USB في مكان آمن
- انسخ الـ ISO على عدة أجهزة

---

**ملاحظة:** تم بناء CarrotOS 1.0 بكامل قوة:
- Bootloader محسّن (Multiboot2)
- Kernel متقدم مع دعم وحدات
- 7 تطبيقات متكاملة
- نظام تثبيت تفاعلي
- دعم BIOS و UEFI

**استمتع باستخدام CarrotOS على معداتك الحقيقية! 🚀**

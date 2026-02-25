#!/bin/bash
# CarrotOS Bare Metal - USB Burning Script
# استخدام على Linux و macOS

ISO_FILE="carrotos-1.0-bare-metal.iso"
DEVICE=""

echo "╔═══════════════════════════════════════════╗"
echo "║  CarrotOS 1.0 - Bare Metal USB Burner    ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# التحقق من الملف
if [ ! -f "$ISO_FILE" ]; then
    echo "❌ ملف ISO غير موجود: $ISO_FILE"
    exit 1
fi

echo "✓ ملف ISO: $ISO_FILE"
echo ""

# البحث عن الأقراص
echo "🔍 الأقراص المتاحة (USB):"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    diskutil list external physical
    echo ""
    DEVICE=$(read -p "اختر الجهاز (مثل disk2): " && echo "${REPLY//[^0-9]/}")
    DEVICE="/dev/disk$DEVICE"
else
    # Linux
    lsblk
    echo ""
    read -p "اختر الجهاز (مثل /dev/sdb): " DEVICE
fi

# التحقق من الجهاز
if [ ! -b "$DEVICE" ]; then
    echo "❌ جهاز غير صالح: $DEVICE"
    exit 1
fi

# التحذير
echo ""
echo "⚠️  تحذير: سيتم حذف جميع البيانات على $DEVICE!"
read -p "هل أنت متأكد؟ (نعم/لا): " confirm

if [ "$confirm" != "نعم" ] && [ "$confirm" != "yes" ]; then
    echo "تم الإلغاء"
    exit 0
fi

# الحرق
echo ""
echo "💾 جاري الحرق..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    diskutil unmountDisk "$DEVICE"
    sudo dd if="$ISO_FILE" of="${DEVICE}r0" bs=4m
    diskutil eject "$DEVICE"
else
    # Linux
    sudo umount "${DEVICE}"*
    sudo dd if="$ISO_FILE" of="$DEVICE" bs=4M status=progress
    sudo sync
fi

echo ""
echo "✅ اكتمل! الفلاشة جاهزة للإقلاع"

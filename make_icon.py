from PIL import Image

# نام عکس خود را بررسی کنید (اگر png یا jpg است اینجا بنویسید)
input_image = "icon.png"  

try:
    img = Image.open(input_image)
    # تبدیل عکس به فایل آیکون با ابعاد مختلف برای ویندوز
    img.save("icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("✅ فایل icon.ico با موفقیت ساخته شد!")
except Exception as e:
    print("❌ خطا:", e)
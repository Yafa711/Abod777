import os
import requests
from tiktok_uploader.upload import upload_video

# 1. التحميل المباشر للفيديو
with open("video_url.txt", "r") as f:
    video_url = f.read().strip()

print(f"[+] جاري التحميل من: {video_url}")
response = requests.get(video_url, stream=True)

if response.status_code == 200:
    with open("downloaded_video.mp4", "wb") as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    print("[+] تم تحميل الفيديو بنجاح إلى السيرفر!")
else:
    print(f"[-] فشل التحميل، كود الخطأ: {response.status_code}")
    exit(1)

# 2. الرفع إلى تيك توك باستخدام الإعدادات السحابية
print("[+] جاري الرفع إلى تيك توك (وضع الخلفية)...")

try:
    upload_video(
        filename='downloaded_video.mp4',
        description='محتوى رائع من قناتي! #ترند',
        cookies='cookies.txt',
        browser='chrome',
        headless=True,  # ضروري لتشغيل البوت بدون شاشة في جيثب
        browser_args=['--no-sandbox', '--disable-dev-shm-usage'] # ضروري لتجنب مشاكل المتصفح
    )
    print("[+] تم الرفع بنجاح على تيك توك!")
except Exception as e:
    print(f"[-] حدث خطأ أثناء الرفع: {e}")
    exit(1)

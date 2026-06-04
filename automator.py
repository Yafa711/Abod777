import os
import requests
from tiktok_uploader.upload import upload_video

# 1. تحميل الفيديو
with open("video_url.txt", "r") as f:
    video_url = f.read().strip()

print(f"[+] جاري التحميل من: {video_url}")
response = requests.get(video_url, stream=True)

if response.status_code == 200:
    with open("downloaded_video.mp4", "wb") as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk: f.write(chunk)
    print("[+] تم التحميل بنجاح!")
else:
    print(f"[-] فشل التحميل، كود الخطأ: {response.status_code}")
    exit(1)

# 2. رفع الفيديو مع تمويه كامل
print("[+] جاري الرفع إلى تيك توك...")
try:
    upload_video(
        filename='downloaded_video.mp4',
        description='محتوى رائع! #ترند #TikTok',
        cookies='cookies.txt',
        browser='chrome',
        headless=True,
        browser_args=[
            '--no-sandbox', 
            '--disable-dev-shm-usage',
            '--window-size=1920,1080',
            '--disable-blink-features=AutomationControlled',
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
    )
    print("[+] تم إرسال أمر الرفع بنجاح!")
except Exception as e:
    print(f"[-] فشل الرفع (قد يكون الحظر مستمراً): {e}")
 


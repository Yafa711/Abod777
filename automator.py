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

# بديل لجزء الرفع والنشر
try:
    print("[+] بانتظار اختفاء نوافذ تيك توك...")
    # إجبار البوت على الانتظار 20 ثانية إضافية قبل محاولة الضغط على النشر
    import time
    time.sleep(20) 
    
    print("[+] جاري الضغط على زر النشر...")
    # استمر في عملية الرفع كما هي
    upload_video(...) 
    
except Exception as e:
    print(f"[-] حدث خطأ في التوقيت: {e}")

 


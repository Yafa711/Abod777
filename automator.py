import os
import requests

# قراءة الرابط من الملف
with open("video_url.txt", "r") as f:
    video_url = f.read().strip()

print(f"[+] جاري تحميل الفيديو مباشرة من الرابط: {video_url}")

# التحميل المباشر للملف وتسميته downloaded_video.mp4 ليتوافق مع بقية السكريبت
response = requests.get(video_url, stream=True)
if response.status_code == 200:
    with open("downloaded_video.mp4", "wb") as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    print("[+] تم تحميل الفيديو بنجاح من الملاذ المباشر!")
else:
    print(f"[-] فشل التحميل، كود الخطأ: {response.status_code}")

import os
import requests
from tiktok_uploader.upload import upload_video

# 1. التحميل
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
    print(f"[-] فشل التحميل: {response.status_code}")
    exit(1)

# 2. الرفع (تأكد من وضع معلومات حسابك في Secrets في جيثب)
print("[+] جاري الرفع إلى تيك توك...")
upload_video(
    filename='downloaded_video.mp4',
    description='محتوى رائع من قناتي! #ترند #فيديو',
    cookies='cookies.txt' # تأكد أن ملف الكوكيز موجود في مستودعك
)
print("[+] تم الرفع بنجاح!")

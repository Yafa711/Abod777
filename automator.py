import time
from tiktok_uploader.upload import upload_video

# 1. الرفع المباشر
print("[+] جاري الرفع إلى تيك توك...")
try:
    # نقوم بعملية الرفع مباشرة، وبدون تعديلات معقدة قد تفسد الجلسة
    upload_video(
        filename='downloaded_video.mp4',
        description='محتوى رائع! #ترند #TikTok',
        cookies='cookies.txt', # تأكد أن الملف موجود في نفس المجلد
        browser='chrome',
        headless=True,
        browser_args=['--no-sandbox', '--disable-dev-shm-usage']
    )
    print("[+] تم الانتهاء من عملية الرفع!")
except Exception as e:
    print(f"[-] فشل الرفع: {e}")

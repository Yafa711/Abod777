import os
import math
import time
import requests
from moviepy import VideoFileClip

STATE_FILE = "state.txt"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            lines = f.read().splitlines()
            if len(lines) >= 2:
                return lines[0].strip(), int(lines[1].strip())
    
    if os.path.exists("video_url.txt"):
        with open("video_url.txt", "r") as f:
            url = f.read().strip()
            return url, 1
    return None, 1

def save_state(url, next_part):
    with open(STATE_FILE, "w") as f:
        f.write(f"{url}\n{next_part}")
    print(f"[+] تم تحديث الحالة: الجزء القادم هو {next_part}")

def download_youtube_video(url, output_path="downloaded_video.mp4"):
    print("[+] جاري سحب الفيديو عبر البوابة البديلة لتخطي تشفير يوتيوب نهائياً...")
    
    # استخراج الـ Video ID من الرابط
    video_id = ""
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    elif "v=" in url:
        video_id = url.split("v=")[1].split("&")[0]
        
    if not video_id:
        raise Exception("لم يتم التعرف على معرف الفيديو بالشكل الصحيح")

    # استخدام خوادم انـفـيـديـوس المفتوحة والوسيطة لسحب رابط التحميل المباشر بدون قيود n-challenge
    instances = [
        "https://invidious.nerdvpn.de",
        "https://yewtu.be",
        "https://invidious.flokinet.to",
        "https://iv.melmac.space"
    ]
    
    download_url = None
    for instance in instances:
        try:
            print(f"[⏳] محاولة الاتصال بالبوابة الآمنة: {instance}")
            api_url = f"{instance}/api/v1/videos/{video_id}"
            response = requests.get(api_url, timeout=15).json()
            
            # البحث عن صيغة فيديو mp4 مناسبة تحتوي على الصوت والصورة معاً
            for fmt in response.get("formatStreams", []):
                if "mp4" in fmt.get("container", "") and fmt.get("qualityLabel"):
                    download_url = fmt["url"]
                    break
            if download_url:
                break
        except Exception:
            continue

    if not download_url:
        print("[-] فشل السحب عبر البوابات السريعة، جاري استخدام محرك التحميل الاحتياطي المباشر...")
        # محرك احتياطي مباشر في حال توقفت المنصات الوسيطة
        download_url = f"https://co.wuk.sh/api/json"
        try:
            res = requests.post(download_url, json={"url": url, "vQuality": "720"}, headers={"Accept": "application/json"}).json()
            if res.get("url"):
                download_url = res["url"]
        except Exception as e:
            raise Exception(f"جميع محركات التخطي فشلت في الوصول للملف: {e}")

    # تحميل الملف الفعلي إلى السيرفر
    print("[+] تم العثور على المسار الآمن المباشر، جاري سحب ملف الفيديو الفعلي...")
    res = requests.get(download_url, stream=True)
    with open(output_path, "wb") as f:
        for chunk in res.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
                
    print("[🎉] اكتمل تحميل الفيديو بنجاح تام وبدون حظر!")
    return output_path

if __name__ == "__main__":
    url, current_part = load_state()
    
    if not url or ("youtube" not in url and "youtu.be" not in url):
        print(f"[-] لا يوجد رابط فيديو صالح في الملفات. الرابط الموجود: {url}")
        exit(0)
        
    try:
        video_file = download_youtube_video(url)
    except Exception as e:
        print(f"[-] خطأ حرج أثناء التحميل: {e}")
        exit(1)
    
    with VideoFileClip(video_file) as clip_for_meta:
        total_duration = clip_for_meta.duration
    
    segment_length = 60
    total_parts = math.ceil(total_duration / segment_length)
    print(f"[+] الفيديو يحتوي على {total_parts} أجزاء إجمالاً. نحن الآن في الجزء {current_part}.")
    
    if current_part > total_parts:
        print("[🎉] تم نشر هذا الفيديو بالكامل!")
        exit(0)
        
    parts_to_publish = list(range(current_part, min(current_part + 3, total_parts + 1)))
    print(f"[🚀] الأجزاء المستهدفة للنشر اليوم: {parts_to_publish}")
    uploaded_count = 0
    
    for part_num in parts_to_publish:
        start_time = (part_num - 1) * segment_length
        end_time = min(part_num * segment_length, total_duration)
        
        print(f"[-] جاري قص الجزء {part_num}...")
        part_filename = f"temp_part_{part_num}.mp4"
        
        with VideoFileClip(video_file) as main_clip:
            subclip = main_clip.subclipped(start_time, end_time)
            subclip.write_videofile(part_filename, codec="libx264", audio_codec="aac")
        
        caption = f"قصص وخواطر مؤثرة 📖✨ | الجزء {part_num} #خواطر #قصص #fyp"
        
        try:
            print(f"[+] جاري رفع الجزء {part_num} إلى تيك توك...")
            from tiktok_uploader.upload import upload_video
            upload_video(part_filename, description=caption, cookies='cookies.txt')
            print(f"[+] تم رفع الجزء {part_num} بنجاح.")
            uploaded_count += 1
            if os.path.exists(part_filename):
                os.remove(part_filename)
            if part_num != parts_to_publish[-1]:
                print("[⏳] انتظار 10 دقائق قبل رفع الجزء التالي لحماية الحساب...")
                time.sleep(600)
        except Exception as e:
            print(f"[-] فشل رفع الجزء {part_num}: {e}")
            break
            
    next_part_to_run = current_part + uploaded_count
    save_state(url, next_part_to_run)
    
    if os.path.exists(video_file):
        os.remove(video_file)

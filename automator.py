import os
import math
import time
from yt_dlp import YoutubeDL
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
    print("[+] جاري تحميل فيديو قصص الخواطر عبر عميل التلفزيون الذكي المضمون لتخطي الحظر...")
    ydl_opts = {
        # طلب أفضل جودة فيديو وصوت مدمجة مباشرة لتفادي مشاكل الدمج والتشفير
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_path,
        'cookiefile': 'youtube_cookies.txt',
        # استخدام عملاء التلفزيون الذكي (tv, tv_embedded) لأنهم لا يعتمدون على تشفير n-challenge الصارم
        'extractor_args': {
            'youtube': {
                'player_client': ['tv', 'tv_embedded'],
            }
        },
        'quiet': False
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

if __name__ == "__main__":
    url, current_part = load_state()
    
    if not url or ("youtube" not in url and "youtu.be" not in url):
        print(f"[-] لا يوجد رابط فيديو صالح في الملفات. الرابط الموجود: {url}")
        exit(0)
        
    video_file = download_youtube_video(url)
    
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
    if os.path.exists('youtube_cookies.txt'):
        os.remove('youtube_cookies.txt')

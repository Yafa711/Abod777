import os
import math
import time
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip
from tiktok_uploader.upload import upload_video

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
    print("[+] جاري تحميل فيديو قصص الخواطر من يوتيوب...")
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

def split_video(video_path, segment_length=60):
    print("[+] جاري معالجة وتقطيع الفيديو بالكامل...")
    clip = VideoFileClip(video_path)
    duration = clip.duration
    num_segments = math.ceil(duration / segment_length)
    output_files = []
    for i in range(num_segments):
        output_files.append((i + 1, i * segment_length, min((i + 1) * segment_length, duration)))
    clip.close()
    return output_files, duration

if __name__ == "__main__":
    url, current_part = load_state()
    if not url or "youtube" not in url:
        print("[-] لا يوجد رابط فيديو صالح في الملفات.")
        exit(0)
        
    video_file = download_youtube_video(url)
    clip_for_meta = VideoFileClip(video_file)
    total_duration = clip_for_meta.duration
    clip_for_meta.close()
    
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
        main_clip = VideoFileClip(video_file)
        subclip = main_clip.subclip(start_time, end_time)
        part_filename = f"temp_part_{part_num}.mp4"
        subclip.write_videofile(part_filename, codec="libx264", audio_codec="aac")
        main_clip.close()
        
        caption = f"قصص وخواطر مؤثرة 📖✨ | الجزء {part_num} #خواطر #قصص #foryou #fyp"
        
        try:
            print(f"[+] جاري رفع الجزء {part_num} إلى تيك توك...")
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

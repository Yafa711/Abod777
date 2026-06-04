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
    print("[+] جاري استخراج رابط التحميل المباشر عبر بوابة Y2Mate الفعالة...")
    
    headers = {
        'authority': 'www.y2mate.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.y2mate.com',
        'referer': 'https://www.y2mate.com/en858/download-youtube',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    # الخطوة 1: تحليل الرابط والحصول على التوكن والمعرفات
    data_analyze = {
        'k_query': url,
        'k_page': 'Youtube Downloader',
        'hl': 'en',
        'q_auto': '0',
    }
    
    try:
        response = requests.post('https://www.y2mate.com/mates/en858/analyzeV2/ajax', headers=headers, data=data_analyze).json()
        if response.get('status') != 'ok':
            raise Exception("الموقع الوسيط لم يتمكن من تحليل الرابط")
            
        vid = response["vid"]
        video_links = response.get('links', {}).get('mp4', {})
        
        # البحث عن أفضل جودة متاحة (يفضل 720p أو 480p لسرعة المعالجة)
        target_k = None
        for k_id, info in video_links.items():
            quality = info.get('q', '')
            if quality in ['720p', '480p', '360p']:
                target_k = info.get('k')
                print(f"[+] تم اختيار جودة الفيديو المناسبة: {quality}")
                break
                
        # إذا لم يجد الجودات المفضلة، نأخذ أول خيار متاح
        if not target_k and video_links:
            first_key = list(video_links.keys())[0]
            target_k = video_links[first_key].get('k')
            print(f"[+] تم اختيار جودة الفيديو التلقائية المتاحة: {video_links[first_key].get('q')}")

        if not target_k:
            raise Exception("لم يتم العثور على صيغ تحميل صالحة")

        # الخطوة 2: تحويل الطلب واستخراج الرابط المباشر النظيف (dlink)
        data_convert = {
            'vid': vid,
            'k': target_k,
        }
        
        convert_res = requests.post('https://www.y2mate.com/mates/convertV2/index', headers=headers, data=data_convert).json()
        download_url = convert_res.get("dlink")
        
        if not download_url:
            raise Exception("فشل استخراج رابط التحميل النهائي dlink")
            
        print("[+] تم الحصول على الرابط المباشر، جاري سحب ملف الفيديو الفعلي الآن...")
        
        # الخطوة 3: تحميل الفيديو مباشرة إلى السيرفر
        video_req = requests.get(download_url, stream=True, timeout=30)
        with open(output_path, "wb") as f:
            for chunk in video_req.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        print("[🎉] اكتمل تحميل الفيديو بالكامل وبنجاح تام عبر الثغرة البديلة!")
        return output_path

    except Exception as e:
        raise Exception(f"فشلت عملية السحب البرمجية عبر Y2Mate: {e}")

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

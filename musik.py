import yt_dlp
import os
import re
import subprocess
import threading
import logging

# Setup logging
logging.basicConfig(filename='download_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '', name)

def generate_unique_filename(folder, title, extension, quality_or_resolution):
    sanitized_title = sanitize_filename(title)
    filename = f"{sanitized_title} [{quality_or_resolution}].{extension}"
    filepath = os.path.join(folder, filename)
    
    counter = 1
    while os.path.exists(filepath):
        filepath = os.path.join(folder, f"{sanitized_title} [{quality_or_resolution}] ({counter}).{extension}")
        counter += 1
    return filepath

def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"\r📥 Downloading: {d['_percent_str']} - {d['_eta_str']} ETA", end='', flush=True)
    elif d['status'] == 'finished':
        print("\n✅ Download selesai!")

def validate_url(url):
    return re.match(r'https?://(?:www\.)?(?:youtube\.com|youtu\.be)/.+', url)

def download_media(url, output_folder, quality, video_resolution, mode):
    if not validate_url(url):
        print(f"❌ URL {url} tidak valid!")
        return
    
    quality_map = {"1": "128k", "2": "192k", "3": "256k", "4": "320k"}
    video_resolutions = {"1": "1080", "2": "1440", "3": "2160", "4": "4320"}

    ydl_opts = {
        'outtmpl': generate_unique_filename(output_folder, '%(title)s', 'mp3' if mode == 'audio' else 'mp4', quality_map.get(quality, "128k") if mode == 'audio' else video_resolutions.get(video_resolution, "1080")),
        'progress_hooks': [progress_hook],
        'continuedl': True,
        'noplaylist': True
    }
    
    if mode == "audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality_map.get(quality, "128k")
            }]
        })
    else:
        ydl_opts.update({
            'format': f'bestvideo[ext=mp4][height<={video_resolutions.get(video_resolution, "1080")}] + bestaudio/best',
            'merge_output_format': 'mp4'
        })
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            logging.info(f"Download berhasil: {url}")
        
        subprocess.run(["termux-media-scan", output_folder])
    except yt_dlp.utils.DownloadError as e:
        logging.error(f"Error: {e}")
        print(f"❌ Error: {e}")

def handle_download(urls, output_folder, quality, video_resolution, mode):
    for url in urls:
        print(f"\n📥 Mulai mendownload {url}...")
        download_media(url, output_folder, quality, video_resolution, mode)
        print(f"✅ Download untuk {url} selesai!")

def get_input(prompt, choices):
    while True:
        choice = input(prompt).strip()
        if choice in choices:
            return choice
        print("❌ Pilihan tidak valid!")

def main():
    print("==========================================")
    print("          🔥 BIMA PROJECT 🔥")
    print("         Owner: @bima.gunawan")
    print("==========================================")
    
    while True:
        mode = get_input("\n✨ Pilih Mode Download:\n1. Download Audio MP3\n2. Download Video MP4\nMasukkan pilihan: ", {"1", "2"})
        mode = "audio" if mode == "1" else "video"
        output_folder = "/storage/emulated/0/Music/" if mode == "audio" else "/storage/emulated/0/Movies/"
        os.makedirs(output_folder, exist_ok=True)

        urls = input("\n🎵 Masukkan URL YouTube (pisahkan dengan koma jika lebih dari satu): ").split(',')
        urls = [url.strip() for url in urls if validate_url(url.strip())]
        
        if not urls:
            print("❌ Tidak ada URL yang valid. Coba lagi.")
            continue
        
        quality = get_input("\n✨ Pilih kualitas audio:\n1. 128kbps (Normal)\n2. 192kbps (High)\n3. 256kbps (High Quality)\n4. 320kbps (Maximal)\nMasukkan pilihan: ", {"1", "2", "3", "4"}) if mode == "audio" else None
        video_resolution = get_input("\n✨ Pilih resolusi video:\n1. 1080p (Full HD)\n2. 1440p (Quad HD)\n3. 2160p (4K Ultra HD)\n4. 4320p (8K Ultra HD)\nMasukkan pilihan: ", {"1", "2", "3", "4"}) if mode == "video" else None
        
        download_thread = threading.Thread(target=handle_download, args=(urls, output_folder, quality, video_resolution, mode))
        download_thread.start()
        download_thread.join()

if __name__ == "__main__":
    main()

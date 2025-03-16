import yt_dlp
import os
import re
import threading
import logging

def color_text(text, color):
    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "whatsapp_green": "\033[38;5;46m",  # Hijau khas WhatsApp
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "telegram_blue": "\033[38;5;33m",  # Biru khas Telegram
        "magenta": "\033[35m",
        "orange": "\033[38;5;214m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m"  # Untuk mengembalikan warna ke default
    }
    return f"{colors[color]}{text}{colors['reset']}"

def display_title():
    print(color_text("==========================================", "cyan"))
    print(color_text("          🔥 BIMA PROJECT 🔥          ", "yellow"))
    print(color_text("         Owner: @bima.gunawan         ", "magenta"))
    print(color_text("==========================================", "cyan"))

# Setup logging untuk mencatat aktivitas download
logging.basicConfig(filename='download_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def sanitize_filename(name):
    """Menghapus karakter yang nggak bisa dipakai di nama file"""
    return re.sub(r'[\\/*?:"<>|]', '', name)

def generate_unique_filename(folder, title, extension, quality_or_resolution):
    """Menghasilkan nama file unik jika file sudah ada dan memasukkan kualitas atau resolusi ke dalam nama file"""
    sanitized_title = sanitize_filename(title)
    filename = f"{sanitized_title} [{quality_or_resolution}].{extension}"
    filepath = os.path.join(folder, filename)

    # Jika file sudah ada, tambahkan angka di belakang nama file untuk membuatnya unik
    counter = 1
    while os.path.exists(filepath):
        filepath = os.path.join(folder, f"{sanitized_title} [{quality_or_resolution}] ({counter}).{extension}")
        counter += 1
    return filepath

def progress_hook(d):
    """Menampilkan status progress download"""
    if d['status'] == 'downloading':
        print(f"\r📥 Downloading: {d['_percent_str']} - {d['_eta_str']} ETA", end='', flush=True)
    elif d['status'] == 'finished':
        print("\n✅ Download selesai!")

def validate_url(url):
    """Memvalidasi URL untuk memastikan formatnya benar"""
    pattern = re.compile(r'https?://(?:www\.)?(?:youtube\.com|youtu\.be)/.+')
    return pattern.match(url)

def download_audio_or_video(url, output_folder, quality, video_resolution, mode):
    """Download audio MP3 atau video berdasarkan pilihan mode dan resolusi"""
    if not validate_url(url):
        print(f"❌ URL {url} tidak valid! Format yang benar: https://www.youtube.com/...") 
        return
    
    quality_map = {
        "1": "bestaudio",  # Normal
        "2": "bestaudio",  # High
        "3": "bestaudio",  # High Quality
        "4": "bestaudio",  # Maximal
    }

    video_resolutions = {
        "1": "1080p",  # 1080p
        "2": "1440p",  # 1440p
        "3": "2160p",  # 4K
        "4": "4320p",  # 8K
    }

    # Pilihan format audio atau video
    if mode == "audio":
        ydl_opts = {
            'format': quality_map.get(quality, "bestaudio"),
            'outtmpl': generate_unique_filename(output_folder, '%(title)s', 'mp3', quality_map.get(quality, "bestaudio")),  # Untuk audio
            'progress_hooks': [progress_hook],
            'continuedl': True,  # Resume download jika gagal
            'writethumbnail': False,  # Matikan download thumbnail untuk audio
            'noplaylist': True,  # Jika URL adalah playlist, hanya download 1 video
        }
    elif mode == "video":
        resolution = video_resolutions.get(video_resolution, "1080p")
        ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best',  # Pilih video dan audio terbaik sesuai resolusi
            'outtmpl': generate_unique_filename(output_folder, '%(title)s', 'mp4', resolution),  # Untuk video
            'progress_hooks': [progress_hook],
            'continuedl': True,  # Resume download jika gagal
            'writethumbnail': True,  # Download thumbnail untuk video
            'noplaylist': True,  # Jika URL adalah playlist, hanya download 1 video
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            logging.info(f"Download berhasil: {url}")
    except yt_dlp.utils.DownloadError as e:
        logging.error(f"Error: {e}. Coba format lain untuk {url}.")
        print(f"❌ Error: {e}. Coba format lain...")

def handle_download(urls, output_folder, quality, video_resolution, mode):
    """Fungsi untuk mendownload semua URL secara bersamaan"""
    for url in urls:
        print(f"\n📥 Mulai mendownload {url}...")
        download_audio_or_video(url, output_folder, quality, video_resolution, mode)
        print(f"✅ Download untuk {url} selesai!")

def get_valid_urls():
    """Memastikan URL yang dimasukkan valid"""
    while True:
        urls_input = input("\n🎵 Masukkan URL YouTube (pisahkan dengan koma jika lebih dari satu): ")
        urls = [url.strip() for url in urls_input.split(',')]
        valid_urls = [url for url in urls if validate_url(url)]
        
        if len(valid_urls) == 0:
            print("❌ Semua URL yang dimasukkan tidak valid. Coba lagi.")
        else:
            return valid_urls

def get_valid_quality():
    """Memastikan pilihan kualitas audio valid"""
    while True:
        print("\n✨ Pilih kualitas audio yang diinginkan: ✨")
        print("1. Normal 🎵 (Kualitas standar) - 128kbps")
        print("2. High 🎶 (Kualitas lebih baik) - 192kbps")
        print("3. High Quality 🎧 (Kualitas tinggi) - 256kbps")
        print("4. Maximal 🔊 (Kualitas terbaik) - 320kbps")

        quality = input("\nMasukkan nomor pilihan kualitas audio: ")

        if quality in ["1", "2", "3", "4"]:
            return quality
        else:
            print("❌ Pilihan tidak valid. Pilih antara 1 dan 4.")

def get_valid_resolution():
    """Memastikan pilihan resolusi video valid"""
    while True:
        print("\n✨ Pilih resolusi video yang diinginkan: ✨")
        print("1. 1080p (Full HD)")
        print("2. 1440p (Quad HD)")
        print("3. 2160p (4K Ultra HD)")
        print("4. 4320p (8K Ultra HD)")

        resolution = input("\nMasukkan nomor pilihan resolusi video: ")

        if resolution in ["1", "2", "3", "4"]:
            return resolution
        else:
            print("❌ Pilihan tidak valid. Pilih antara 1 dan 4.")

def get_mode_choice():
    """Memastikan pilihan mode download valid"""
    while True:
        print("\n✨ Pilih Mode Download: ✨")
        print("1. Download Audio MP3")
        print("2. Download Video MP4")
        mode = input("\nMasukkan pilihan (1/2): ")

        if mode == "1":
            return "audio"
        elif mode == "2":
            return "video"
        else:
            print("❌ Pilihan tidak valid. Pilih antara 1 dan 2.")

def main():
    display_title()  # Tampilkan judul program sebelum memulai

    while True:
        # Mendapatkan mode (audio atau video)
        mode = get_mode_choice()

        # Mendapatkan URL yang valid
        urls = get_valid_urls()

        output_folder = input("\n📂 Masukkan folder penyimpanan (default: downloads): ").strip() or "downloads"
        os.makedirs(output_folder, exist_ok=True)

        # Mendapatkan kualitas audio jika mode audio dipilih
        if mode == "audio":
            quality = get_valid_quality()
            # Menggunakan multithreading untuk download beberapa URL sekaligus
            download_thread = threading.Thread(target=handle_download, args=(urls, output_folder, quality, None, mode))
        else:
            # Mendapatkan resolusi jika mode video dipilih
            video_resolution = get_valid_resolution()
            download_thread = threading.Thread(target=handle_download, args=(urls, output_folder, None, video_resolution, mode))

        download_thread.start()
        download_thread.join()

if __name__ == "__main__":
    main()

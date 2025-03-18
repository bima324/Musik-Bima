import os
import yt_dlp
import mutagen.mp3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
from tqdm import tqdm
import requests

def download_thumbnail(video_id, output_path):
    url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        thumb_path = os.path.join(output_path, f"{video_id}.jpg")
        with open(thumb_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return thumb_path
    return None

def edit_metadata(file_path, title, artist, album, thumbnail_path):
    try:
        audio = mutagen.mp3.MP3(file_path, ID3=ID3)
        audio.tags = ID3()
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        audio.tags.add(TALB(encoding=3, text=album))
        
        if thumbnail_path:
            with open(thumbnail_path, 'rb') as img:
                audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=img.read()))
        
        audio.save()
        print(f"✅ Metadata updated: {title} - {artist} ({album}) 🎵")
    except Exception as e:
        print(f"⚠️ Failed to update metadata: {e}")

def download_audio(urls, output_path, quality, format_choice):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    for url in tqdm(urls, desc="🎵 Downloading & Converting", unit="file"):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format_choice,
                    'preferredquality': quality,
                }
            ],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown')
                artist = info.get('uploader', 'Unknown')
                album = "YouTube Download"
                video_id = info.get('id', 'Unknown')
                
                file_ext = format_choice if format_choice != "mp3" else "mp3"
                audio_file = f"{output_path}/{title}.{file_ext}"
                
                thumbnail_path = download_thumbnail(video_id, output_path)
                edit_metadata(audio_file, title, artist, album, thumbnail_path)
        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")
    
    print("✨ All downloads & conversions are complete! 🎶")

if __name__ == "__main__":
    print("🚀 Welcome to BimaGunawan YT-MP3 Downloader! 🎧")
    print("🔥 Developed by: Bima Gunawan 🔥")
    print("💡 Download high-quality audio from YouTube with metadata & cover art! 💡")
    
    output_path = input("📂 Enter output folder (press enter for default 'downloads'): ") or "downloads"
    
    print("\n🔹 Select audio format:")
    print("1. MP3 🎧")
    print("2. AAC 🎵")
    print("3. FLAC 🎼")
    print("4. WAV 🎶")
    format_map = {"1": "mp3", "2": "aac", "3": "flac", "4": "wav"}
    format_choice = format_map.get(input("Enter choice (1-4): "), "mp3")
    
    print("\n🔹 Select audio quality:")
    print("1. Low (64kbps) 🎵")
    print("2. Medium (128kbps) 🎶")
    print("3. High (192kbps) 🎼")
    print("4. Highest (320kbps) 🎧")
    
    quality_map = {"1": "64", "2": "128", "3": "192", "4": "320"}
    quality_choice = quality_map.get(input("Enter choice (1-4): "), "192")
    
    print("\n🎵 Enter YouTube URLs:")
    print("- You can enter a single URL or multiple URLs separated by commas.")
    print("- Example: https://youtu.be/abc123, https://youtu.be/xyz789")
    video_urls = input().split(",")
    video_urls = [url.strip() for url in video_urls if url.strip()]
    
    if not video_urls:
        print("⚠️ No valid URLs provided. Exiting...")
    else:
        download_audio(video_urls, output_path, quality_choice, format_choice)

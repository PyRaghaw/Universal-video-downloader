import os
import sys
import subprocess
import re
from yt_dlp import YoutubeDL

def is_valid_url(url):
    """Detect platform based on URL and return platform name or None."""
    patterns = {
        'facebook': [
            r'https?://(?:www\.)?facebook\.com/.*?/videos/\d+',
            r'https?://(?:www\.)?facebook\.com/video\.php\?v=\d+',
            r'https?://(?:www\.)?facebook\.com/.*?/posts/\d+',
            r'https?://(?:www\.)?fb\.watch/[a-zA-Z0-9_-]+'
        ],
        'instagram': [
            r'https?://(?:www\.)?instagram\.com/reel/[a-zA-Z0-9_-]+/?',
            r'https?://(?:www\.)?instagram\.com/p/[a-zA-Z0-9_-]+/?'
        ],
        'youtube': [
            r'https?://(?:www\.)?(youtube\.com|youtu\.be)/.+'
        ]
    }

    for platform, platform_patterns in patterns.items():
        for pattern in platform_patterns:
            if re.match(pattern, url):
                return platform
    return None

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL, 
                       check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def download_video(url, platform, save_path=None):
    """Download video from supported platform using yt-dlp."""
    if not save_path:
        save_path = os.getcwd()

    os.makedirs(save_path, exist_ok=True)

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'nooverwrites': True,
        'no_color': True,
        'progress_hooks': [download_progress]
    }

    print(f"\n🔍 Detected platform: {platform.capitalize()}")
    print("⏳ Downloading video... Please wait...")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"\n✅ Video successfully downloaded to: {save_path}")
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        handle_download_error(e)

def download_progress(d):
    """Display download progress."""
    if d['status'] == 'downloading':
        downloaded_bytes = d.get('downloaded_bytes', 0)
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)

        if total_bytes > 0:
            percent = downloaded_bytes / total_bytes * 100
            print(f"\r⬇️ Downloading: {percent:.1f}%", end='', flush=True)

def handle_download_error(error):
    """Handle download errors with explanations."""
    error_str = str(error).lower()

    if 'ffmpeg' in error_str:
        print("\n🛠️ FFmpeg is required for proper downloading (esp. for audio/video merge).")
        print("Install it from https://ffmpeg.org or use the following commands:")
        print("- Mac: brew install ffmpeg")
        print("- Windows: Download & add to PATH from ffmpeg.org")
        print("- Linux: sudo apt install ffmpeg")
    elif 'private' in error_str or '403' in error_str:
        print("\n🔒 The video may be private or region-locked.")
    elif 'unsupported url' in error_str:
        print("\n⚠️ Unsupported URL. Make sure it's a valid video link.")

def main():
    print("====================================")
    print("    UNIVERSAL VIDEO DOWNLOADER 🎥   ")
    print("====================================")

    if not check_ffmpeg():
        print("⚠️ FFmpeg not found. Audio-video merge may fail.")

    while True:
        url = input("\n📌 Enter video URL (Facebook/Instagram/YouTube): ").strip()

        if not url:
            print("❌ URL cannot be empty.")
            continue

        platform = is_valid_url(url)
        if not platform:
            print("⚠️ Unsupported or invalid video URL.")
            continue

        save_path = input("📂 Enter folder path to save (leave blank for current directory): ").strip()
        save_path = save_path if save_path else None

        download_video(url, platform, save_path)

        again = input("\n🔁 Download another video? (y/n): ").strip().lower()
        if again != 'y':
            break

    print("\n👋 Thank you for using Universal Video Downloader!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Download cancelled by user.")
        sys.exit(0)


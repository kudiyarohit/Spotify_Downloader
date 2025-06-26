import os
import subprocess
import glob
import shutil
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from pytube import YouTube
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def download_mp3(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

def get_thumbnail(url):
    yt = YouTube(url)
    video_id = yt.video_id
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

def songLink(song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        return results['tracks']['items'][0]['external_urls']['spotify']
    else:
        return "Song not found."

def extractId(url):
    parts = url.split("/")
    for i, part in enumerate(parts):
        if part == "playlist" or part == "track":
            return parts[i + 1].split("?")[0]
    return None

def song_download(url, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    output_template = f"{output_folder}/{{artist}} - {{title}}"
        
    if "track" in url:
        track_id = extractId(url)
        track = sp.track(track_id)
        cover_url = track['album']['images'][0]['url'] if track['album']['images'] else None

        subprocess.run(["spotdl", "download", url, "--output", output_template])
        
        files = sorted(
            glob.glob(os.path.join(output_folder, "*.mp3")),
            key=os.path.getmtime,
            reverse=True
        )

        download_path = files[0] if files else None
        return [download_path, cover_url]
    
    elif "playlist" in url:
        playlist_id = extractId(url)
        playlist = sp.playlist(playlist_id)
        cover_url = playlist['images'][0]['url'] if playlist['images'] else None
        name = sp.playlist(playlist_id)['name']
        playlist_folder = os.path.join(output_folder, f"{name}")
        
        os.makedirs(playlist_folder, exist_ok=True)

        output_template = f"{playlist_folder}/{{artist}} - {{title}}"
        subprocess.run(["spotdl", "download", url, "--output", output_template])
        
        zip_path = os.path.join(output_folder, f"{name}")
        shutil.make_archive(zip_path, "zip", playlist_folder)
        
        files = sorted(
            glob.glob(os.path.join(output_folder, "*.zip")),
            key=os.path.getmtime,
            reverse=True
        )
        download_path = files[0] if files else None
        return [download_path, cover_url]
    
    else:
        if "youtube.com" in url or "youtu.be" in url:
            cover_url = get_thumbnail(url)

            downloaded_file = {"filename": None}

            def hook(d):
                if d['status'] == 'finished':
                    downloaded_file['filename'] = d['filename']

            outtmpl = os.path.join(output_folder, '%(title)s.%(ext)s')

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': outtmpl,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'progress_hooks': [hook],
                'quiet': False,
                'noplaylist': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if downloaded_file['filename']:
                mp3_file = os.path.splitext(downloaded_file['filename'])[0] + '.mp3'
                download_path = os.path.abspath(mp3_file)
                return [download_path, cover_url]
            else:
                return [None, cover_url]
            
        else:
            spotify_link = songLink(url)
            if spotify_link == "Song not found.":
                return [None, None]

            track_id = extractId(spotify_link)
            track = sp.track(track_id)
            cover_url = track['album']['images'][0]['url'] if track['album']['images'] else None
            subprocess.run(["spotdl", "download", url, "--output", output_template])
        
        files = sorted(
            glob.glob(os.path.join(output_folder, "*.mp3")),
            key=os.path.getmtime,
            reverse=True
        )

        download_path = files[0] if files else None
        return [download_path, cover_url]
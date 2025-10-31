import os
import requests
import yt_dlp
import re

def get_video_source(path_or_url, download_dir="downloads"):

    """
        Get video source either from local or download it 

        Args:
            path_or_url (string): the path or the url to get the video .
            download_dir (string): The directory where video will be place.

        Returns:
            string: Path to the video download
    """
    os.makedirs(download_dir, exist_ok=True)

    # Case 1 : local files
    if os.path.exists(path_or_url):
        return path_or_url

    # Case 2 : URL
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        if "youtube.com" in path_or_url or "youtu.be" in path_or_url:
            print(f"[INFO] Download by YouTube : {path_or_url}")
            ydl_opts = {
                "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(path_or_url, download=True)
                downloaded_path = ydl.prepare_filename(info)
                if not downloaded_path.endswith(".mp4"):
                    downloaded_path = os.path.splitext(downloaded_path)[0] + ".mp4"
            return downloaded_path
        else:
            local_filename = os.path.join(download_dir, os.path.basename(path_or_url.split('?')[0]))
            if not os.path.exists(local_filename):
                print(f"[INFO] Downlaod by {path_or_url}...")
                with requests.get(path_or_url, stream=True) as r:
                    r.raise_for_status()
                    with open(local_filename, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                print(f"[OK] Download : {local_filename}")
            return local_filename

    raise ValueError(f"Format no recognize : {path_or_url}")

def cleanup_directory(directory="downloads"):
    """ Delete all files in directory
        Args:
            directory (string): The directory to clean .
    
    """
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Erreur lors de la suppression de {file_path} : {e}")

def sanitize_filename(filename):
    """
    Replace caracters if it can be problem for the filename
    Arg:
        filename (string) : name of the file who need to have correct name
    """
    # Supprimer les caractères illégaux
    sanitized = re.sub(r'[<>:"/\\|?*]', '-', filename)
    # Supprimer les espaces multiples
    sanitized = re.sub(r'\s+', ' ', sanitized)
    # Supprimer les espaces ou points en fin de nom
    sanitized = sanitized.strip().rstrip('.')
    return sanitized

def rename_file(original_path, new_name):

    """
    Rename file
    Args:
        original_path (string) : the path of the file
        new_name (string) : the new name of the file
    return 
        new_path (string) : new path of the file
    """
    directory, old_filename = os.path.split(original_path)
    extension = os.path.splitext(old_filename)[1]
    new_path = os.path.join(directory, sanitize_filename(new_name) + extension)
    os.rename(original_path, new_path)
    return new_path

def rename_all_files_segment_in_directory(directory, new_base_name):

    """
    Rename all file in directory by the part it represents in the video
    Args:
        directory (string) : Directory where all files will be rename
        new_bas_name (string) : the common base of all files

    """
    all_segments = sorted([
        f for f in os.listdir(directory)
    ])

    for index, filename in enumerate(all_segments):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            new_name = f"[Partie {index + 1}] {new_base_name}"
            rename_file(file_path, new_name)
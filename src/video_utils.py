import os
import shutil
import tempfile
import ffmpeg
import textwrap
from moviepy import VideoFileClip
from src.source_file_utils import get_video_source
from src.subtitles_utils import load_subtitles_master, load_subtitles_master_ass, save_ass, seconds_to_srt_time

def cut_segment_of_video(file_video, number_of_segment, start_cuting_time_code, time_of_segment, directory_videos, file_video_name_output):
    """
        Cut the video in multiple segments of the video

        Args:
            file_video (string): the path or the url to get the video .
            download_dir (string): The directory where video will be place.

        Returns:
            string: Path to the video download
    """
    file_video = get_video_source(file_video)  
    os.makedirs(directory_videos, exist_ok=True)
    clip = VideoFileClip(file_video)
    start = start_cuting_time_code

    for i in range(number_of_segment):
        end = start + time_of_segment
        if end > clip.duration:
            end = clip.duration
        segment = clip.subclipped(start, end)
        segment.write_videofile(f"{directory_videos}/{file_video_name_output}_{i}.mp4", codec="libx264")
        start = end
        if start >= clip.duration:
            break
    clip.reader.close()
    clip.audio = None

def add_subtitles_to_video_segments_ass_segment_only(
    directory_videos,
    directory_input_sub,
    directory_output,
    file_video_name_output,
    burn_in=True
):
    """
    Add subtitles of segments with .ass extension

    Args:
        directory_videos (string): directory where videos are
        directory_input_sub (string): directory where subtitle are
        directory_output (string): directory for the output video
        file_video_name_output (string): name of the output video
        burn_in (bool, optional): If subtitles are embedded or not. Defaults to True.
    """
    all_segments = sorted([
        f for f in os.listdir(directory_videos)
        if f.startswith(file_video_name_output) and f.endswith(".mp4")
    ])

    print(f"[INFO] {len(all_segments)} segments found in {directory_videos}")

    for seg_file in all_segments:
        segment_path = os.path.join(directory_videos, seg_file)
        segment_path_ass = os.path.join(directory_input_sub, f"{os.path.splitext(seg_file)[0]}.ass")

        with tempfile.NamedTemporaryFile(dir=directory_videos, suffix=".mp4", delete=False) as tmpfile:
            temp_output = tmpfile.name

        if not os.path.exists(segment_path_ass):
            print(f"[WARNING] No file .ass for {seg_file}, skip.")
            continue
        try:
            if burn_in:
                (
                    ffmpeg
                    .input(segment_path)
                    .output(
                        temp_output, 
                        vf=f"ass='{segment_path_ass.replace(os.sep, '/')}'",
                        vcodec="libx264", 
                        acodec="copy"
                    )
                    .run(overwrite_output=True, quiet=False)
                )

            print(f"[OK] Subtitles add to : {temp_output}")

        except ffmpeg.Error as e:
            print(f"[ERREUR] ffmpeg failed with {seg_file} : {e}")
        finally:
            shutil.move(temp_output, segment_path)
        if directory_output:
            shutil.move(segment_path, directory_output)
    print("\n[OK] All segments are subtitled ")

def add_part_to_video(segment_path, title, font_path=None, output_path=None):
    """
    Add banner part for the video

    Args:
        segment_path (string): path to segment
        title (string): Number of the part
        font_path (_type_, optional): Which use. Defaults to None.
        output_path (_type_, optional): path to the ouput directory. Defaults to None.
    """
    directory = os.path.dirname(segment_path)

    with tempfile.NamedTemporaryFile(dir=directory, suffix=".mp4", delete=False) as tmpfile:
        temp_output = tmpfile.name

    font_option = f"fontfile='{font_path}'" if font_path else "font='Arial'"
    vf = (
        "drawtext="
        f"text='{title}':"
        f"{font_option}:"
        "fontsize=70:"
        "fontcolor=black:"
        "x=(w-text_w)/2:"
        "y=1500:"
        "box=1:"
        "boxcolor=white@1.0:"
        "boxborderw=25"
    )

    try:
        (
            ffmpeg
            .input(segment_path)
            .output(
                temp_output,
                vf=vf,
                vcodec="libx264",
                acodec="copy"
            )
            .run(overwrite_output=True, quiet=False)
        )

        destination = output_path if output_path else segment_path
        shutil.move(temp_output, destination)

    except ffmpeg.Error as e:
        print(f"[ERREUR] ffmpeg failed : {e}")
        if os.path.exists(temp_output):
            os.remove(temp_output)

def add_title_to_video(
    segment_path, 
    title, 
    font_path=None, 
    output_path=None,
    max_chars_per_line=25
):
    """Add title banner to the video

    Args:
        segment_path (string): path to the segment
        title (string): title in the banner
        font_path (_type_, optional): Which font to use. Defaults to None.
        output_path (_type_, optional): path for the output directory. Defaults to None.
        max_chars_per_line (int, optional): Number of characters per line. Defaults to 25.
    """
    directory = os.path.dirname(segment_path)

    with tempfile.NamedTemporaryFile(dir=directory, suffix=".mp4", delete=False) as tmpfile:
        temp_output = tmpfile.name

    print(f"[INFO] Ajout du titre '{title}' à {segment_path}")

    wrapped_title = "\n".join(textwrap.wrap(title, width=max_chars_per_line))
    font_option = f"fontfile='{font_path}'" if font_path else "font='Arial'"

    length = len(title)
    if length < 30:
        fontsize = 70
    elif length < 60:
        fontsize = 60
    else:
        fontsize = 50

    vf = (
        "drawtext="
        f"text='{wrapped_title}':"
        f"{font_option}:"
        f"fontsize={fontsize}:"
        "fontcolor=black:"
        "x=(w-text_w)/2:"
        "y=(h/10):"
        "line_spacing=15:"
        "box=1:"
        "boxcolor=white@0.9:"
        "boxborderw=25"
    )

    try:
        (
            ffmpeg
            .input(segment_path)
            .output(
                temp_output,
                vf=vf,
                vcodec="libx264",
                acodec="copy"
            )
            .run(overwrite_output=True, quiet=False)
        )

        destination = output_path if output_path else segment_path
        shutil.move(temp_output, destination)
        print(f"[OK] Titre ajouté et fichier mis à jour : {destination}")

    except ffmpeg.Error as e:
        print(f"[ERREUR] ffmpeg a échoué : {e}")
        if os.path.exists(temp_output):
            os.remove(temp_output)

def convert_to_tiktok_format(
    directory_videos, 
    file_video_name_output, 
    directory_output = None,
    mode="letterbox"
):
    """Transform video to 16:9 format to 9:16 to correspond to the tiktok

    Args:
        directory_videos (string): directory where videos
        file_video_name_output (string): name for the output video
        directory_output (string, optional): path to output directory. Defaults to None.
        mode (string, optional): letterbox format or crop. Defaults to "letterbox".

    Raises:
        ValueError: wrong mode
    """

    if mode == "letterbox":
        vf = "scale=1080:-1:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
    elif mode == "crop":
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    else:
        raise ValueError("Unknown mode. Choose 'letterbox' or 'crop'")

    all_segments = sorted([
        f for f in os.listdir(directory_videos)
        if f.startswith(file_video_name_output) and f.endswith('.mp4')
    ])

    for seg_file in all_segments:
        segment_path = os.path.join(directory_videos, seg_file)

        with tempfile.NamedTemporaryFile(dir=directory_videos, suffix=".mp4", delete=False) as tmpfile:
            temp_output = tmpfile.name

        (
            ffmpeg
            .input(segment_path)
            .output(
                temp_output,
                vf=vf,
                vcodec="libx264",
                acodec="copy"
            )
            .run(overwrite_output=True, quiet=False)
        )

        shutil.move(temp_output, segment_path)
        if directory_output:
            shutil.move(segment_path, directory_output)

        print(f"[OK] Video converted : {segment_path}")

def add_part_to_correct_index(directory_videos, output_path=None):
    """Add part banner with correct index video

    Args:
        directory_videos (string): directory where videos
        output_path (string, optional): output path for the video. Defaults to None.
    """
    all_segments = sorted([
        f for f in os.listdir(directory_videos)
        if f.endswith(".mp4")
    ])

    for i, seg_file in enumerate(all_segments):
        seg_path = os.path.join(directory_videos, seg_file)

        with tempfile.NamedTemporaryFile(dir=directory_videos, suffix=".mp4", delete=False) as tmpfile:
            temp_output = tmpfile.name

        try:
            add_part_to_video(
                segment_path=seg_path,
                title=f"Partie {i + 1}",
                output_path=temp_output,
                font_path="./fonts/Montserrat-SemiBold.otf"
            )


        except Exception as e:
            print(f"[ERROR] in {seg_file} : {e}")
            if os.path.exists(temp_output):
                os.remove(temp_output)
        finally:
            shutil.move(temp_output, seg_path)
            if output_path:
                shutil.move(seg_path, output_path)

def add_title_to_correct_index(directory_videos, video_title, output_path=None):
    """Add title banner with correct index video

    Args:
        directory_videos (string): directory where videos
        output_path (string, optional): output path for the video. Defaults to None.
        video_title (string, optional): title in the banner the video. Defaults to None.

    """
    all_segments = sorted([
        f for f in os.listdir(directory_videos)
        if f.endswith(".mp4")
    ])

    for i, seg_file in enumerate(all_segments):
        seg_path = os.path.join(directory_videos, seg_file)

        with tempfile.NamedTemporaryFile(dir=directory_videos, suffix=".mp4", delete=False) as tmpfile:
            temp_output = tmpfile.name

        try:
            add_title_to_video(
                segment_path=seg_path,
                title=f"{video_title}",
                output_path=temp_output,
                font_path="./fonts/Montserrat-SemiBold.otf"
            )

        except Exception as e:
            print(f"[ERROR] in {seg_file} : {e}")
            if os.path.exists(temp_output):
                os.remove(temp_output)

        finally:
            shutil.move(temp_output, seg_path)
            if output_path:
                shutil.move(seg_path, output_path)


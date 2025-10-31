from datetime import timedelta
import json
import os
import re
import whisper

from src.source_file_utils import get_video_source


def save_srt(segments, output_path="subtitles.srt"):

    """Save subtiltes in .srt 

    Args:
        segments (string): segments where subtitles are find
        output_path (str, optional): output path of the subtitles file. Defaults to "subtitles.ass".
    """

    def format_time(seconds):
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hh = total_seconds // 3600
        mm = (total_seconds % 3600) // 60
        ss = total_seconds % 60
        ms = int((seconds - total_seconds) * 1000)
        return f"{hh:02}:{mm:02}:{ss:02},{ms:03}"

    idx = 1
    with open(output_path, "w", encoding="utf-8") as f:
        for seg in segments:
            words = seg.get("words", [])
            if words:
                for w in words:
                    f.write(f"{idx}\n")
                    f.write(f"{format_time(w['start'])} --> {format_time(w['end'])}\n")
                    f.write(f"{w['word'].strip()}\n\n")
                    idx += 1
            else:
                f.write(f"{idx}\n")
                f.write(f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n")
                f.write(f"{seg['text'].strip()}\n\n")
                idx += 1

def save_ass(segments, output_path="subtitles.ass"):
    """Save subtiltes stylized in .ass 

    Args:
        segments (string): segments where subtitles are find
        output_path (str, optional): output path of the subtitles file. Defaults to "subtitles.ass".
    """
    def format_time_ass(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds - int(seconds)) * 100)
        return f"{h}:{m:02}:{s:02}.{cs:02}"

    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MyStyle,Arial,75,&H00FFFFFF,&H00000000,&H64000000,0,0,1,2,1,2,10,10,400,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = [header]
    for seg in segments:
        words = seg.get("words", [])
        if words:
            for w in words:
                lines.append(f"Dialogue: 0,{format_time_ass(w['start'])},{format_time_ass(w['end'])},MyStyle,,0,0,0,,{w['word'].strip()}")
        else:
            lines.append(f"Dialogue: 0,{format_time_ass(seg['start'])},{format_time_ass(seg['end'])},MyStyle,,0,0,0,,{seg['text'].strip()}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def srt_to_json(srt_file, json_file):
    """Create json from srt file

    Args:
        srt_file (string): srt file
        json_file (string): json file
    """
    with open(srt_file, 'r', encoding='utf-8') as f:
        data = f.read()

    pattern = re.compile(r'(\d+)\s+([\d:,]+)\s-->\s([\d:,]+)\s+(.*?)\n(?=\d+\s|$)', re.DOTALL)
    subtitles = []

    for match in pattern.finditer(data):
        idx, start, end, text = match.groups()
        subtitles.append({
            "index": int(idx),
            "start": start.strip(),
            "end": end.strip(),
            "text": text.replace("\n", " ").strip()
        })

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(subtitles, f, ensure_ascii=False, indent=2)

def json_to_srt(json_file, srt_file):
    """Create srt from json file

    Args:
        srt_file (string): srt file
        json_file (string): json file
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        subtitles = json.load(f)

    with open(srt_file, 'w', encoding='utf-8') as f:
        for sub in subtitles:
            f.write(f"{sub['index']}\n")
            f.write(f"{sub['start']} --> {sub['end']}\n")
            f.write(f"{sub['text']}\n\n")

def transcribe_video_to_srt(video_to_transcribe_path, output_srt_file_path, output_json_file_path):
    """Transcribe video with whisper model

    Args:
        video_to_transcribe_path (string): path to the video to transcribe
        output_srt_file_path (string): ouput path for the srt file
        output_json_file_path (string): ouput path for the json file
    """
    video_to_transcribe_path = get_video_source(video_to_transcribe_path) 
    model = whisper.load_model("medium")
    result = model.transcribe(video_to_transcribe_path,word_timestamps=True)
    save_srt(result["segments"], output_path=output_srt_file_path)
    srt_to_json(output_srt_file_path, output_json_file_path)
    del model

def transcribe_video_to_ass(video_to_transcribe_path, output_ass_file_path, output_json_file_path):
    """Transcribe video with whisper model

    Args:
        video_to_transcribe_path (string): path to the video to transcribe
        output_ass_file_path (string): ouput path for the ass file
        output_json_file_path (string): ouput path for the json file
    """
    video_to_transcribe_path = get_video_source(video_to_transcribe_path) 
    model = whisper.load_model("medium")
    result = model.transcribe(video_to_transcribe_path,word_timestamps=True)
    save_ass(result["segments"], output_path=output_ass_file_path)
    srt_to_json(output_ass_file_path, output_json_file_path)
    del model

def transcribe_all_segments_to_ass(directory_videos,directory_output_sub, file_video_name_output):
    """Transcribe segments by segments

    Args:
        directory_videos (string): directory where are the videos
        directory_output_sub (string): where place subtitles
        file_video_name_output (string): name of the video output
    """
    all_segments = sorted([
        f for f in os.listdir(directory_videos)
        if f.startswith(file_video_name_output) and f.endswith('.mp4')
    ])


    model = whisper.load_model("medium")

    for i, seg_file in enumerate(all_segments):
        segment_path = os.path.join(directory_videos, seg_file)
        output_ass_file_path = os.path.join(directory_output_sub, f"{os.path.splitext(seg_file)[0]}.ass")
        output_json_file_path = os.path.join(directory_output_sub, f"{os.path.splitext(seg_file)[0]}.json")

        print(f"[INFO] → Transcription of segements {i+1}/{len(all_segments)} : {seg_file}")
        result = model.transcribe(segment_path, word_timestamps=True)

        save_ass(result["segments"], output_path=output_ass_file_path)
        with open(output_json_file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    del model

def srt_time_to_seconds(t):
    """Transform srt time to seconds

    Args:
        t (string): time in srt file
    """
    hh, mm, ss_ms = t.split(':')
    ss, ms = ss_ms.split(',')
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000.0

def ass_time_to_seconds(t):
    """Transform ass time to seconds

    Args:
        t (string): time in ass file
    """
    h, m, s_cs = t.split(":")
    s, cs = s_cs.split(".")
    return int(h)*3600 + int(m)*60 + int(s) + int(cs)/100.0

def seconds_to_srt_time(seconds):
    if seconds < 0:
        seconds = 0
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hh = total_seconds // 3600
    mm = (total_seconds % 3600) // 60
    ss = total_seconds % 60
    ms = int((seconds - total_seconds) * 1000)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"

def load_subtitles_master(path):
    """Load the subtitles file

    Args:
        path (string): path to subtitles file
    """
    if path.lower().endswith('.json'):
        with open(path, 'r', encoding='utf-8') as f:
            subs = json.load(f)
        normalized = []
        for s in subs:
            start = s['start']
            end = s['end']
            if isinstance(start, str):
                s_start = srt_time_to_seconds(start)
                s_end = srt_time_to_seconds(end)
            else:
                s_start = float(start)
                s_end = float(end)
            normalized.append({'start': s_start, 'end': s_end, 'text': s['text']})
        return normalized
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    pattern = re.compile(r'(\d+)\s+([\d:,]+)\s-->\s([\d:,]+)\s+(.*?)\n(?=\d+\s|$)', re.DOTALL)
    subs = []
    for m in pattern.finditer(data):
        _, start, end, text = m.groups()
        subs.append({'start': srt_time_to_seconds(start), 'end': srt_time_to_seconds(end), 'text': text.replace("\n", " ").strip()})
    return subs

def load_subtitles_master_ass(path):
    """Load the subtitles file

    Args:
        path (string): path to subtitles file
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    events_section = False
    subs = []
    for line in lines:
        line = line.strip()
        if line.startswith("[Events]"):
            events_section = True
            continue
        if not events_section:
            continue
        if line.startswith("Format:"):
            fields = [x.strip().lower() for x in line[len("Format:"):].split(",")]
            start_idx = fields.index("start")
            end_idx = fields.index("end")
            text_idx = fields.index("text")
            continue
        if line.startswith("Dialogue:"):
            parts = line[len("Dialogue:"):].split(",", len(fields)-1)
            start = ass_time_to_seconds(parts[start_idx].strip())
            end = ass_time_to_seconds(parts[end_idx].strip())
            text = parts[text_idx].strip()
            text = re.sub(r"{.*?}", "", text)
            subs.append({"start": start, "end": end, "text": text})
    return subs
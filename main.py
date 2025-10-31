
import os
from src import cut_segment_of_video,transcribe_all_segments_to_ass,convert_to_tiktok_format,add_subtitles_to_video_segments_ass_segment_only,cleanup_directory,rename_all_files_segment_in_directory
from src.video_utils import add_part_to_correct_index, add_title_to_correct_index

PATH_TO_VIDEO = "https://www.youtube.com/watch?YOUR_VIDEO or path/to/your/video"
NUMBER_OF_SEGMENT = 9
START_TIME_CODE = 0
TIME_OF_SEGMENT = 90
DIRECTORY_VIDEOS = "./segments/"
DIRECTORY_OUTPUT = "./output/"
DIRECTORY_VIDEOS_SUB = "./subtitles/"
FILE_VIDEO_NAME_OUTPUT = "example_segment"
PATH_ASS_FILE = "./segments/example.ass"
PATH_JSON_FILE = "./segments/example.json"
VIDEO_NAME = "name of your video"
TITLE_TO_ADD = "name of the title in the video"

cut_segment_of_video(
    PATH_TO_VIDEO,
    number_of_segment=NUMBER_OF_SEGMENT,
    start_cuting_time_code=START_TIME_CODE,
    time_of_segment=TIME_OF_SEGMENT,
    directory_videos=DIRECTORY_VIDEOS,
    file_video_name_output=FILE_VIDEO_NAME_OUTPUT
)
'''
transcribe_all_segments_to_ass(
    directory_videos=DIRECTORY_VIDEOS,
    directory_output_sub=DIRECTORY_VIDEOS_SUB,
    file_video_name_output=FILE_VIDEO_NAME_OUTPUT
)
'''
convert_to_tiktok_format(
    directory_videos=DIRECTORY_VIDEOS,
    file_video_name_output=FILE_VIDEO_NAME_OUTPUT,
    mode="letterbox"
)

'''
add_subtitles_to_video_segments_ass_segment_only(
    directory_videos=DIRECTORY_VIDEOS,
    directory_input_sub=DIRECTORY_VIDEOS_SUB,
    directory_output=DIRECTORY_OUTPUT,
    file_video_name_output=FILE_VIDEO_NAME_OUTPUT,
    burn_in=True
)

'''

add_part_to_correct_index(
    directory_videos=DIRECTORY_VIDEOS,
    output_path=None, 
)

add_title_to_correct_index(
    directory_videos=DIRECTORY_VIDEOS,
    video_title=TITLE_TO_ADD,
    output_path=DIRECTORY_OUTPUT
)

rename_all_files_segment_in_directory(DIRECTORY_OUTPUT, VIDEO_NAME)
cleanup_directory(DIRECTORY_VIDEOS)
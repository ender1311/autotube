import os
import datetime
from moviepy.editor import VideoFileClip

video_path = 'IMG_3638.MOV'

# Check if the file exists
if not os.path.exists(video_path):
    print("The file does not exist.")
else:
    # File system attributes
    file_size = os.path.getsize(video_path)
    creation_time = os.path.getctime(video_path)
    modification_time = os.path.getmtime(video_path)
    access_time = os.path.getatime(video_path)

    print(f"File Size: {file_size} bytes")
    print(f"Creation Time: {datetime.datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Modification Time: {datetime.datetime.fromtimestamp(modification_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Access Time: {datetime.datetime.fromtimestamp(access_time).strftime('%Y-%m-%d %H:%M:%S')}")

    # Video content attributes using moviepy
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration  # Duration in seconds
        resolution = clip.size  # Returns (width, height)
        fps = clip.fps  # Frames per second

        print(f"Duration: {duration} seconds")
        print(f"Resolution: {resolution[0]}x{resolution[1]}")
        print(f"Frame Rate: {fps} FPS")

        clip.close()
    except Exception as e:
        print(f"An error occurred while reading the video file: {str(e)}")

import os
import datetime
from moviepy.editor import VideoFileClip

# this code will rename files and put them in correct subfolders

def organize_videos(videos_folder):
    # Check if the videos folder exists
    if not os.path.exists(videos_folder):
        print("The specified folder does not exist.")
        return
    
    # Loop through all files in the folder
    for filename in os.listdir(videos_folder):
        video_path = os.path.join(videos_folder, filename)
        
        # Check if it's a file and a video based on extension
        if os.path.isfile(video_path) and filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            try:
                # Using creation time from the filesystem (could also parse from metadata)
                creation_time = os.path.getctime(video_path)
                date = datetime.datetime.fromtimestamp(creation_time)
                
                # Create subfolders based on year and quarter
                year_folder = os.path.join(videos_folder, str(date.year))
                quarter = (date.month - 1) // 3 + 1
                quarter_folder = os.path.join(year_folder, f'Q{quarter}')
                
                # Ensure the subfolders exist
                if not os.path.exists(year_folder):
                    os.makedirs(year_folder)
                if not os.path.exists(quarter_folder):
                    os.makedirs(quarter_folder)
                
                # Prepare the new filename
                new_filename = date.strftime('%Y.%m.%d') + os.path.splitext(filename)[1]
                new_file_path = os.path.join(quarter_folder, new_filename)
                
                # Handle duplicate filenames
                file_counter = 1
                while os.path.exists(new_file_path):
                    new_filename = f"{date.strftime('%Y.%m.%d')}.{chr(64 + file_counter)}{os.path.splitext(filename)[1]}"
                    new_file_path = os.path.join(quarter_folder, new_filename)
                    file_counter += 1
                
                # Rename and move the file
                os.rename(video_path, new_file_path)
                print(f"Moved and renamed file to {new_file_path}")
            
            except Exception as e:
                print(f"An error occurred processing {filename}: {str(e)}")

# Specify the videos folder
videos_folder = r'd:\fam_vid'  # Raw string for the path
organize_videos(videos_folder)

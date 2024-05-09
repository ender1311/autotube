import os
import datetime
import shutil

# Define the source and target directories
source_directory = 'C:/Coding/youtube/'
target_directory = 'C:/FamilyVideos'

# Ensure the target directory exists
if not os.path.exists(target_directory):
    os.makedirs(target_directory)

# Dictionary to track filenames and ensure unique names
filename_tracker = {}

# Loop through each file in the source directory
for filename in os.listdir(source_directory):
    if filename.endswith(".mov") or filename.endswith(".mp4"):
        video_path = os.path.join(source_directory, filename)
        
        # Check if the file exists
        if os.path.exists(video_path):
            # Get file system attributes
            creation_date = os.path.getctime(video_path)
            modification_date = os.path.getmtime(video_path)
            formatted_date = datetime.datetime.fromtimestamp(modification_date).strftime('%Y.%m.%d')
            file_extension = os.path.splitext(video_path)[1]  # Extract file extension
            
            # Generate the base new file name
            base_new_file_name = f"{formatted_date}{file_extension}"
            new_file_name = base_new_file_name
            
            # Ensure the filename is unique
            counter = 1
            while new_file_name in filename_tracker:
                new_file_name = f"{formatted_date}_{counter}{file_extension}"
                counter += 1
            
            # Add the new file name to the tracker and copy the file
            filename_tracker[new_file_name] = True
            new_file_path = os.path.join(target_directory, new_file_name)
            shutil.copy(video_path, new_file_path)
            print(f"File copied and renamed from {video_path} to {new_file_path}")

print("Processing complete.")

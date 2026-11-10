import os
import re
import shutil

source_dir = "data/full_data"
dest_dir = "data/full_data_final"

# Create the destination directory if it doesn't exist
os.makedirs(dest_dir, exist_ok=True)

# Update the regex pattern to match .drawio files
pattern = re.compile(r"^(\d+)-(\d+)-.*\.drawio$")
latest_attempts = {}

# Step 1: Find the latest attempt's base name for each user
for file in os.listdir(source_dir):
    match = pattern.match(file)
    if not match:
        continue

    user_id = match.group(1)
    attempt = int(match.group(2))
    
    # Strip the '.drawio' extension (7 characters) to get the clean base name
    base_name = file[:-7]

    if user_id not in latest_attempts or attempt > latest_attempts[user_id][0]:
        latest_attempts[user_id] = (attempt, base_name)

# Step 2: Copy both the .drawio and .png files to the final directory
for user_id, (attempt, base_name) in latest_attempts.items():
    # Update the extension list to process .drawio instead of .xml
    for ext in [".drawio", ".png"]:
        src_path = os.path.join(source_dir, f"{base_name}{ext}")
        dest_path = os.path.join(dest_dir, f"{base_name}{ext}")
        
        # Verify the file exists before copying to prevent crashes
        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)

print(f"Successfully transferred {len(latest_attempts)} submission pairs to {dest_dir}")
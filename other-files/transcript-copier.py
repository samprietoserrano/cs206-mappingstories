import os
import shutil
import time

def copy_all_files(source_folder, destination_folder):
    """
    Copies all files from subdirectories of `source_folder` to `destination_folder`.

    :param source_folder: Path to the source directory
    :param destination_folder: Path to the destination directory
    """
    # print(os.path.exists(source_folder))
    # print(os.path.exists(destination_folder))
    # return
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    else:
        shutil.rmtree(destination_folder)

    time.sleep(2)  # Pauses execution for 2 seconds

    for root, _, files in os.walk(source_folder):
        for file in files:
            source_file_path = os.path.join(root, file)
            destination_file_path = os.path.join(destination_folder, file)

            if "all" in source_file_path or not source_file_path.endswith(".txt"):
                # print("Skipping non-text file: ", source_file_path)
                continue
            
            # print(f"Copying: {source_file_path} -> {destination_file_path}")
            # If a file with the same name exists, rename it
            counter = 1
            while os.path.exists(destination_file_path):
                name, ext = os.path.splitext(file)
                destination_file_path = os.path.join(destination_folder, f"{name}_{counter}{ext}")
                counter += 1

            shutil.copy2(source_file_path, destination_file_path)
            print(f"Copied: {source_file_path} -> {destination_file_path}")

if __name__ == "__main__":
    source_folder = "././transcripts"  # Replace with your source folder path
    destination_folder = "././transcripts/all-compiled"  # Replace with your destination folder path

    # copy_all_files(source_folder, destination_folder)

    files_now = len([f for f in os.listdir(destination_folder) if os.path.isfile(os.path.join(destination_folder, f))])
    print(f"Total files copied: {files_now}")
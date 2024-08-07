import os
import subprocess
import argparse
import multiprocessing
import zipfile

def getPath(filename):
    import sys
    from os import chdir
    from os.path import join
    from os.path import dirname
    from os import environ

    if hasattr(sys, '_MEIPASS'):
        chdir(sys._MEIPASS)
        filename = join(sys._MEIPASS, filename)
    elif '_MEIPASS2' in environ:
        chdir(environ['_MEIPASS2'])
        filename = join(environ['_MEIPASS2'], filename)
    else:
        parent = os.path.dirname(os.path.abspath(__file__))
        filename = join(parent, filename)

    return filename

def addFFmpegPath():
    ffmpeg_path = getPath('ffmpeg')
    ffprobe_path = getPath('ffprobe')

    if not os.path.exists(ffmpeg_path):
        print(f"ffmpeg not found at {ffmpeg_path}")
        return
    if not os.path.exists(ffprobe_path):
        print(f"ffprobe not found at {ffprobe_path}")
        return

    print(f"ffmpeg_path: {ffmpeg_path}")
    print(f"ffprobe_path: {ffprobe_path}")

    os.environ['PATH'] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ['PATH']
    os.environ['PATH'] = os.path.dirname(ffprobe_path) + os.pathsep + os.environ['PATH']
    print("Updated PATH: ", os.environ['PATH'])

    # Check permissions
    if not os.access(ffmpeg_path, os.X_OK):
        print(f"ffmpeg is not executable. Setting executable permissions.")
        os.chmod(ffmpeg_path, 0o755)
    if not os.access(ffprobe_path, os.X_OK):
        print(f"ffprobe is not executable. Setting executable permissions.")
        os.chmod(ffprobe_path, 0o755)

    # Test if ffmpeg can be called using just its name
    try:
        result = subprocess.call(["ffmpeg", "-version"])
        print(f"ffmpeg call result: {result}")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
    except Exception as e:
        print(f"Exception: {e}")


def unzip_file_old(zip_path, extract_to):   
    if not os.path.isfile(zip_path):
        print(f"The file {zip_path} does not exist.")
        return

    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"Extracted all files to {extract_to}")

def unzip_file(zip_path, extract_to):
    extract_to = os.path.expanduser(extract_to)
    
    if not os.path.isfile(zip_path):
        print(f"The file {zip_path} does not exist.")
        return
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_contents = zip_ref.namelist()

        all_files_exist = all(os.path.exists(os.path.join(extract_to, member)) for member in zip_contents)
        
        if all_files_exist:
            print(f"All files already exist in {extract_to}. Skipping extraction.")
        else:            
            if not os.path.exists(extract_to):
                os.makedirs(extract_to)
            
            zip_ref.extractall(extract_to)
            print(f"Extracted all files to {extract_to}")

def unzip_silero_vad():
    from pathlib import Path
    zip_file_path = getPath('silero-vad/snakers4_silero-vad_master.zip')
    extraction_directory = str(Path.home() / '.cache/torch/testhub')

    unzip_file(zip_file_path, extraction_directory)

if __name__ == '__main__':
    multiprocessing.freeze_support()

    parser = argparse.ArgumentParser(description='Generate TTS audio with voice cloning.')
    parser.add_argument('-o', '--output', type=str, help='Path to save the output audio file.')
    parser.add_argument('-r', '--reference', type=str, help='Path to the reference speaker audio file.')
    parser.add_argument('-t', '-i', '--text', type=str, help='Text to be converted to speech.')
    
    args = parser.parse_args()
    # addFFmpegPath()    
    unzip_silero_vad()

    
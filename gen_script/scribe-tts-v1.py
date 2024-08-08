import os
import torch
import multiprocessing
import argparse
import traceback
import sys
from os.path import join
from os import environ

REFERENCE_FILES = {
    0: 'demo_speaker0.mp3',
    1: 'demo_speaker1.mp3',
    2: 'demo_speaker2.mp3',
    3: 'example_reference.mp3',
    4: 'dv.mp3'
}

def getPath(filename):
    # from os import chdir
    # from os.path import dirname    

    if hasattr(sys, '_MEIPASS'):
        # PyInstaller >= 1.6
        # chdir(sys._MEIPASS)
        filename = join(sys._MEIPASS, filename)
    elif '_MEIPASS2' in environ:
        # PyInstaller < 1.6 (tested on 1.5 only)
        # chdir(environ['_MEIPASS2'])
        filename = join(environ['_MEIPASS2'], filename)
    else:
        parent = os.path.dirname(os.path.abspath(__file__))
        filename = join(parent, filename)

    return filename

def choose_reference_file(default_index=0):    
    if default_index in REFERENCE_FILES:
        return getPath(join('resources', REFERENCE_FILES[default_index]))
    else:
        raise ValueError(f"Invalid reference file index: {default_index}. Valid range is 0-{len(REFERENCE_FILES) - 1}.")

def main(args):
    from openvoice import se_extractor
    from openvoice.api import BaseSpeakerTTS, ToneColorConverter

    ckpt_base = getPath('checkpoints/base_speakers/EN')
    ckpt_converter = getPath('checkpoints/converter')
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    output_dir = 'outputs'

    # initialize BaseSpeakerTTS
    base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)
    base_speaker_tts.load_ckpt(f'{ckpt_base}/checkpoint.pth')

    # initialize ToneColorConverter
    tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
    tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

    # ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # load source speaker embedding
    source_se = torch.load(f'{ckpt_base}/en_default_se.pth').to(device)

    # path to reference speaker audio    
    if args.reference:
        reference_speaker = args.reference
    else:
        try:
            reference_speaker = choose_reference_file(default_index=args.default_ref_index)
        except ValueError as e:
            print(traceback.format_exc())
            print(e)
            return

    # extract target speaker embedding
    try:
        target_se, audio_name = se_extractor.get_se(
            reference_speaker, 
            tone_color_converter, 
            target_dir='processed', 
            vad=True
            )
    except Exception as e:
        print(traceback.format_exc())
        print(f"Error extracting speaker embedding: {e}")
        return

    # define output file paths
    save_path = args.output if args.output else f'{output_dir}/output_en_default.wav'
    
    # create directories for save_path if they don't exist
    save_dir = os.path.dirname(save_path)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        
    src_path = f'{output_dir}/tmp.wav'

    # text to be converted to speech
    text = args.text

    # Run!!
    try:
        base_speaker_tts.tts(text, src_path, speaker='default', language='English', speed=1.0)
    except Exception as e:
        print(traceback.format_exc())
        print(f"Error generating TTS audio: {e}")
        return

    # run ToneColorConverter
    encode_message = "@MyShell"
    try:
        tone_color_converter.convert(
            audio_src_path=src_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=save_path,
            message=encode_message
        )
    except Exception as e:
        print(traceback.format_exc())
        print(f"Error converting tone and color: {e}")
        return

    print(f"Audio generated and saved to {save_path}")

def addFFmpegPath():
    ffmpeg_path = getPath('ffmpeg')
    ffprobe_path = getPath('ffprobe')

    if not os.path.exists(ffmpeg_path):
        print(f"ffmpeg not found at {ffmpeg_path}")
        return
    if not os.path.exists(ffprobe_path):
        print(f"ffprobe not found at {ffprobe_path}")
        return

    # debugging logs
    # print(f"ffmpeg_path: {ffmpeg_path}")
    # print(f"ffprobe_path: {ffprobe_path}")

    os.environ['PATH'] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ['PATH']
    os.environ['PATH'] = os.path.dirname(ffprobe_path) + os.pathsep + os.environ['PATH']
    # print("Updated PATH: ", os.environ['PATH'])

    # Check permissions
    if not os.access(ffmpeg_path, os.X_OK):
        print(f"ffmpeg is not executable. Setting executable permissions.")
        os.chmod(ffmpeg_path, 0o755)
    if not os.access(ffprobe_path, os.X_OK):
        print(f"ffprobe is not executable. Setting executable permissions.")
        os.chmod(ffprobe_path, 0o755)

    # import subprocess
    # try:
    #     result = subprocess.call(["ffmpeg", "-version"])
    #     print(f"ffmpeg call result: {result}")
    # except FileNotFoundError as e:
    #     print(f"FileNotFoundError: {e}")
    # except Exception as e:
    #     print(f"Exception: {e}")

def unzip_file(zip_path, extract_to):
    import zipfile
    extract_to = os.path.expanduser(extract_to)
    
    if not os.path.isfile(zip_path):
        print(f"The file {zip_path} does not exist.")
        return
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_contents = zip_ref.namelist()

        all_files_exist = all(os.path.exists(os.path.join(extract_to, member)) for member in zip_contents)
        
        if all_files_exist:
            # print(f"All files already exist in {extract_to}. Skipping extraction.")
            print("All files already exist. Skipping extraction.")
        else:            
            if not os.path.exists(extract_to):
                os.makedirs(extract_to)
            
            zip_ref.extractall(extract_to)
            # print(f"Extracted all files to {extract_to}")
            print(f"Extracted all files.")

def unzip_silero_vad():
    from pathlib import Path
    zip_file_path = getPath('silero-vad/snakers4_silero-vad_master.zip')
    extraction_directory = str(Path.home() / '.cache/torch/hub')

    unzip_file(zip_file_path, extraction_directory)

def validate_args(args):    
    if not args.text:
        raise ValueError("Text to be converted to speech is required.")
    
    if args.default_ref_index < 0 or args.default_ref_index >= len(REFERENCE_FILES):
        raise ValueError(f"Invalid default reference index {args.default_ref_index}. Valid range is 0-{len(REFERENCE_FILES) - 1}.")

if __name__ == '__main__':
    print("----------------------------------------")
    print("OpenVoice V1 TTS for LightWeave Scribe")
    print("----------------------------------------")
    multiprocessing.freeze_support()

    # Argument parser
    parser = argparse.ArgumentParser(description='Generate TTS audio with voice cloning.')
    parser.add_argument('-o', '--output', type=str, help='Path to save the output audio file.')
    parser.add_argument('-r', '--reference', type=str, help='Path to the reference speaker audio file.')
    parser.add_argument('-t', '--text', type=str, help='[REQUIRED] Text to be converted to speech.')
    parser.add_argument('-ri', '--default-ref-index', type=int, default=0, help=f'Default reference speaker file index to use if -r is not provided (valid range: 0-{len(REFERENCE_FILES) - 1}).')
        
    args = parser.parse_args()
    
    try:
        validate_args(args)
    except ValueError as e:                
        parser.print_help()
        print("\nExample usage:\n> scribe_tts_v1 -t 'Hello, this is a test.' [-r path/to/reference_speaker.mp3] [-o path/to/output.wav] [--default-ref-index 1]")
        print(f"\nError: {e}")
        sys.exit(1)
    
    addFFmpegPath()
    unzip_silero_vad()
    main(args)
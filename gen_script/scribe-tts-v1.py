import os
import torch
import multiprocessing
import argparse
import traceback

def getPath(filename):
    import os
    import sys
    from os import chdir
    from os.path import join
    from os.path import dirname
    from os import environ

    if hasattr(sys, '_MEIPASS'):
        # PyInstaller >= 1.6
        chdir(sys._MEIPASS)
        filename = join(sys._MEIPASS, filename)
        # print("MEIPASS")
        # print(filename)
    elif '_MEIPASS2' in environ:
        # PyInstaller < 1.6 (tested on 1.5 only)
        chdir(environ['_MEIPASS2'])
        filename = join(environ['_MEIPASS2'], filename)
        # print("MEIPASS22")
        # print(filename)
    else:        
        # chdir(dirname(sys.argv[0]))
        # filename = join(dirname(sys.argv[0]), filename)
        parent = os.path.dirname(os.path.abspath(__file__))
        filename = join(parent, filename)
        # print("ELSE")
        # print(filename)
        
    # print("dirname")
    # print(os.path.dirname(os.path.realpath(__file__)))
    # print("getCwd")
    # cwd = os.getcwd()
    # print(cwd)

    return filename

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
    reference_speaker = args.reference if args.reference else getPath('resources/demo_speaker0.mp3') # This is the voice you want to clone

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
    text = args.text if args.text else "This audio is generated by OpenVoice."

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

    # import subprocess
    # try:
    #     result = subprocess.call(["ffmpeg", "-version"])
    #     print(f"ffmpeg call result: {result}")
    # except FileNotFoundError as e:
    #     print(f"FileNotFoundError: {e}")
    # except Exception as e:
    #     print(f"Exception: {e}")

if __name__ == '__main__':
    print("OpenVoice V1 TTS for LightWeave Scribe")
    multiprocessing.freeze_support()

    # Argument parser
    parser = argparse.ArgumentParser(description='Generate TTS audio with voice cloning.')
    parser.add_argument('-o', '--output', type=str, help='Path to save the output audio file.')
    parser.add_argument('-r', '--reference', type=str, help='Path to the reference speaker audio file.')
    parser.add_argument('-t', '-i', '--text', type=str, help='Text to be converted to speech.')
    
    args = parser.parse_args()
    addFFmpegPath()
    main(args)
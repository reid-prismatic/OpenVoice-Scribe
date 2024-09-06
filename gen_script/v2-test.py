import os
import torch
import multiprocessing
import sys
from os.path import join
from os import environ
from openvoice import se_extractor
from openvoice.api import ToneColorConverter

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


def main():
    print("Start------")

    ckpt_converter = getPath('checkpoints_v2/converter')
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    output_dir = 'outputs_v2'
    # print(device)

    print("1111")
    tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
    tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')
    print("2222")
    print(tone_color_converter)
    os.makedirs(output_dir, exist_ok=True)
    print("3333")

    # reference_speaker = 'resources/example_reference.mp3' # This is the voice you want to clone
    # reference_speaker = 'resources/sample-reid.mp3' # This is the voice you want to clone
    # reference_speaker = '/Users/reid/Projects/prismatic/research/tts/openvoice/OpenVoice/resources/sample-reid.mp3' # This is the voice you want to clone
    reference_speaker = getPath('resources/demo_speaker0.mp3') # This is the voice you want to clone
    target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, vad=False)
    print("44444")

    from melo.api import TTS
    print("555555")
    texts = {
        'EN_NEWEST': "LightWeave Products are awesome! I love Prismatic Company!!",  # The newest English base speaker model
        'EN': "Did you ever hear a folk tale about a giant turtle?",
        'ES': "El resplandor del sol acaricia las olas, pintando el cielo con una paleta deslumbrante.",
        'FR': "La lueur dorée du soleil caresse les vagues, peignant le ciel d'une palette éblouissante."
    }


    src_path = f'{output_dir}/tmp-reid.wav'

    # Speed is adjustable
    speed = 1.0

    cwd = os.getcwd()
    print(cwd)
    # print(src_path)
    # print("END--")

    # for language, text in texts.items():
    #     model = TTS(language=language, device=device)
    #     speaker_ids = model.hps.data.spk2id
        
    #     for speaker_key in speaker_ids.keys():
    #         speaker_id = speaker_ids[speaker_key]
    #         speaker_key = speaker_key.lower().replace('_', '-')
            
    #         source_se = torch.load(f'OpenVoice/checkpoints_v2/base_speakers/ses/{speaker_key}.pth', map_location=device)
    #         model.tts_to_file(text, speaker_id, src_path, speed=speed)
    #         save_path = f'{output_dir}/output_v2_{speaker_key}.wav'

    #         # Run the tone color converter
    #         encode_message = "@MyShell"
    #         tone_color_converter.convert(
    #             audio_src_path=src_path, 
    #             src_se=source_se, 
    #             tgt_se=target_se, 
    #             output_path=save_path,
    #             message=encode_message)

    #///////
    language = 'EN_NEWEST'
    text = texts[language]
    model = TTS(language=language, device=device)
    speaker_ids = model.hps.data.spk2id
    speaker_key = 'EN-Newest'

    # for speaker_key in speaker_ids.keys():
    print('before')
    print(speaker_key)
    speaker_id = speaker_ids[speaker_key]
    speaker_key = speaker_key.lower().replace('_', '-')
    print('after')
    print(speaker_key)

    check_base = getPath('checkpoints_v2/base_speakers/ses')
    source_se = torch.load(f'{check_base}/{speaker_key}.pth', map_location=device)
    model.tts_to_file(text, speaker_id, src_path, speed=speed)
    save_path = f'{output_dir}/output_v2_{speaker_key}.wav'

    # Run the tone color converter
    encode_message = "@MyShell"
    tone_color_converter.convert(
        audio_src_path=src_path, 
        src_se=source_se, 
        tgt_se=target_se, 
        output_path=save_path,
        message=encode_message)

    print("END--")



if __name__ == '__main__':
    multiprocessing.freeze_support()
    addFFmpegPath()    
    main()
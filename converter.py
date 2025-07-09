import subprocess
import json
import os

video_path= input("Enter a path to your video file: ").strip().strip('"').strip("'")
print("You entered:", video_path)
if not os.path.exists(video_path):
    print("ERROR: File not found at that path.")
    exit()

probe_command = [
    'ffprobe',
    '-v', 'error',
    '-show_streams',
    '-print_format', 'json',
    video_path
]
try:
    result = subprocess.run(probe_command, capture_output=True, text=True, check=True)
    streams = json.loads(result.stdout)['streams']
except subprocess.CalledProcessError as e:
    print(f"Error running ffprobe: {e}")
    print(f"Stderr: {e.stderr}")
    exit()
except json.JSONDecodeError:
    print("Error parsing ffprobe output. Is ffprobe installed and in your PATH?")
    exit()


print("\nAvailable Streams:")
has_subtitles = any(stream['codec_type'] == 'subtitle' for stream in streams)
for stream in streams:
    index = stream['index']
    codec_type = stream['codec_type']
    codec_name = stream.get('codec_name', 'unknown')
    language = stream.get('tags', {}).get('language', 'undefined')
    print(f"Stream #{index}: Type={codec_type}, Codec={codec_name}, Language={language}")

output_path= input("Enter your output path e.g. 'C:\\movies\\New.mp4\\Example.mp4 '").strip().strip("'").strip('"')
print("You entered:", output_path)

valid_stream=[f"0:{s['index']}" for s in streams]
while True:
    Map1=input("Map your first stream").strip()
    if Map1.lower() in valid_stream:
        break
    else:
        print("Invalid Streams! Please enter one of the following: " + ', '.join(valid_stream))
        
while True:
    Map2=input("Map your second stream").strip()
    if Map2.lower() in valid_stream:
        break
    else:
        print("Invalid Streams! Please enter one of the following: " + ', '.join(valid_stream))

ValidResolutionsList=['1920:1080', '1280:720','640:420']
ResolutionChecker=None
while True:
    scale=input("Select a Resolution")
    
    if scale in ValidResolutionsList:
        print("Valid selection")
        ResolutionChecker=True
        break
    else:
        print("Invalid resolution")
        print("Valid resolutions are: " + ', '.join(ValidResolutionsList))

my_subtitle=False
valid_answers=['y','n']

Map3 = None
subtitle_codec = None
HardSubtitle=False
if has_subtitles:
    while True:
        ConditionalSubtitle=input("Enable subtitles? (y/n): ").strip()
        if ConditionalSubtitle.lower() == 'y':
            my_subtitle=True
            break
        elif ConditionalSubtitle.lower() not in valid_answers:
            print("Pick: " + ', '.join(valid_answers))
        elif ConditionalSubtitle.lower() == 'n':
            my_subtitle=False
            break

HardSubtitleAnswer=False
subtitle_filename=None

if my_subtitle:
     while True:
         import_choice=input("Do you want to import srt for Hard Subtitles (Must be in same directory) (y for hard subtitles/n for soft subtitles)" )
        
        
         if import_choice.lower() == 'y':
            subtitle_filename=input("Enter the name of the SRT file for hard subtitles ")
            subtitle_filename = os.path.join(os.path.dirname(video_path), subtitle_filename)
            subtitle_filename = os.path.abspath(subtitle_filename).replace('\\', '/')
            if not os.path.isfile(subtitle_filename):
                print("ERROR: Subtitle file not found.")
                
            else:
                print("File Valid")
                HardSubtitleAnswer=True
                break
            
         elif import_choice.lower() == 'n':
             HardSubtitleAnswer=False
             break
    
         elif import_choice.lower() not in valid_answers:
            print("Pick: " + ', '.join(valid_answers))
    
if not HardSubtitleAnswer:
    valid_subtitle_streams = [f"0:{stream['index']}" for stream in streams if stream['codec_type'] == 'subtitle']
    if not valid_subtitle_streams:
        print("No subtitle streams found in the video to map. Disabling subtitle option.")
        my_subtitle = False
    else:
        while True:
            print(valid_subtitle_streams)
            Map3 = input("Map your soft subtitle stream").strip()
            if Map3 in valid_subtitle_streams:
                subtitle_index = int(Map3.split(':')[1])
                subtitle_stream = next((s for s in streams if s['index'] == subtitle_index), None)
                if subtitle_stream:
                    subtitle_codec = subtitle_stream.get('codec_name', '').lower()
                break
            else:
                print("Invalid Streams! Please enter one of the following: " + ', '.join(valid_subtitle_streams))
     
valid_audio_codec=['aac', 'mp3', 'ac3', 'eac3', 'opus', 'flac']
while True:
    audio_codec=input("Enter your audio codec: ").lower()
    if audio_codec.lower() in valid_audio_codec:
        break
    else:
        print("Invalid codec! Please enter one of the following: " + ', '.join(valid_audio_codec))

valid_video_codec=['libx264', 'libx265', 'mpeg4', 'vp9']
while True:
    video_codec=input("Enter your video codec: ").lower()
    if video_codec.lower() in valid_video_codec:
        break
    else:
        print("Invalid codec! Please enter one of the following: " + ', '.join(valid_video_codec))


ffmpeg_command = [
    'ffmpeg', '-y',
    '-i', video_path,
    '-map', Map1,
    '-map', Map2,
    '-c:v', video_codec,
    '-c:a', audio_codec
]

scale_filter = f"scale={scale}" if ResolutionChecker else ""

vf_filters = []

if HardSubtitleAnswer and subtitle_filename:
    vf_filters.append(f"subtitles={os.path.basename(subtitle_filename)}")

if ResolutionChecker:
    vf_filters.append(f"scale={scale}")

if vf_filters:
    ffmpeg_command += ['-vf', ','.join(vf_filters)]
    
if Map3 and not HardSubtitleAnswer:
    ffmpeg_command += ['-map', Map3]
    output_extension = os.path.splitext(output_path)[1].lower()
    output_subtitle_codec = 'copy'
    if subtitle_codec == 'subrip' and output_extension == '.mp4':
        output_subtitle_codec = 'mov_text'
    ffmpeg_command += ['-c:s', output_subtitle_codec]
    
        

ffmpeg_command.append(output_path)

print("\nRunning ffmpeg command:")
print(' '.join(ffmpeg_command))
try:
    if HardSubtitleAnswer:
        os.chdir(os.path.dirname(subtitle_filename))
    subprocess.run(ffmpeg_command, check=True)
    print("\nFFmpeg process completed successfully!")
except subprocess.CalledProcessError as e:
    print(f"\nError running ffmpeg: {e}")
    print(f"Stderr: {e.stderr}")
except FileNotFoundError:
    print("\nError: ffmpeg not found. Please ensure ffmpeg is installed and in your system's PATH.")

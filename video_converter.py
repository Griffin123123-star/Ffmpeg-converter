import subprocess
import json
import os

video_path= input("Enter a path to your video file: ")
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
result = subprocess.run(probe_command, capture_output=True, text=True)



streams = json.loads(result.stdout)['streams']
print("\nAvailable Streams:")

for stream in streams:
    index = stream['index']
    codec_type = stream['codec_type']
    codec_name = stream.get('codec_name', 'unknown')
    language = stream.get('tags', {}).get('language', 'undefined')
    print(f"Stream #{index}: Type={codec_type}, Codec={codec_name}, Language={language}")




output_path= input("Enter your output path e.g. 'C:\\movies\\New.mp4/mkv'")
print("You entered:", output_path)

valid_stream=['0:0','0:1','0:2','0:3','0:4','0:5','0:6','0:7','0:8']
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

my_subtitle=False
valid_answers=['y','n']
while True:
    ConditionalSubtitle=input("Do you want subtitles? (y/n): ").strip()
    if ConditionalSubtitle.lower() == 'y':
        my_subtitle=True
        break

    elif ConditionalSubtitle.lower() not in valid_answers:
        print("Pick: " + ', '.join(valid_answers))

    elif ConditionalSubtitle.lower() == 'n':
        my_subtitle=False
        break

my_subtitles1=False
valid_answers1=['y','n']
if my_subtitle:
    while True:
        ConditionalHardSubtitle=input("Do you want hard subtitles? (y/n): ").strip()
        if ConditionalHardSubtitle.lower() == 'y':
            my_subtitle1=True
            break

        elif ConditionalHardSubtitle.lower() not in valid_answers1:
         print("Pick: " + ', '.join(valid_answers1))
        elif ConditionalHardSubtitle.lower() == 'n':
            my_subtitle1=False
            break

valid_subtitle_streams = [f"0:{stream['index']}" for stream in streams if stream['codec_type'] == 'subtitle']
if my_subtitle==True:
    while True:
        print(valid_subtitle_streams)
        Map3=input("Map your third subtitle stream").strip()
        if Map3 in valid_subtitle_streams:
            break
        else:
            print("Invalid Streams! Pleasse enter one of the following: " + ', '.join(valid_subtitle_streams))

     

    
        

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
'ffmpeg',
'-i',video_path,

'-map',Map1
,
'-map',Map2,

'-c:v',
video_codec,
'-c:a',
audio_codec,

]

if my_subtitle:
    if my_subtitle1: #hard subtitles
        ffmpeg_command += [
            '-filter_complex',
            f"subtitles='{video_path}':si={int(Map3.split(':')[1])}"
        ]
    else:  # soft subtitles
        ffmpeg_command += ['-map', Map3, '-c:s', 'copy']
  
ffmpeg_command.append(output_path)
print("Running ffmpeg command:")
print(' '.join(ffmpeg_command))

subprocess.run(ffmpeg_command)

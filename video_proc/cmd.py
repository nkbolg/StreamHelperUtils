import os
import subprocess
from dataclasses import dataclass

image_template = """magick -gravity center -background black -fill white -size 852x480 -font /System/Library/Fonts/MarkerFelt.ttc caption:"{}" short.png"""

cmd1_template = """ffmpeg -i "{input_file}" -i short.png -filter_complex "
       color=c=black:size=852x480 [temp]; \
       [temp][1:v] overlay=x=0:y=0:enable='between(t,0,1)' [temp]; \
       [0:v] setpts=PTS+1/TB, scale=852x480:force_original_aspect_ratio=decrease, pad=852:480:-1:-1:color=black [v:0]; \
       [temp][v:0] overlay=x=0:y=0:shortest=1:enable='gt(t,1)' [v]; \
       [0:a] asetpts=PTS+1/TB [a]" -map [v] -map [a] "{out_file}.mp4" """

cut_piece_template = "ffmpeg -ss {start_time} -to {end_time} -i \"{input_file}\" -c copy \"{out_file}\""
in_file = "2023-01-06 20-00-01.mkv"

os.chdir('stream_06.01.2023')

@dataclass
class Part:
    title: str
    start_time: str
    end_time: str


def read_parts(filename: str) -> list[Part]:
    xs = []
    with open(filename) as f:
        for line in f:
            start_time, _, end_time, *name = line.split(" ")
            xs.append(Part(title=' '.join(name).strip(), start_time=start_time, end_time=end_time))
    return xs


parts = read_parts("tracklist.txt")


def fmt_time(time: str) -> str:
    items = list(map(int, time.split('-')))
    if len(items) == 2:
        return f"00:{items[0]:02}:{items[1]:02}"
    elif len(items) == 3:
        return f"{items[0]:02}:{items[1]:02}:{items[2]:02}"
    else:
        raise RuntimeError("Unexpected time str: " + time)



for part in parts:
    print(f"Processing {part.title}")

    piece_filename = part.title + '.mp4'

    cut_cmd = cut_piece_template.format(start_time=fmt_time(part.start_time),
                                        end_time=fmt_time(part.end_time),
                                        input_file=in_file,
                                        out_file=piece_filename)

    print(cut_cmd)
    result = subprocess.run(cut_cmd, shell=True)
    if result.returncode != 0:
        # handle the error
        raise RuntimeError("Stop")

    image_cmd = image_template.format(part.title)
    print(image_cmd)
    result = subprocess.run(image_cmd, shell=True)
    if result.returncode != 0:
        # handle the error
        raise RuntimeError("Stop")
    cmd1 = cmd1_template.format(input_file=piece_filename, out_file=part.title + '_out')
    print(cmd1)
    result = subprocess.run(cmd1, shell=True)
    if result.returncode != 0:
        # handle the error
        raise RuntimeError("Stop")

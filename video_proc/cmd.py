import os
import subprocess
from dataclasses import dataclass

resolution = 768, 432

image_template = f"""convert -gravity center -background black -fill white -size {resolution[0]}x{resolution[1]} caption:"{{}}" short.png"""

cmd1_template = f"""ffmpeg -i "{{input_file}}" -i short.png -filter_complex "
       color=c=black:size={resolution[0]}x{resolution[1]} [temp]; \
       [temp][1:v] overlay=x=0:y=0:enable='between(t,0,1)' [temp]; \
       [0:v] setpts=PTS+1/TB, scale={resolution[0]}x{resolution[1]}:force_original_aspect_ratio=decrease, pad={resolution[0]}:{resolution[1]}:-1:-1:color=black [v:0]; \
       [temp][v:0] overlay=x=0:y=0:shortest=1:enable='gt(t,1)' [v]; \
       [0:a] asetpts=PTS+1/TB [a]" -map [v] -map [a] "{{out_file}}" """

cut_piece_template = "ffmpeg -ss {start_time} -to {end_time} -i \"{input_file}\" -c copy \"{out_file}\""

dir_name = input("Dir name: ")
# in_file = "2023-01-06 20-00-01.mkv"
in_file = input("input file name: ")
os.chdir(dir_name)


@dataclass
class Part:
    author: str
    song_name: str
    start_time: str
    end_time: str

    @property
    def title(self):
        return f"{self.author} — {self.song_name}"


def read_parts(filename: str) -> list[Part]:
    xs = []
    with open(filename) as f:
        for line in f:
            start_time, _, end_time, *name = line.rstrip().split(" ")
            pos = name.index('-')
            author = ' '.join(name[:pos])
            song_name = ' '.join(name[pos+1:])
            xs.append(Part(author=author, song_name=song_name, start_time=start_time, end_time=end_time))
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


if not os.path.exists('res'):
    os.mkdir('res')

if not os.path.exists('piece'):
    os.mkdir('piece')

if not os.path.exists('mp3'):
    os.mkdir('mp3')

for part in parts:
    print(f"Processing {part.title}")

    piece_filename = os.path.join('piece',  part.title + '.mp4')

    if not os.path.exists(piece_filename):
        cut_cmd = cut_piece_template.format(start_time=fmt_time(part.start_time),
                                            end_time=fmt_time(part.end_time),
                                            input_file=in_file,
                                            out_file=piece_filename)
        subprocess.run(cut_cmd, shell=True, check=True)

    res_file = os.path.join('res', f"{part.title}.mp4")

    if not os.path.exists(res_file):
        image_cmd = image_template.format(f"{part.author}\n{part.song_name}")
        subprocess.run(image_cmd, shell=True, check=True)

        cmd1 = cmd1_template.format(input_file=piece_filename, out_file=res_file)
        subprocess.run(cmd1, shell=True, check=True)

    music_file = os.path.join('mp3', f"{part.title}.mp3")

    if not os.path.exists(music_file):
        subprocess.run(f'ffmpeg -i "{piece_filename}" -metadata title="{part.song_name}" -metadata artist="{part.author}" "{music_file}"', shell=True, check=True)



cmd0_template = """magick -gravity center -background black -fill white -size 852x480 -font /System/Library/Fonts/MarkerFelt.ttc caption:"{}" short.png"""

cmd1_template = """ffmpeg -i {input_file}.mp4 -i short.png -filter_complex "
       color=c=black:size=852x480 [temp]; \
       [temp][1:v] overlay=x=0:y=0:enable='between(t,0,1)' [temp]; \
       [0:v] setpts=PTS+1/TB, scale=852x480:force_original_aspect_ratio=decrease, pad=852:480:-1:-1:color=black [v:0]; \
       [temp][v:0] overlay=x=0:y=0:shortest=1:enable='gt(t,1)' [v]; \
       [0:a] asetpts=PTS+1/TB [a]" -map [v] -map [a] {out_file}.mp4"""

files = {
    "bi2": "Би-2 Её Глаза",
    "bluz": "Пилот Большой Питерский Блюз",
    "chaif": "Чайф Аргентина-Ямайка",
    "kino": "Кино Бездельник",
    "kish": "КиШ Северный флот",
    "kukri": "Кукрыниксы Это не беда",
    "maks": "Ногу Свело Турецкий Гамбит",
    "nau": "Наутилус Берег",
    "noize": "Noize MC Зелёный",
    "rock": "Пилот Рок!",
    "rozi": "Ночные снайперы Розы",
}

import subprocess

for file, capt in files.items():
    print(f"Processing {file}")
    cmd0 = cmd0_template.format(capt)
    print(cmd0)
    result = subprocess.run(cmd0, shell=True)
    if result.returncode != 0:
        # handle the error
        raise RuntimeError("Stop")
    cmd1 = cmd1_template.format(input_file=file, out_file=file + '_out')
    print(cmd1)
    result = subprocess.run(cmd1, shell=True)
    if result.returncode != 0:
        # handle the error
        raise RuntimeError("Stop")

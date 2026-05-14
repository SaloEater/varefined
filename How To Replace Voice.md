To replace voice for existing language follow these steps:

## 1) DLTX
You need to  dltx `configs/plugins/varefined.ltx`. That can be done by creating `mod_varefined_<any_suffix>.ltx` in `configs/plugins`.
There you need to override lines amount for the language that you replace.
For that you want to use language prefix:
- rus - Russian
- eng - English

For example, to replace English voice you need to override `lines_eng` section:
```ltx
![lines_eng]
```
Then you want to disable **ALL** existing lines definitions to erase all existing voice lines:
```ltx
![lines_eng]
!add_this_spot
!command_start
!command_stop
...
```
Then you want to add your own lines definitions by replacing disabled lines with your own by replacing
```ltx
![lines_eng]
!add_this_spot
...
```
with
```ltx
![lines_eng]
add_this_spot = 5
...
```
Where `5` is the amount of sound files you have in that folder.

## 2) Sounds files
You need to create required folders described at [Implemented reactions](README.md#implemented-reactions) for your new voice in `gamedata/sounds` and add your sound files there.

Name files according to the template: `<folder_name>_<ordered number>.ogg`. For example, if you have 3 sound files for `add_this_spot` they should be named like this:
```
add_this_spot_1.ogg
add_this_spot_2.ogg
add_this_spot_3.ogg
```

You may also find use of this [script](scripts/fix_filenames.py) that will rename all files in all folders according to the template after you put them all there.
I run it like this:
```shell
python scripts/fix_filenames.py <path/to/characters_voice>
```

## 3) Generate muffled sounds
I use a python [script](scripts/batch_armorfx.py) with these parameters:
```shell
python scripts/batch_armorfx.py apply --root gamedata/sounds/characters_voice --in-place --helmet-only --sox <path to sox_ng.exe> --ffmpeg <path to ffmpeg.exe> --preset halo --wet 0.65 --comb-hz 115 --comb-decay 0.75
```
- Sox-NG - https://sourceforge.net/projects/sox/
- FFMPEG - https://ffmpeg.org/download.html

## 4) Double check
Make sure that you have the same amount of sound files in each folder as you defined in `mod_varefined_<any_suffix>.ltx` and that they are named correctly.
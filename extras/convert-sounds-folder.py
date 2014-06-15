import download_dict_sound
import os

print "Looking for .mp3 files and replacing them with wav files"

os.chdir("../sounds")

for file in os.listdir("."):
    if file.endswith(".mp3"):
        download_dict_sound.convert_mp3_to_wav(file)
        os.remove(file)
print os.listdir(".")

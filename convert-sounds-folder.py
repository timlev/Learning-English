import download_dict_sound
import os

print "okay"

os.chdir("sounds")

for file in os.listdir("."):
    if file.endswith(".mp3"):
        download_dict_sound.convert_mp3_to_wav(file)
print os.listdir(".")

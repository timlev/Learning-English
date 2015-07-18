import os
import include.download_dict_sound as download_dict_sound
import sys
import glob

units_root = os.path.relpath("Units")

######## REMOVE HIDDEN (.) FILES ##########
for root, dirs, files in os.walk("./"):
	for f in files:
		if f.startswith(".") and "Learning-English.app" not in root and f != ".gitignore":
			#os.remove(os.join(root,f))
			print os.path.join(os.path.abspath(root),f)
			os.remove(os.path.join(os.path.abspath(root),f))

if len(os.path.split(sys.argv[0])[0]) > 0:
    os.chdir(os.path.split(sys.argv[0])[0])


########## DOWNLOAD GOOGLE SPEECH AND CONVERT TO WAVE#########
picfiles = [os.path.abspath(file) for file in glob.glob('Units/*/*/pics/*.*')]
soundfiles = [os.path.abspath(file) for file in glob.glob('Units/*/*/sounds/*.*')]
comparepicfiles = [file[:file.rindex(".")] for file in picfiles]
comparesoundfiles =[file.replace("speech_google.ogg","").replace("speech_google.wav","").replace("/sounds/","/pics/") for file in soundfiles]
compared = [os.path.split(file) for file in comparepicfiles if file not in comparesoundfiles]
print compared
for item in compared:
    path, raw_word = item[0], item[1]
    download_dict_sound.convert_mp3_to_wav(download_dict_sound.download_google(raw_word, path), True)


############DOWNLOAD DICT SOUNDS#################
dictsoundfiles = [x for x in os.listdir("sounds") if x.startswith(".") == False and os.path.isfile(x)]
print dictsoundfiles

all_words = []
for pic in picfiles:
	f = os.path.basename(pic)
	f = f[:f.rindex(".")]
	f = download_dict_sound.replace_symbols(f)
	f = f.lower()
	f = f.replace("?","").replace("!","").replace(".", "").replace(",","")
	f = f.split(" ")
	all_words += f

all_words = list(set(all_words))
could_not_convert = []
for word in all_words:
	if download_dict_sound.check_downloaded_word(word, "sounds") == False:
		try:
			downloaded_file = download_dict_sound.download(word, "sounds")
			download_dict_sound.convert_mp3_to_wav(downloaded_file, True)
		except:
			pass

print could_not_convert

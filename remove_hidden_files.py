import os
import download_dict_sound
import urllib2
import sys
import glob

######## REMOVE HIDDEN (.) FILES ##########
for root, dirs, files in os.walk("./"):
	for f in files:
		if f.startswith(".") and "RosettaTablet.app" not in root:
			#os.remove(os.join(root,f))
			print os.path.join(os.path.abspath(root),f)
			os.remove(os.path.join(os.path.abspath(root),f))

if len(os.path.split(sys.argv[0])[0]) > 0:
    os.chdir(os.path.split(sys.argv[0])[0])


########## DOWNLOAD GOOGLE SPEECH #########
replacementsdict = {'.exclamationmark': '!', '.apostrophe': "'", '.questionmark': '?', '.comma': ',', '.colon': ':'}

picfiles = [os.path.abspath(file) for file in glob.glob('*/*/pics/*.*')]
soundfiles = [os.path.abspath(file) for file in glob.glob('*/*/sounds/*.*')]

comparepicfiles = [file[:file.rindex(".")] for file in picfiles]
comparesoundfiles =[file.replace("speech_google.ogg","").replace("speech_google.wav","").replace("/sounds/","/pics/") for file in soundfiles]
print len(picfiles)
print len(soundfiles)
print len(comparepicfiles)
print len(comparesoundfiles)

compared = [os.path.split(file) for file in comparepicfiles if file not in comparesoundfiles]

google_translate_url = 'http://translate.google.com/translate_tts'
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)')]

for dirpath, sentence in compared:
    outputdir = dirpath.replace("/pics","/sounds/")
    sentence_corrected = sentence
    for sym in [sym for sym in replacementsdict.keys() if sym in sentence_corrected]:
        sentence_corrected = sentence_corrected.replace(sym,replacementsdict[sym])
    response = opener.open(google_translate_url+'?q='+sentence_corrected.replace(' ','%20')+'&tl=en')
    ofp = open(outputdir+sentence+'speech_google.mp3','wb')
    ofp.write(response.read())
    ofp.close()
    if platform.system() == 'Linux':
        os.system('mplayer -ao pcm:fast:waveheader:file="'+str(outputdir+sentence)+'speech_google.wav" -format s16le -af resample=44100 -vo null -vc null "'+str(outputdir+sentence)+'speech_google.mp3"')
        #os.system('avconv -i '+'"'+str(outputdir+sentence)+'speech_google.mp3" '+'"'+str(outputdir+sentence)+'speech_google1.wav"') #on Linux
        #os.system('avconv -i '+'"'+str(outputdir+sentence)+'speech_google.mp3" -acodec libvorbis '+'"'+str(outputdir+sentence)+'speech_google.ogg"') #on Linux
    else:
        print "*"*20 + "Trying afconvert" + "*"*20
        os.system("afconvert -f 'WAVE' -d I16@44100 " + "'"+str(outputdir+sentence)+"speech_google.mp3' -o "+ '"'+str(outputdir+sentence)+'speech_google.wav"') #on a mac
        #os.system("afconvert -f 'WAVE' -d I16@44100 " + "'"+str(outputdir+sentence)+"speech_google.mp3' -o"+ '"'+str(outputdir+sentence)+'speech_google3.wav"') #on a mac
    os.system('rm '+'"'+str(outputdir+sentence)+'speech_google.mp3"')
    print outputdir    
    print sentence

############# DOWNLOAD DICT FILES #####################
all_files = []
extensions = []
words = []
problems = []
replacementsdict = {'.exclamationmark': '!', '.apostrophe': "'", '.questionmark': '?', '.comma': ',', '.colon': ':'}


for root, dirs, files in os.walk("."):
	for f in files:
		if "pics" in root:
			ext = f[f.rfind("."):]
			f = f.replace(ext,"")
			for word in f.split(" "):
				word_filename = word
				word = word.lower()
				for sym in [sym for sym in replacementsdict.keys() if sym in word_filename]:
					word = word_filename.replace(sym,replacementsdict[sym])
				word.replace("!","")
				words.append(word)
			#print f
			extensions.append(ext)
		#for word in f.split(" "):
			#print word
		#all_files.append(f)

print set(words)

sound_files = os.listdir("sounds")
for word in set(words):
	try:
		if word + ".mp3" not in sound_files:
			download_dict_sound.download(word,"sounds")
			download_dict_sound.convert_mp3_to_wav(os.path.join("sounds",word+".mp3"))
	except:
		problems.append(word)
		pass



#Change ownership properties - writable by teacher and readable by all others
print os.getcwd()
for d in os.walk(os.getcwd()).next()[1]:
    os.system('chmod -R 755 "' + d + '"')

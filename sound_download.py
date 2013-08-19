#!/usr/bin/env python2.7

import urllib2
import os
import glob
import platform
import sys

#http://glowingpython.blogspot.com/2012/11/text-to-speech-with-correct-intonation.html

#change working dir to script folder
if len(os.path.split(sys.argv[0])[0]) > 0:
	os.chdir(os.path.split(sys.argv[0])[0])

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
	sentence_corrected = sentence#.replace(".questionmark","?")
	for sym in [sym for sym in replacementsdict.keys() if sym in sentence_corrected]:
		sentence_corrected = sentence_corrected.replace(sym,replacementsdict[sym])
	response = opener.open(google_translate_url+'?q='+sentence_corrected.replace(' ','%20')+'&tl=en')
	ofp = open(outputdir+sentence+'speech_google.mp3','wb')
	ofp.write(response.read())
	ofp.close()
	if platform.system() == 'Linux':
		os.system('avconv -i '+'"'+str(outputdir+sentence)+'speech_google.mp3" -acodec libvorbis '+'"'+str(outputdir+sentence)+'speech_google.ogg"') #on Linux
	else:
		os.system("afconvert -f 'WAVE' -d I16@44100 " + "'"+str(outputdir+sentence)+"speech_google.mp3'") #on a mac
	os.system('rm '+'"'+str(outputdir+sentence)+'speech_google.mp3"')
	print outputdir	
	print sentence

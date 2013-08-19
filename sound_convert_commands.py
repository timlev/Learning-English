#!/usr/bin/env python2.7

import urllib2
import os
import glob
import platform
import sys
import pygame
pygame.mixer.pre_init(16000, -16, 1, 4096)
pygame.mixer.init()
#http://glowingpython.blogspot.com/2012/11/text-to-speech-with-correct-intonation.html

#change working dir to script folder
if len(os.path.split(sys.argv[0])[0]) > 0:
	os.chdir(os.path.split(sys.argv[0])[0])

replacementsdict = {'.exclamationmark': '!', '.apostrophe': "'", '.questionmark': '?', '.comma': ',', '.colon': ':'}
"""
picfiles = [os.path.abspath(file) for file in glob.glob('*/*/pics/*.*')]
soundfiles = [os.path.abspath(file) for file in glob.glob('*/*/sounds/*.*')]
comparepicfiles = [file[:file.rindex(".")] for file in picfiles]
comparesoundfiles =[file.replace("speech_google.ogg","").replace("speech_google.wav","").replace("/sounds/","/pics/") for file in soundfiles]
print len(picfiles)
print len(soundfiles)
print len(comparepicfiles)
print len(comparesoundfiles)

compared = [os.path.split(file) for file in comparepicfiles if file not in comparesoundfiles]
"""

google_translate_url = 'http://translate.google.com/translate_tts'
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)')]

sentence = "Where is the bathroom.questionmark"
if platform.system() == 'Linux':
	outputdir = "/home/levtim/Desktop/"
else:
	outputdir = "/Users/admin/Desktop/"
sentence_corrected = sentence
for sym in [sym for sym in replacementsdict.keys() if sym in sentence_corrected]:
	sentence_corrected = sentence_corrected.replace(sym,replacementsdict[sym])
response = opener.open(google_translate_url+'?q='+sentence_corrected.replace(' ','%20')+'&tl=en')
ofp = open(outputdir+sentence+'speech_google.mp3','wb')
ofp.write(response.read())
ofp.close()
if platform.system() == 'Linux':
	print "*"*20 + "Trying avconv" + "*"*20
	os.system('avconv -i '+'"'+str(outputdir+sentence)+'speech_google.mp3" '+'"'+str(outputdir+sentence)+'speech_google1.wav"') #on Linux
	pygame.mixer.music.load(str(outputdir+sentence)+'speech_google1.wav')
	pygame.time.wait(100)
	pygame.mixer.music.play(0)
	while pygame.mixer.music.get_busy() == True:
		pygame.time.wait(10)
	print "*"*20 + "Trying sox" + "*"*20
	os.system('sox '+'"'+str(outputdir+sentence)+'speech_google.mp3" '+'"'+str(outputdir+sentence)+'speech_google2.wav"') #on Linux
	#pygame.mixer.music.load(str(outputdir+sentence)+'speech_google2.wav')
	pygame.time.wait(100)
	pygame.mixer.music.play(0)
	while pygame.mixer.music.get_busy() == True:
		pygame.time.wait(10)
	print "*"*20 + "Trying mplayer" + "*"*20
	os.system('mplayer -ao pcm:waveheader:file="'+str(outputdir+sentence)+'speech_google3.wav" -vo null -vc null -format s16le "'+str(outputdir+sentence)+'speech_google.mp3"')
	pygame.mixer.music.load(str(outputdir+sentence)+'speech_google3.wav')
	pygame.time.wait(100)
	pygame.mixer.music.play(0)
	while pygame.mixer.music.get_busy() == True:
		pygame.time.wait(10)
else:
	print "*"*20 + "Trying afconvert" + "*"*20
	os.system("afconvert -f 'WAVE' -d I16 " + "'"+str(outputdir+sentence)+"speech_google.mp3' -o "+ '"'+str(outputdir+sentence)+'speech_google3.wav"') #on a mac
	pygame.mixer.music.load(str(outputdir+sentence)+'speech_google3.wav')
	pygame.time.wait(100)
	pygame.mixer.music.play(0)
	while pygame.mixer.music.get_busy() == True:
		pygame.time.wait(10)
print sentence

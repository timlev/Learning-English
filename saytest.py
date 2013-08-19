import os

outputdir = "/tmp/"
sentence_corrected = "My name is Tim."
sentence = sentence_corrected.replace(" ","")
os.system("say '" + sentence_corrected + "' -o "+ "'"+ outputdir + sentence + "speech_google.aiff'")
os.system("afconvert -f 'WAVE' -d I16@44100 " + "'"+str(outputdir+sentence)+"speech_google.aiff'") #on a mac
os.system("play "+ "'"+str(outputdir+sentence)+"speech_google.wav'")

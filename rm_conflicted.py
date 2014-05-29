import glob
import os


conflicted_wav = glob.glob('*/*/*/*conflict*speech_google.wav')
conflicted_jpg = glob.glob('*/*/*/*_conflict*.jpg')
conflicted_JPG = glob.glob('*/*/*/*_conflict*.JPG')
conflicted_jpg += conflicted_JPG
conflicted_png = glob.glob('*/*/*/*_conflict*.png')
mp3s = glob.glob('*/*/*.mp3')
hidden = glob.glob('*/*/*/.*')
allconflicted = glob.glob('*/*/*/*conflict*')
print len(allconflicted)
for file in allconflicted:
	print file



print len(hidden)
for file in hidden:
	file = os.path.abspath(file)
	os.system("rm '" + file + "'")

for file in conflicted_jpg:
	file = os.path.abspath(file)
	os.system("mv '" + file + "' '" + file[:file.rindex("_conflict")] + ".jpg'")
for file in conflicted_png:
	file = os.path.abspath(file)
	os.system("mv '" + file + "' '" + file[:file.rindex("_conflict")] + ".png'")

for file in conflicted_wav:
	file = os.path.abspath(file)
	os.system("rm '" + file + "'")

for file in mp3s:
	file = os.path.abspath(file)
	os.system("rm '" + file + "'")



print len(conflicted_jpg), len(conflicted_wav), len(mp3s)

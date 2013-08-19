from glob import glob
import os

soundfiles = [os.path.abspath(file) for file in glob('*/*/sounds/*')]
print soundfiles

for sound in soundfiles:
	print sound
	#os.system('rm "' + sound + '"')

import urllib2
import os
import tempfile
import platform

def download(word, directory="./"):
    base = "http://dictionary.cambridge.org/us/dictionary/american-english/"
    qmid = "?q="
    #end = "#"
    end = ""
    query = base + word + qmid + word + end
    response = urllib2.urlopen(query)
    mp3source = ""
    for line in response:
        if "sound audio_play_button pron-us" in line and word + ".mp3" in line:
            #print line
            start = line.find("data-src-mp3=") + len("data-src-mp3=") + 1
            end = line.find(".mp3") + len(".mp3")
            mp3source = line[start:end]
            break
    print query
    print mp3source
    print "Downloading to:", os.path.join(directory, word + ".mp3")

    getmp3 = urllib2.urlopen(mp3source)
    ofp = open(os.path.join(directory, word + ".mp3"),'wb')
    ofp.write(getmp3.read())
    ofp.close()

def replace_symbols(word):
    replacementsdict = {'.exclamationmark': '!', '.apostrophe': "'", '.questionmark': '?', '.comma': ',', '.colon': ':'}
    sentence_corrected = word
    for sym in [sym for sym in replacementsdict.keys() if sym in sentence_corrected]:
        sentence_corrected = sentence_corrected.replace(sym,replacementsdict[sym])
    return sentence_corrected

def remove_symbols_lower(word):
    keep = ["'"]
    ind_word = "".join([l for l in list(word) if l.isalnum() or l == "'"]) #exclude characters except '
    ind_word = ind_word.lower() #lowercase
    return ind_word

def download_google(word, directory="./"):
    replacementsdict = {'.exclamationmark': '!', '.apostrophe': "'", '.questionmark': '?', '.comma': ',', '.colon': ':'}
    google_translate_url = 'http://translate.google.com/translate_tts'
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)')]
    outputdir = directory.replace("/pics","/sounds/")
    sentence_corrected = word
    for sym in [sym for sym in replacementsdict.keys() if sym in sentence_corrected]:
        sentence_corrected = sentence_corrected.replace(sym,replacementsdict[sym])
    response = opener.open(google_translate_url+'?q='+sentence_corrected.replace(' ','%20')+'&tl=en')
    ofp = open(outputdir+word+'speech_google.mp3','wb')
    ofp.write(response.read())
    ofp.close()

def convert_mp3_to_wav(mp3file):
    mp3path = os.path.abspath(mp3file)
    mp3_dir = os.path.dirname(mp3file)
    mp3file = os.path.basename(mp3file)
    wavfile = mp3file.replace(".mp3",".wav")
    wavpath = mp3path.replace(".mp3",".wav")
    if platform.system() == 'Linux':
        os.system('mplayer -ao pcm:fast:waveheader:file="'+ wavpath +'" -format s16le -af resample=44100 -vo null -vc null "'+ mp3path +'"')
    elif platform.system() == 'Windows':
        os.system('"C:\Program Files (x86)\Lame For Audacity\lame.exe" --decode ' + mp3path + " " + wavpath)
    else:
        print "*"*20 + "Trying afconvert" + "*"*20
        os.system("afconvert -f 'WAVE' -d I16@44100 " + "'"+ mp3path +"' -o "+ '"'+ wavpath +'"') #on a mac
    #os.remove(mp3path)
    return wavpath

def get_macsay(word_display, word):
	os.system('say -o "' + os.path.join(tempfile.gettempdir(),word + "speech_google.WAVE") +'" -f BEI16@44100 "' + word_display + '"')
	return os.path.join(tempfile.gettempdir(),word + "speech_google.WAVE")
#problematic examples
#don't
#walked
#Minnesota
#This

if __name__ == "__main__":
    import pygame
    pygame.mixer.init()
    word = "happy"
    download(word, tempfile.gettempdir())
    pygame.mixer.music.load(os.path.join(tempfile.gettempdir(), word + ".mp3"))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy:
        continue
    print "Finished ..."
"""
if __name__ == "__main__":
    with open("get.txt","r") as fp:
        get = fp.read()
    if "," not in get:
        get = get.replace(" ", ", ")
    get = get.replace("\n", ", ")
    get = get.split(", ")
    get = [word for word in get if word != ""]
    print get
    list_of_words = get
    for word in list_of_words:
        if word + ".mp3" not in os.listdir("."):
            download(word)
        try:
            pygame.mixer.music.load(word + ".mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy:
                continue
        except:
            os.system("afplay " + word + ".mp3")
"""

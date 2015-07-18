import urllib2
import os
import tempfile
import platform
def check_downloaded_word(word, directory="./"):
    soundfiles = os.listdir(directory)
    #strip extension
    downloaded_words = [os.path.splitext(x)[0] for x in soundfiles]
    if word in downloaded_words:
        return True
    else:
        return False

def download(word, directory="./"):
    if check_downloaded_word(word, directory):
        return False
    base = "http://dictionary.cambridge.org/us/dictionary/american-english/"
    qmid = "?q="
    #end = "#"
    end = ""
    query = base + word + qmid + word + end
    try:
        response = urllib2.urlopen(query)
    except:
        print "Couldn't find", word
        return False
    mp3source = ""
    for line in response:
        if "sound audio_play_button pron-icon us" in line and word + ".mp3" in line:
            #print line
            start = line.find("data-src-mp3=") + len("data-src-mp3=") + 1
            end = line.find(".mp3") + len(".mp3")
            mp3source = line[start:end]
            break
    #print query
    #print mp3source
    try:
        getmp3 = urllib2.urlopen(mp3source)
        ofp = open(os.path.join(directory, word + ".mp3"),'wb')
        ofp.write(getmp3.read())
        ofp.close()
        print "Downloaded to:", os.path.join(directory, word + ".mp3")
        return os.path.abspath(os.path.join(directory, word + ".mp3"))
    except:
        print "Could not download:", word
        return False


def replace_symbols(word):
    replacementsdict = {'.exclamationmark': '!', '.apostrophe': "'", '.questionmark': '?', '.comma': ',', '.colon': ':'}
    sentence_corrected = word
    for sym in [sym for sym in replacementsdict.keys() if sym in sentence_corrected]:
        sentence_corrected = sentence_corrected.replace(sym,replacementsdict[sym])
    return sentence_corrected

def place_symbols(word):
    replacementsdict = {'.exclamationmark': '!', '.apostrophe': "'", '.questionmark': '?', '.comma': ',', '.colon': ':'}
    raw_file = word
    for key in [sym for sym in replacementsdict.keys() if replacementsdict[sym] in raw_file]:
        raw_file = raw_file.replace(replacementsdict[key], key)
    return raw_file

def remove_symbols_lower(word):
    keep = ["'"]
    ind_word = "".join([l for l in list(word) if l.isalnum() or l == "'"]) #exclude characters except '
    ind_word = ind_word.lower() #lowercase
    return ind_word

def download_google(word, orig_directory="./"):
    replacementsdict = {'.exclamationmark': '!', '.apostrophe': "'", '.questionmark': '?', '.comma': ',', '.colon': ':'}
    file_form_word = place_symbols(word)
    search_form_word = replace_symbols(word)
    google_translate_url = 'http://translate.google.com/translate_tts'
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)')]
    outputdir = os.path.abspath(orig_directory.replace("pics","sounds"))
    response = opener.open(google_translate_url+'?q='+ search_form_word.replace(' ','%20')+'&tl=en')
    ofp = open(os.path.join(outputdir, file_form_word + 'speech_google.mp3'),'wb')
    ofp.write(response.read())
    ofp.close()
    return os.path.join(outputdir, file_form_word + 'speech_google.mp3')

def convert_mp3_to_wav(mp3file, remove_mp3 = False):
    mp3path = os.path.abspath(mp3file)
    mp3_dir = os.path.dirname(mp3file)
    mp3file = os.path.basename(mp3file)
    wavfile = mp3file.replace(".mp3",".wav")
    wavpath = mp3path.replace(".mp3",".wav")
    if platform.system() == 'Linux':
        print "*"*20 + "Trying avconv" + "*"*20
        #os.system('mplayer -ao pcm:fast:waveheader:file="'+ wavpath +'" -format s16le -af resample=44100 -vo null -vc null "'+ mp3path +'"')
        os.system('avconv -i "' + mp3path + '" "' + wavpath + '"')
    elif platform.system() == 'Windows':
        print "*"*20 + "Trying Lame" + "*"*20
        os.system('"C:\Program Files (x86)\Lame For Audacity\lame.exe" --decode ' + mp3path + " " + wavpath)
    else:
        print "*"*20 + "Trying afconvert" + "*"*20
        os.system("afconvert -f 'WAVE' -d I16@44100 " + "'"+ mp3path +"' -o "+ '"'+ wavpath +'"') #on a mac
    if remove_mp3:
        os.remove(mp3path)
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

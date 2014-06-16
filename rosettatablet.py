#!/usr/bin/env python2.7

#added icon
#added wordbuttons to pronunciation practice as well

import urllib2
import os
from os import listdir
from os.path import isfile, join
import random
import datetime
import sys
try:
    import pyaudio
    import wave
    import contextlib
except:
    print "Ooops ... no pyaudio or wave ... Say will try SoX"
import glob
import platform
import tempfile
import include.download_dict_sound as download_dict_sound
#http://glowingpython.blogspot.com/2012/11/text-to-speech-with-correct-intonation.html

try:
    with open("testfile.txt", "w") as fp:
        fp.write("This is a test.")
    import remove_hidden_files
    os.remove("testfile.txt")
except:
    print "You do not have permissions to write in this directory. Files not updated this time."



#change working dir to script folder
if len(os.path.split(sys.argv[0])[0]) > 0:
    os.chdir(os.path.split(sys.argv[0])[0])
dict_sounds_path = os.path.join("sounds")

#replacementsdict = {'.exclamationmark': '!', '.apostrophe': "'", '.questionmark': '?', '.comma': ',', '.colon': ':'}

picfiles = [os.path.abspath(file) for file in glob.glob('Units/*/*/pics/*.*')]
soundfiles = [os.path.abspath(file) for file in glob.glob('Units/*/*/sounds/*.*')]


print "\n \
How to use:\n \
Save pictures to pics folder. Name them exactly what you want the text to be.\n \
Use .questionmark, .comma in the name instead of ? or , etc. -- files cannot have a ? in the name\n \
Run sound_download.py to get audio for text from Google Translate TTS API (unofficial).\n"

# try to import pg module
try:
    import pygame as pg
    from pygame.locals import *
    import pygame._view
except:
    print "RosettaTable depends on the pygame module. Please install pygame."


#start the show
#pg.mixer.pre_init(16000, -16, 1, 4096)
pg.init()
pg.mixer.init()
#pg.event.set_allowed(None)
#pg.event.set_allowed([pg.QUIT, pg.MOUSEBUTTONDOWN])
pg.event.set_blocked(pg.MOUSEMOTION)
#Get Date
now = datetime.datetime.now()
current_year = now.year
current_month = now.month
current_day = now.day
date = str(current_month) + "/" + str(current_day) + "/" + str(current_year)

#adjust mac volume
try:
    os.system('osascript -e "set volume input volume 90"')
    os.system('osascript -e "set volume output volume 60"')
except:
    print "Please adjust your microphone volume."
#display variables
red = (255, 0, 0)
green = (0, 255, 0)
blue = (15, 15, 255)
yellow = (255, 255, 0)
gray = (101,111,117)
white = (255,255,255)
black = (0,0,0)
background_colour = white

score = 0
incorrectscore = 0
trycount = 0
original_length = 0
completeddict = {}
buttonresult = False
# create the basic window/screen and a title/caption
icon = pg.image.load(os.path.join("icons","headphones_globe.png"))
pg.display.set_icon(icon)

screen = pg.display.set_mode((0,0)) #full sized window mode pg.FULLSCREEN
screen.fill(background_colour)
size = screen.get_size()
w = size[0]
h = size[1]
pg.display.set_caption("RosettaTablet")
font = os.path.join("include","DidactGothic.ttf")
myfont = pg.font.Font(font, 50)
mysmallfont = pg.font.Font(font, 40)

#correct/wrong sounds and pics
sound = pg.mixer.Sound(os.path.join("include",'rails.wav'))
wrong_sound = pg.mixer.Sound(os.path.join("include",'CymbalCrash.wav'))
correct_sound = pg.mixer.Sound(os.path.join("include",'GuitarStrum.wav'))
correctpic = pg.image.load(os.path.join("icons","correct.png")).convert_alpha()
wrongpic = pg.image.load(os.path.join("icons","wrong.png")).convert_alpha()
micpic = pg.image.load(os.path.join("icons","mic.png")).convert_alpha()

# show the whole thing
pg.display.flip()

class TextRectException:
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

def render_textrect(string, rect, text_color, background_color, justification=0, font = pg.font.Font(font, 40)):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """
    word_display = string[:string.rindex(".")]
    word_siplay = download_dict_sound.replace_symbols(word_display)
    #for sym in [sym for sym in replacementsdict.keys() if sym in word_display]:
    #    word_display = word_display.replace(sym,replacementsdict[sym])
    string = word_display
    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    # Let's try to write the text out on the surface.

    surface = pg.Surface(rect.size)
    surface.fill(background_color)

    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException, "Invalid justification argument: " + str(justification)
        accumulated_height += font.size(line)[1]

    return surface

def disp(word):
    myfont = pg.font.Font(font, 40)
    label = myfont.render(word, 1, black)
    labelwidth = label.get_rect()[2]
    space_available = screen.get_size()[0] - quitbuttonbox[2] - 100
    space_indicies = []
    for pos, letter in enumerate(word):
        if letter == " ":
            space_indicies.append(pos)
    space_indicies.reverse()
    list_word = word.split(" ")
    print word, myfont.size(word)
    total_width = 0
    cursor_w = soundbutton.right
    cursor_h = 0
    wordbuttons = []
    for w in list_word:
        if cursor_w + myfont.size(w)[0] > space_available:
            cursor_w = soundbutton.right
            cursor_h = myfont.size(w)[1] - 10
        wordbuttons.append(screen.blit(myfont.render(w,1,black), (cursor_w, cursor_h)))
        cursor_w += myfont.size(w)[0] + myfont.size(" ")[0]
    return wordbuttons

def loadword(word_display, word, soundpath):
    dict_sound_files = os.listdir(os.path.abspath(dict_sounds_path))
    set_of_words = set([os.path.splitext(f)[0] for f in dict_sound_files])
    #Try to play dict_download if single word
    if " " not in word_display: #For single word
        ind_word = download_dict_sound.remove_symbols_lower(word_display)
        if ind_word not in set_of_words:
            try:#download
                download_dict_sound.download(ind_word,dict_sounds_path)
                download_dict_sound.convert_mp3_to_wav(os.path.join(dict_sounds_path,ind_word + ".mp3"))
                os.remove(os.path.join(dict_sounds_path,ind_word + ".mp3"))
                dict_sound_files = os.listdir(os.path.abspath(dict_sounds_path))
                set_of_words = set([os.path.splitext(f)[0] for f in dict_sound_files])
            except:
                print "OOPS, dowload didn't work."
        try: #Load word wav file
            wordsound = pg.mixer.music.load(os.path.join(dict_sounds_path,ind_word + ".wav"))
            print "Using Dictionary Sound"
        except: #Load 
            if sys.platform == "darwin":
                print "Using Mac Say"
                wordsound = pg.mixer.music.load(download_dict_sound.get_macsay(word_display, word))
            else:
                print "Using google speech"
                wordsound = pg.mixer.music.load(soundpath+word+"speech_google.wav")
    else: #For multiple words
        if sys.platform == "darwin":
            print "Using Mac Say"
            wordsound = pg.mixer.music.load(download_dict_sound.get_macsay(word_display, word))
        else:
            print "Using google speech"
            wordsound = pg.mixer.music.load(soundpath+word+"speech_google.wav")
    return wordsound

def display_word(word):
    myfont = pg.font.Font(font, 40)
    label = myfont.render(word, 1, black)
    labelwidth = label.get_rect()[2]
    space_available = screen.get_size()[0] - quitbuttonbox[2] - 100
    space_indicies = []
    for pos, letter in enumerate(word):
        if letter == " ":
            space_indicies.append(pos)
    space_indicies.reverse()
    line1 = word
    line2 = ""
    while labelwidth > space_available:
        line1 = word[:space_indicies[0]]
        line2 = word[space_indicies[0]:]
        line1_render = myfont.render(line1, 1, black)
        line2_render = myfont.render(line2, 1, black)
        labelwidth = line1_render.get_rect()[2]
        space_indicies.pop(0)
    else:
        line1_render = myfont.render(line1, 1, black)
        line2_render = myfont.render(line2, 1, black)
    screen.blit(line1_render, (100, 0))
    screen.blit(line2_render, (100, 41))

def text_display_word(word, choicebox):
    word_display = word[:word.rindex(".")]
    word_display = download_dict_sound.replace_symbols(word_display)
    #for sym in [sym for sym in replacementsdict.keys() if sym in word_display]:
    #    word_display = word_display.replace(sym,replacementsdict[sym])
    myfont = pg.font.Font(font, 30)
    label = myfont.render(word_display, 1, black)
    labelwidth = label.get_rect()[2]
    space_available = choicebox[2]
    space_indicies = []
    for pos, letter in enumerate(word_display):
        if letter == " ":
            space_indicies.append(pos)
    print type(choicebox[2])
    try:
        del tempsurf
    except:
        pass
    tempsurf = pg.Surface((choicebox[2],choicebox[3]))
    tempsurf.fill((255,255,255))
    line1 = word_display
    line2 = ""
    while labelwidth > space_available:
        line1 = word_display[:space_indicies[-1]]
        line2 = word_display[space_indicies[-1]:]
        line1_render = myfont.render(line1, 1, black)
        line2_render = myfont.render(line2, 1, black)
        labelwidth = line1_render.get_rect()[2]
        space_indicies.pop()
    else:
        line1_render = myfont.render(line1, 1, black)
        line2_render = myfont.render(line2, 1, black)
    tempsurf.blit(line1_render,choicebox)
    tempsurf.blit(line2_render,(choicebox[0],choicebox[1] + myfont.get_linesize(),choicebox[2],choicebox[3]))
    return tempsurf
    #return pg.Surface.blit(screen,line1_render,(choicebox[0],choicebox[1]))
    #return line1_render
def recordinput(RECORD_SECONDS = 5, WAVE_OUTPUT_FILENAME = "/tmp/input.wav"):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format = FORMAT, channels = CHANNELS, rate = RATE, input = True, frames_per_buffer = CHUNK)
    print("* recording")
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("* done recording")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def get_length(fname):
	with contextlib.closing(wave.open(fname,'r')) as f:
		frames = f.getnframes()
		rate = f.getframerate()
		duration = round(frames / float(rate))
		return duration

def playinput():
    CHUNK = 1024
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
    data = wf.readframes(CHUNK)
    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)
    stream.stop_stream()
    stream.close()
    p.terminate()

def getbestratio(boxheight,boxwidth,picheight,picwidth):
    height_ratio = float(boxheight) / float(picheight)
    width_ratio = float(boxwidth) / float(picwidth)
    picwidth *= min(width_ratio, height_ratio)
    picheight *= min(width_ratio, height_ratio)
    return int(picwidth), int(picheight)

def displayactivitychoice():
    global buttonresult
    screen.fill(background_colour)
    label1 = mysmallfont.render("Listen", 2, black,yellow)
    label2 = mysmallfont.render("Say", 2, black,yellow)
    label3 = mysmallfont.render("Read", 2, black,yellow)
    listenlabel = screen.blit(label1,[200,(h/2)-100])
    saylabel = screen.blit(label2,[500,(h/2)-100])
    readlabel = screen.blit(label3,[700,(h/2)-100])
    allfiles = [f for f in os.walk(os.path.abspath(os.path.join(unit,lesson)))]
    allwords = []
    for f in allfiles:
        allwords += f[2]
    allwords = [f[:f.rindex(".")] for f in allwords]
    allwords = "".join(allwords)
    print allwords
    if ' ' not in allwords:
        label4 = mysmallfont.render("Spell", 2, black,yellow)
        spelllabel = screen.blit(label4, [1000, (h/2) - 100])
        drawspellbutton(1000,h/2)
        wordsort = True
    else:
        wordsort = False
    del allwords
    drawmainbutton(200,h/2)
    drawpronunciationbutton(500,h/2)
    drawreadbutton(700,h/2)
    #drawquitbutton()
    drawmenubutton()
    pg.display.flip()
    looping = True
    pg.event.poll()
    while looping:
        event = pg.event.wait()
        # exit conditions --> windows titlebar x click
        if event.type == pg.QUIT:
            raise SystemExit
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            pos = pg.mouse.get_pos()
            if mainbutton.collidepoint(pos) or listenlabel.collidepoint(pos):
                buttonresult = "mainlesson"
                looping = False
                break
            if pronunciationbutton.collidepoint(pos) or saylabel.collidepoint(pos):
                buttonresult = "pronunciation"
                looping = False
                break
            if readbutton.collidepoint(pos) or readlabel.collidepoint(pos):
                buttonresult = "read"
                looping = False
                break
            if wordsort and (spelllabel.collidepoint(pos) or spellbutton.collidepoint(pos)):
                buttonresult = "spell"
                looping = False
                break
            if menubutton.collidepoint(pos):
                looping = False
                break
            #if quitbutton.collidepoint(pos):
            #    raise SystemExit
            #    break

def drawmainbutton(x,y):
    global mainbuttonpic, mainbutton
    mainbuttonpic = pg.image.load(os.path.join("icons","pictures.png")).convert_alpha()
    mainbutton = screen.blit(mainbuttonpic, [x,y])

def drawpronunciationbutton(x,y):
    global pronunciationbuttonpic, pronunciationbutton
    pronunciationbuttonpic = pg.image.load(os.path.join("icons","mic.png"))#.convert_alpha()
    pronunciationbutton = screen.blit(pronunciationbuttonpic, [x,y])

def drawreadbutton(x,y):
    global readbutton, readbuttonpic
    readbuttonpic = pg.image.load(os.path.join("icons","Icon_Text.png"))#.convert_alpha()
    readbutton = screen.blit(readbuttonpic, [x,y])

def drawspellbutton(x,y):
    global spellbuttonpic, spellbutton
    spellbuttonpic = pg.image.load(os.path.join("icons","spelling.png")).convert_alpha()
    spellbutton = screen.blit(spellbuttonpic, [x,y])

def drawquitbutton():
    global quitbuttontext,quitbuttonbox,quitbutton
    quitbuttontext = mysmallfont.render("Quit", 2, black,yellow)
    quitbutton = screen.blit(quitbuttontext, [w-quitbuttontext.get_rect()[2]-3,0])
    quitbuttonbox = pg.draw.rect(screen,black,(quitbutton.left,quitbutton.top,quitbuttontext.get_width(),quitbuttontext.get_height()),2)


def drawmenubutton():
    global menubuttontext,menubuttonbox,menubutton
    menubuttontext = mysmallfont.render("Menu", 2, black,yellow)
    menubutton = screen.blit(menubuttontext, [w-menubuttontext.get_rect()[2]-3,0])
    menubuttonbox = pg.draw.rect(screen,black,(menubutton.left,menubutton.top,menubuttontext.get_width(),menubuttontext.get_height()),2)


def drawnextbutton():
    global nextbuttontext,nextbuttonbox,nextbutton
    nextbuttontext = myfont.render("Next", 2, black, yellow)
    nextbutton = screen.blit(nextbuttontext, [(w-nextbuttontext.get_rect()[2])/2,h-nextbuttontext.get_rect()[1]-250])
    nextbuttonbox = pg.draw.rect(screen,black,(nextbutton.left,nextbutton.top,nextbuttontext.get_width(),nextbuttontext.get_height()),2)



def drawlessonstructure():
    global choicebox1, choicebox2, choicebox3,choicebox4, soundbutton, label
    screen = pg.display.set_mode((0,0)) #full sized window mode
    screen.fill(background_colour)
    size = screen.get_size()
    w = size[0]
    h = size[1]
    pg.display.set_caption("RosettaTablet")
    myfont = pg.font.Font(font, 50)
    mymedfont = pg.font.Font(font, 30)
    mysmallfont = pg.font.Font(font, 40)
    scorelabel = mymedfont.render("Score: " + str(score), 2, black)
    boxsize = scorelabel.get_rect()
    scoreXpos = (w - boxsize[2])-30
    scoreYpos = quitbuttonbox[3]
    screen.blit(scorelabel,[scoreXpos,scoreYpos])
    titlebox = pg.draw.rect(screen, black, (0,0,w,100), 3)
    choicebox1 = pg.draw.rect(screen, black, (0,100,(w)/2,(h-200)/2), 3)
    choicebox2 = pg.draw.rect(screen, black, (w/2,100,(w)/2,(h-200)/2), 3)
    choicebox3 = pg.draw.rect(screen, black, (0,((h-200)/2)+100,(w)/2,(h-200)/2), 3)
    choicebox4 = pg.draw.rect(screen, black, (w/2,((h-200)/2)+100,(w)/2,(h-200)/2), 3)
    soundpic = pg.image.load(os.path.join("icons",'sound.png'))
    soundbutton = screen.blit(soundpic, (0,0))
    pg.display.flip()

def pronunciationpractice(lesson):
    print unit, str(lesson)
    global pronunciationbuttonpic, pronunciationbutton, menupushed, soundbutton
    menupushed = False
    screen.fill(background_colour)
    soundpic = pg.image.load(os.path.join("icons",'sound.png'))
    recorddot = pg.image.load(os.path.join("icons",'recorddot.png'))
    drawnextbutton()
    drawpronunciationbutton(w-200,h/2)
    #lesson = "emotions" #temporary lesson variable before getting sreen picked
    listofpics = [f for f in listdir(os.path.join("Units",unit,lesson,"pics")) if isfile(os.path.join("Units",unit,lesson,"pics",f))]
    #listofpics = [f for f in listdir(unit + "/" + lesson+"/pics/") if isfile(join(unit + "/" + lesson+"/pics/",f))] #pictures in lesson/pics/ folder
    original_length = len(listofpics)
    random.shuffle(listofpics) #shuffle order of lesson
    picpath = os.path.join("Units",unit,lesson,"pics")
    #picpath = unit + "/" + lesson+"/pics/"
    soundpath = os.path.join("Units",unit,lesson,"sounds")
    #soundpath = unit + "/" + lesson+"/sounds/"
    count_originals = 0
    for pic in listofpics:
        print pic
        screen.fill(background_colour)
        soundbutton = screen.blit(soundpic, (0,0))
        drawnextbutton()
        drawpronunciationbutton(w-200,h/2)
        answer = pic
        word = answer[:answer.rindex(".")]
        word_display = word#.replace(".questionmark","?")
        word_display = download_dict_sound.replace_symbols(word_display)
        #for sym in [sym for sym in replacementsdict.keys() if sym in word_display]:
        #    word_display = word_display.replace(sym,replacementsdict[sym])
        loadword(word_display, word, soundpath)
        #display_word(word_display)
        wordbuttons = disp(word_display)
        #drawquitbutton()
        drawmenubutton()
        picimage = pg.image.load(os.path.join(picpath,pic))
        picimage = pg.transform.smoothscale(picimage, getbestratio(screen.get_size()[1]-350,screen.get_size()[0]-350,float(picimage.get_size()[1]),float(picimage.get_size()[0]))) #(screenheight, screenwidht, picheight, picwidth)
        screen.blit(picimage,[5,100])
        #play word sound
        pg.display.flip()
        pg.mixer.music.play(0)
        #Figure out what to do with click event handler
        looping = True
        pg.event.poll()
        while looping:
            event = pg.event.wait()
            # exit conditions --> windows titlebar x click
            if event.type == pg.QUIT:
                raise SystemExit
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                pos = pg.mouse.get_pos()
                for individual_word in wordbuttons:
                    if individual_word.collidepoint(pos):
                        ind_word = word_display.split(" ")[wordbuttons.index(individual_word)]
                        print ind_word
                        try:
                            loadword(ind_word, ind_word, soundpath)
                            pg.mixer.music.play()
                            while pg.mixer.music.get_busy():
                                pg.time.wait(10)
                        except:
                            print "OOOOPS, loading/download didn't work"
                        wordsound = pg.mixer.music.load(os.path.join(soundpath,word+"speech_google.wav"))
                if soundbutton.collidepoint(pos): #Sound button is pressed
                    loadword(word_display, word, soundpath)
                    pg.mixer.music.play(0)
                    while pg.mixer.get_busy():
                        pg.time.wait(10)
                if pronunciationbutton.collidepoint(pos):
                    pg.draw.rect(screen,background_colour,(pronunciationbutton.left,pronunciationbutton.top,150,150),0)
                    pronunciationbuttonpic = pg.image.load(os.path.join("icons","recorddot.png")).convert_alpha()
                    pronunciationbutton = screen.blit(pronunciationbuttonpic, [w-200,h/2])
                    pg.display.update()
                    try:
                        print os.path.join(soundpath,word+"speech_google.wav"), str(get_length(os.path.join(soundpath,word+"speech_google.wav")) * 2)
                        recordinput(RECORD_SECONDS = get_length(os.path.join(soundpath,word+"speech_google.wav")) * 2)
                        print "Using recordinput"
                    except:
                        os.system("rec -c 2 /tmp/voice.aiff trim 0 00:05")
                        print "Using SoX"
                    pg.draw.rect(screen,background_colour,(pronunciationbutton.left,pronunciationbutton.top,150,150),0)
                    drawpronunciationbutton(w-200,h/2)
                    pg.display.update()
                    loadword(word_display, word, soundpath)
                    pg.mixer.music.play(0)
                    while pg.mixer.get_busy():
                        pg.time.wait(10)
                    try:
                        playinput()
                    except:
                        os.system("play /tmp/voice.aiff")
                elif menubutton.collidepoint(pos):
                    looping = False
                    lessonon = False
                    menupushed = True
                    break
                if nextbutton.collidepoint(pos):
                    looping = False
                    break
        if menupushed == True:
            break

def mainlesson(lesson):
    global scorelabel, score, incorrectscore, trycount, original_length, missed, menupushed
    menupushed = False
    missed = []
    score = 0
    incorrectscore = 0
    #lesson = "emotions" #temporary lesson variable before getting screen picked
    #listofpics = [f for f in listdir(unit + "/" + lesson+"/pics/") if isfile(join(unit + "/" + lesson+"/pics/",f))] #pictures in unit/lesson/pics/ folder
    #original_length = len(listofpics)
    #random.shuffle(listofpics) #shuffle order of lesson
    #picpath = unit + "/" + lesson+"/pics/"
    #soundpath = unit + "/" + lesson+"/sounds/"
    listofpics = [f for f in listdir(os.path.join("Units",unit,lesson,"pics")) if isfile(os.path.join("Units",unit,lesson,"pics",f))]
    #listofpics = [f for f in listdir(unit + "/" + lesson+"/pics/") if isfile(join(unit + "/" + lesson+"/pics/",f))] #pictures in lesson/pics/ folder
    original_length = len(listofpics)
    random.shuffle(listofpics) #shuffle order of lesson
    picpath = os.path.join("Units",unit,lesson,"pics")
    #picpath = unit + "/" + lesson+"/pics/"
    soundpath = os.path.join("Units",unit,lesson,"sounds")
    #soundpath = unit + "/" + lesson+"/sounds/"
    
    count_originals = 0
    for pic in listofpics:
        trycount = 0
        count_originals += 1
        drawlessonstructure()
        answer = pic
        word = answer[:answer.rindex(".")]
        word_display = word
        word_display = download_dict_sound.replace_symbols(word_display)
        #for sym in [sym for sym in replacementsdict.keys() if sym in word_display]:
        #    word_display = word_display.replace(sym,replacementsdict[sym])
        loadword(word_display, word, soundpath)
        choices = ["","","",""]
        choices[0] = answer #choiceX = answer ... we don't know which choice number it is
        #if choices[0] gets clicked and trycount == 0, add to score, move to next pic
        #if [choices[1],choices[2], choices[3]] get clicked, trycount += 1, play word again, wait for click, append to end of list?
        choices[1] = random.choice([x for x in listofpics if x != choices[0]])
        choices[2] = random.choice([x for x in listofpics if x not in [choices[0],choices[1]]])
        choices[3] = random.choice([x for x in listofpics if x not in [choices[0],choices[1],choices[2]]])
        #Load pictures, scale and match to choiceboxes surfaces
        randomindex = [0,1,2,3]
        random.shuffle(randomindex)#mixing up the placement of the answer
        choice1 = choices[randomindex[0]]
        choice2 = choices[randomindex[1]]
        choice3 = choices[randomindex[2]]
        choice4 = choices[randomindex[3]]
        pic1 = pg.image.load(os.path.join(picpath,choice1))
        pic2 = pg.image.load(os.path.join(picpath,choice2))
        pic3 = pg.image.load(os.path.join(picpath,choice3))
        pic4 = pg.image.load(os.path.join(picpath,choice4))
        pics = [pic1,pic2,pic3,pic4]
        #scale pictures to max size without stretching
        pic1 = pg.transform.smoothscale(pic1, getbestratio((float(choicebox1[3]-5)),float(choicebox1[2]-5),float(pic1.get_size()[1]),float(pic1.get_size()[0])))
        pic2 = pg.transform.smoothscale(pic2, getbestratio((float(choicebox1[3]-5)),float(choicebox1[2]-5),float(pic2.get_size()[1]),float(pic2.get_size()[0])))
        pic3 = pg.transform.smoothscale(pic3, getbestratio((float(choicebox1[3]-5)),float(choicebox1[2]-5),float(pic3.get_size()[1]),float(pic3.get_size()[0])))
        pic4 = pg.transform.smoothscale(pic4, getbestratio((float(choicebox1[3]-5)),float(choicebox1[2]-5),float(pic4.get_size()[1]),float(pic4.get_size()[0])))
        #match to choiceboxes surfaces
        surf1 = pg.Surface.blit(screen,pic1,choicebox1)
        surf2 = pg.Surface.blit(screen,pic2,choicebox2)
        surf3 = pg.Surface.blit(screen,pic3,choicebox3)
        surf4 = pg.Surface.blit(screen,pic4,choicebox4)
        pics = [pic1,pic2,pic3,pic4]
        surfs = [surf1,surf2,surf3,surf4]
        #display_word(word_display)
        wordbuttons = disp(word_display)
        drawmenubutton()
        #play word sound
        pg.display.flip()
        pg.mixer.music.play(0)
        #Figure out what to do with click event handler
        looping = True
        pg.event.poll()
        while looping:
            event = pg.event.wait()
            # exit conditions --> windows titlebar x click
            if event.type == pg.QUIT:
                raise SystemExit
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                pos = pg.mouse.get_pos()
                for individual_word in wordbuttons:
                    if individual_word.collidepoint(pos):
                        ind_word = word_display.split(" ")[wordbuttons.index(individual_word)]
                        print ind_word
                        try:
                            loadword(ind_word, ind_word, soundpath)
                            pg.mixer.music.play()
                            while pg.mixer.music.get_busy():
                                pg.time.wait(10)
                        except:
                            print "OOOOPS, loading/download didn't work"
                        loadword(word_display, word, soundpath)
                if soundbutton.collidepoint(pos): #Sound button is pressed
                    pg.mixer.music.play(0)
                #Wrong answer is clicked
                elif surfs[randomindex.index(1)].collidepoint(pos) or surfs[randomindex.index(2)].collidepoint(pos) or surfs[randomindex.index(3)].collidepoint(pos):
                    screen.blit(wrongpic,[(w-wrongpic.get_rect()[2]-150),0])
                    pg.display.flip()
                    missed.append(word_display)
                    wrong_sound.play()
                    pg.mixer.music.play(0)
                    trycount += 1
                #Right answer is clicked
                elif surfs[randomindex.index(0)].collidepoint(pos):
                    correct_sound.play()
                    screen.fill(background_colour)
                    wordsound = pg.mixer.music.load(os.path.join(soundpath,word+"speech_google.wav"))
                    display_word(word_display)
                    screen.blit(pics[randomindex.index(0)],[(w - pics[randomindex.index(0)].get_rect()[2])/2,(h- pics[randomindex.index(0)].get_rect()[1])/2])
                    pg.display.flip()
                    pg.mixer.music.play(0)
                    while pg.mixer.music.get_busy():
                        pg.time.wait(10)
                    pg.time.wait(2000)
                    looping = False
                    break
                elif menubutton.collidepoint(pos):
                    looping = False
                    lessonon = False
                    menupushed = True
                    break
        if menupushed == True:
            break
        if trycount == 0 and count_originals <= original_length:
            score +=1
        elif trycount > 0:
            incorrectscore += 1
            listofpics.append(pic) #review picture if you got it wrong

def text_only_lesson(lesson):
    global scorelabel, score, incorrectscore, trycount, original_length, missed, menupushed
    menupushed = False
    missed = []
    score = 0
    incorrectscore = 0
    #lesson = "emotions" #temporary lesson variable before getting screen picked
    listofpics = [f for f in listdir(os.path.join("Units",unit,lesson,"pics")) if isfile(os.path.join("Units",unit,lesson,"pics",f))]
    #listofpics = [f for f in listdir(unit + "/" + lesson+"/pics/") if isfile(join(unit + "/" + lesson+"/pics/",f))] #pictures in lesson/pics/ folder
    original_length = len(listofpics)
    random.shuffle(listofpics) #shuffle order of lesson
    picpath = os.path.join("Units",unit,lesson,"pics")
    #picpath = unit + "/" + lesson+"/pics/"
    soundpath = os.path.join("Units",unit,lesson,"sounds")
    #soundpath = unit + "/" + lesson+"/sounds/"

    count_originals = 0
    for pic in listofpics:
        trycount = 0
        count_originals += 1
        drawlessonstructure()
        answer = pic
        word = answer[:answer.rindex(".")]
        word_display = word
        word_display = download_dict_sound.replace_symbols(word_display)
        #for sym in [sym for sym in replacementsdict.keys() if sym in word_display]:
        #    word_display = word_display.replace(sym,replacementsdict[sym])
        loadword(word_display, word, soundpath)
        choices = ["","","",""]
        choices[0] = answer #choiceX = answer ... we don't know which choice number it is
        #if choices[0] gets clicked and trycount == 0, add to score, move to next pic
        #if [choices[1],choices[2], choices[3]] get clicked, trycount += 1, play word again, wait for click, append to end of list?
        choices[1] = random.choice([x for x in listofpics if x != choices[0]])
        choices[2] = random.choice([x for x in listofpics if x not in [choices[0],choices[1]]])
        choices[3] = random.choice([x for x in listofpics if x not in [choices[0],choices[1],choices[2]]])
        #Load pictures, scale and match to choiceboxes surfaces
        randomindex = [0,1,2,3]
        random.shuffle(randomindex)#mixing up the placement of the answer
        choice1 = choices[randomindex[0]]
        choice2 = choices[randomindex[1]]
        choice3 = choices[randomindex[2]]
        choice4 = choices[randomindex[3]]
        pic1 = pg.image.load(os.path.join(picpath,choice1))
        pic2 = pg.image.load(os.path.join(picpath,choice2))
        pic3 = pg.image.load(os.path.join(picpath,choice3))
        pic4 = pg.image.load(os.path.join(picpath,choice4))
        pics = [pic1,pic2,pic3,pic4]
        #scale pictures to max size without stretching
        pic1 = pg.transform.smoothscale(pic1, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic1.get_size()[1]),float(pic1.get_size()[0])))
        pic2 = pg.transform.smoothscale(pic2, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic2.get_size()[1]),float(pic2.get_size()[0])))
        pic3 = pg.transform.smoothscale(pic3, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic3.get_size()[1]),float(pic3.get_size()[0])))
        pic4 = pg.transform.smoothscale(pic4, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic4.get_size()[1]),float(pic4.get_size()[0])))
        #render choice text
        #txt1 = text_display_word(choice1,choicebox1)
        txt1 = render_textrect(download_dict_sound.replace_symbols(choice1), pg.Rect(choicebox1[0],choicebox1[1],choicebox1[2]-3,choicebox1[3]-3), (0, 0, 0), (255, 255, 255))
        surf1 = screen.blit(txt1, choicebox1.topleft)
        #surf1 = pg.Surface.blit(screen,txt1,choicebox1.topleft)
        txt2 = render_textrect(download_dict_sound.replace_symbols(choice2), pg.Rect(choicebox2[0],choicebox2[1],choicebox2[2]-3,choicebox2[3]-3), (0, 0, 0), (255, 255, 255))
        surf2 = pg.Surface.blit(screen,txt2,choicebox2.topleft)
        txt3 = render_textrect(download_dict_sound.replace_symbols(choice3), pg.Rect(choicebox3[0],choicebox3[1],choicebox3[2]-3,choicebox3[3]-3), (0, 0, 0), (255, 255, 255))
        surf3 = pg.Surface.blit(screen,txt3,choicebox3.topleft)
        txt4 = render_textrect(download_dict_sound.replace_symbols(choice4), pg.Rect(choicebox4[0],choicebox4[1],choicebox4[2]-3,choicebox4[3]-3), (0, 0, 0), (255, 255, 255))
        surf4 = pg.Surface.blit(screen,txt4,choicebox4.topleft)
        #match to choiceboxes surfaces
        pics = [pic1,pic2,pic3,pic4]
        surfs = [surf1,surf2,surf3,surf4]
        #display_word(word_display) #Don't display word for text-only
        drawmenubutton()
        #play word sound
        pg.display.flip()
        pg.mixer.music.play(0)
        #Figure out what to do with click event handler
        looping = True
        pg.event.poll()
        while looping:
            event = pg.event.wait()
            # exit conditions --> windows titlebar x click
            if event.type == pg.QUIT:
                raise SystemExit
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                pos = pg.mouse.get_pos()
                if soundbutton.collidepoint(pos): #Sound button is pressed
                    pg.mixer.music.play(0)
                #Wrong answer is clicked
                elif surfs[randomindex.index(1)].collidepoint(pos) or surfs[randomindex.index(2)].collidepoint(pos) or surfs[randomindex.index(3)].collidepoint(pos):
                    screen.blit(wrongpic,[(w-wrongpic.get_rect()[2]-150),0])
                    pg.display.flip()
                    missed.append(word_display)
                    wrong_sound.play()
                    pg.mixer.music.play(0)
                    trycount += 1
                #Right answer is clicked
                elif surfs[randomindex.index(0)].collidepoint(pos):
                    correct_sound.play()
                    screen.fill(background_colour)
                    wordsound = pg.mixer.music.load(os.path.join(soundpath,word+"speech_google.wav"))
                    display_word(word_display)
                    screen.blit(pics[randomindex.index(0)],[(w - pics[randomindex.index(0)].get_rect()[2])/2,(h- pics[randomindex.index(0)].get_rect()[1])/2])
                    pg.display.flip()
                    pg.mixer.music.play(0)
                    while pg.mixer.music.get_busy():
                        pg.time.wait(10)
                    looping = False
                    break
                elif menubutton.collidepoint(pos):
                    looping = False
                    lessonon = False
                    menupushed = True
                    break
        if menupushed == True:
            break
        if trycount == 0 and count_originals <= original_length:
            score +=1
        elif trycount > 0:
            incorrectscore += 1
            listofpics.append(pic) #review picture if you got it wrong

    #display score screen after for loop is finished
def displayscore(lesson):
    global scorelabel,w,h, score,incorrectscore, completeddict, repeatpic
    print set(missed)
    screen.fill(white)
    datebox = pg.draw.rect(screen, black, (0,100,(w)/4,100), 3)
    unitbox = pg.draw.rect(screen, black, ((w)/4,100,(w)/4,100), 3)
    lessonbox = pg.draw.rect(screen, black, ((w)/2,100,(w)/4,100), 3)
    scorebox = pg.draw.rect(screen, black, (3*(w)/4,100,(w)/4,100), 3)
    datelabel = mysmallfont.render(str(date), 2, black)
    columnlabels = [mysmallfont.render("Date: ", 2, black),mysmallfont.render("Unit: ", 2, black),mysmallfont.render("Lesson: ", 2, black),mysmallfont.render("Score: ", 2, black)]
    for column in columnlabels:
        dist = (w/4)*(columnlabels.index(column))
        screen.blit(column, [dist+10,50])
    boxtexts = [mysmallfont.render(str(date), 2, black),mysmallfont.render(unit, 2, black),mysmallfont.render(lesson, 2, black),mysmallfont.render(str(int((float(score) / float(original_length))*100))+" %", 2, black)]
    for box in boxtexts:
        dist = (w/4)*(boxtexts.index(box))
        screen.blit(box, [dist+10,100])
    chooselessonpic = pg.image.load(os.path.join("icons","next.png")).convert_alpha()
    chooselessonbuttontext = mysmallfont.render("Choose a lesson", 2, black)
    chooselessonbuttonbox = pg.draw.rect(screen,gray,((w/2)-(chooselessonbuttontext.get_rect()[2]/2)-3,h-200-3,chooselessonbuttontext.get_width()+6,chooselessonbuttontext.get_height()+6),0)
    chooselessonbutton = screen.blit(chooselessonbuttontext, [(w/2)-(chooselessonbuttontext.get_rect()[2]/2),h-200])
    repeatlessonbuttontext = mysmallfont.render("Repeat", 2, black)
    repeatlessonbuttonbox = pg.draw.rect(screen,gray,((w/2)-(repeatlessonbuttontext.get_rect()[2]/2)-3,h-200-3-65,repeatlessonbuttontext.get_width()+6,repeatlessonbuttontext.get_height()+6),0)
    repeatlessonbutton = screen.blit(repeatlessonbuttontext, [(w/2)-(repeatlessonbuttontext.get_rect()[2]/2),h-200-65])
    repeatpic = pg.image.load(os.path.join("icons","repeat.png")).convert_alpha()
    pencilpic = pg.image.load(os.path.join("icons","pencil.png")).convert_alpha()
    screen.blit(pencilpic, [w/2,h/2])
    nex = screen.blit(chooselessonpic, [chooselessonbuttonbox[0]-75,chooselessonbuttonbox[1]-3])
    rep = screen.blit(repeatpic, [repeatlessonbuttonbox[0]-75,repeatlessonbuttonbox[1]-3])
    drawquitbutton()
    pg.display.flip()
    completeddict[lesson] = int((float(score) / float(original_length))*100)
    looping = True
    pg.event.poll()
    while looping:
        event = pg.event.wait()
        # exit conditions --> windows titlebar x click
        if event.type == pg.QUIT:
            raise SystemExit
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            pos = pg.mouse.get_pos()
            if quitbutton.collidepoint(pos):
                raise SystemExit
            if repeatlessonbuttonbox.collidepoint(pos) or rep.collidepoint(pos):
                mainlesson(lesson)
                displayscore(lesson)
            if chooselessonbuttonbox.collidepoint(pos) or nex.collidepoint(pos):
                looping = False
                break

#display Lessons Menu
def unitmenu():
    global completeddict, buttonresult
    screen = pg.display.set_mode((0,0)) #full sized window mode
    screen.fill(background_colour)
    size = screen.get_size()
    w = size[0]
    h = size[1]
    pg.display.set_caption("RosettaTablet")
    myfont = pg.font.Font(font, 50)#formerly SysFont
    mysmallfont = pg.font.Font(font, 40)
    global unit
    uniton = True
    screen.fill(background_colour)
    listoffolders = [f for f in listdir(os.path.abspath("Units")) if isfile(os.path.join(os.path.abspath("Units"),f)) == False and f not in ["examplelesson","exampleunit","Test","RosettaTablet.app", ".git", "sounds", "extras"]]
    listoffolderlables = [screen.blit(mysmallfont.render(str(listoffolders.index(folder)+1)+". "+folder.title(), 1, black),[20,45*listoffolders.index(folder)]) for folder in listoffolders]
    drawquitbutton()
    pg.display.flip()
    pg.event.poll()
    while uniton:
        event = pg.event.wait()
        if event.type == pg.QUIT:
            raise SystemExit
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            pos = pg.mouse.get_pos()
            if quitbutton.collidepoint(pos):
                raise SystemExit
            for folder in listoffolderlables:
                if folder.collidepoint(pos):
                    unit = listoffolders[listoffolderlables.index(folder)]
                    print unit
                    lessonmenu(os.path.join("Units", unit))
                    pg.display.quit
                    return os.path.join("Units", unit)

def spell(lesson):
    global soundbutton, menupushed
    menupushed = False
    fontsize = 120
    mysmallfont = pg.font.Font('DidactGothic.ttf',fontsize)
    mysmallerfont = pg.font.Font('DidactGothic.ttf',60)
    screen = pg.display.set_mode((0,0)) #full sized window mode
    screen.fill(background_colour)
    size = screen.get_size()
    w = size[0]
    h = size[1]
    pg.display.set_caption("RosettaTablet")
    soundpic = pg.image.load(os.path.join("icons",'sound.png'))
    soundbutton = screen.blit(soundpic, (0,0))
    drawmenubutton()
    pg.display.flip
    def display_word(word):
        screen.fill(white)
        drawmenubutton()
        repeatpicbutton = screen.blit(soundpic, (300,300))
        word = word.lower()
        letters = list(word)
        spacing = 0
        for pos, letter in enumerate(list(correct_word)):
            color = black
            if pos == 0:
                spacing = 0
            else:
                spacing += mysmallfont.render(list(correct_word)[pos-1],True,color).get_width()
            pg.draw.line(screen, black, (spacing+6,fontsize+10),(spacing+mysmallfont.render(letter,True,color).get_width()+1,fontsize+10),3)
        pg.display.update()
        for pos, letter in enumerate(letters):
            #if letter in ["a","e","i","o","u"]:
            #   color = blue
            #else:
            #   color = black
            if letter == correct_word[pos]:
                color = black
            else:
                color = red
                trouble_words.append(correct_word)
            if pos == 0:
                spacing = 0
            else:
                spacing += mysmallfont.render(letters[pos-1],True,color).get_width()
            screen.blit(mysmallfont.render(letter,True,color),(spacing+5,3))
            pg.display.update()
    def playword(word, soundpath):
        print word
        loadword(word, word, soundpath)
        pg.mixer.music.play()

    def drawshowcorrectbutton():
        global showcorrectbutton, showcorrect
        showcorrect = mysmallerfont.render("Show Correct",False,black)
        showcorrectbutton = screen.blit(showcorrect, (50,200))

    def drawbadbutton():
        global badbutton, bad
        bad = mysmallerfont.render("Bad",False,black)
        badbutton = screen.blit(bad, (50,300))

    def showcorrectword(correct_word):
        display_word(correct_word)

    def showtrouble_words(trouble_words):
        screen.fill(white)
        drawmenubutton()
        print trouble_words
        trouble_words = list(set(trouble_words))
        try:
            trouble_word.sort()
        except:
            print "Not enough mistakes"
        mysmallfont = pg.font.Font(font, 50)
        screen.blit(mysmallfont.render('Study:', 1, black),[20,10])
        listoftrouble_words_lables = [screen.blit(mysmallfont.render(tw.lower(), 1, black),[30,100 + 55*trouble_words.index(tw)]) for tw in trouble_words]
        pg.display.update()
        looping = True
        pg.event.poll()
        while looping:
            event = pg.event.wait()
            #for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                pos = pg.mouse.get_pos()
                if menubutton.collidepoint(pos):
                    looping = False
                    lessonon = False
                    menupushed = True
                    break

    keys = [pg.K_a,pg.K_b,pg.K_c,pg.K_d,pg.K_e,pg.K_f,pg.K_g,pg.K_h,pg.K_i,pg.K_j,pg.K_k,pg.K_l,pg.K_m,pg.K_n,pg.K_o,pg.K_p,pg.K_q,pg.K_r,pg.K_s,pg.K_t,pg.K_u,pg.K_v,pg.K_w,pg.K_x,pg.K_y,pg.K_z,pg.K_QUOTE, pg.K_MINUS]
    badwords = []
    trouble_words = []
    menupushed = False
    missed = []
    score = 0
    incorrectscore = 0
    #lesson = "emotions" #temporary lesson variable before getting screen picked
    #listofpics = [f for f in listdir(unit + "/" + lesson+"/pics/") if isfile(join(unit + "/" + lesson+"/pics/",f))] #pictures in unit/lesson/pics/ folder
    #original_length = len(listofpics)
    #random.shuffle(listofpics) #shuffle order of lesson
    #picpath = unit + "/" + lesson+"/pics/"
    #soundpath = unit + "/" + lesson+"/sounds/"
    listofpics = [f for f in listdir(os.path.join("Units",unit,lesson,"pics")) if isfile(os.path.join("Units",unit,lesson,"pics",f))]
    #listofpics = [f for f in listdir(unit + "/" + lesson+"/pics/") if isfile(join(unit + "/" + lesson+"/pics/",f))] #pictures in lesson/pics/ folder
    original_length = len(listofpics)
    random.shuffle(listofpics) #shuffle order of lesson
    picpath = os.path.join("Units",unit,lesson,"pics")
    #picpath = unit + "/" + lesson+"/pics/"
    soundpath = os.path.join("Units",unit,lesson,"sounds")
    #soundpath = unit + "/" + lesson+"/sounds/"
    count_originals = 0
    word_list = [x[:x.rfind(".")] for x in listofpics]
    for word in word_list:
        word_sound_file = word
        word = download_dict_sound.replace_symbols(word)
        #for sym in [sym for sym in replacementsdict.keys() if sym in word]:
        #    word = word.replace(sym,replacementsdict[sym])
        screen.fill(white)
        repeatpicbutton = screen.blit(soundpic, (300,300))
        correct_word = word
        typedword = ""
        #playword(word_sound_file, soundpath)
        loadword(word, word, soundpath)
        pg.mixer.music.play()
        while pg.mixer.music.get_busy():
            pg.time.wait(10)
        display_word(typedword)
        drawshowcorrectbutton()
        #drawbadbutton()
        pg.display.update()
        looping = True
        pg.event.poll()
        while looping:

            if typedword == correct_word.lower():
                screen.fill(white)
                screen.blit(mysmallfont.render("Good job!", True, black),(30,30))
                screen.blit(mysmallfont.render(typedword,True,black),(100,150))
                pg.display.update()
                correct_sound.play()
                pg.time.wait(2000)
                break
            event = pg.event.wait()
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                pos = pg.mouse.get_pos()
                if repeatpicbutton.collidepoint(pos): #Sound button is pressed
                    playword(word_sound_file, soundpath)
                elif showcorrectbutton.collidepoint(pos):
                    showcorrectword(correct_word)
                    trouble_words.append(correct_word)
                    pg.time.wait(3000)
                    display_word(typedword)
                #elif badbutton.collidepoint(pos):
                    #badwords.append(correct_word)
                elif menubutton.collidepoint(pos):
                    looping = False
                    lessonon = False
                    menupushed = True
                    break
            elif event.type == pg.KEYDOWN:
                print event.key
                if event.key in keys and len(typedword) < len(correct_word):
                    typedword += chr(event.key)
                    display_word(typedword)
                    drawshowcorrectbutton()
                    #drawbadbutton()
                    pg.display.update()
                if event.key == pg.K_BACKSPACE:
                    typedword = typedword[:-1]
                    screen.fill(white)
                    repeatpicbutton = screen.blit(soundpic, (300,300))
                    drawshowcorrectbutton()
                    #drawbadbutton()
                    pg.display.update()
                    pg.display.flip()
                    display_word(typedword)
        if menupushed:
            break
    #print badwords
    print trouble_words
    if not menupushed and len(trouble_words) > 0:
        showtrouble_words(trouble_words)

def lessonmenu(unit):
    global completeddict, buttonresult,lessonon
    screen = pg.display.set_mode((0,0)) #full sized window mode
    screen.fill(background_colour)
    size = screen.get_size()
    w = size[0]
    h = size[1]
    pg.display.set_caption("RosettaTablet")
    myfont = pg.font.Font(font, 50)
    mysmallfont = pg.font.Font(font, 40)
    global lesson
    lessonon = True
    screen.fill(background_colour)
    mysmallfont = pg.font.Font(font, 40)
    listoffolders = [f for f in listdir(unit) if isfile(os.path.join(unit,f)) == False]
    try:
        listoffolders.remove("examplelesson") #remove blank lesson from menu
    except:
        pass
    listoffolderlables = [screen.blit(mysmallfont.render(str(listoffolders.index(folder)+1)+". "+folder.title(), 1, black),[20,45*listoffolders.index(folder)]) for folder in listoffolders]
    #drawquitbutton()
    drawmenubutton()
    pg.display.flip()
    completedlessons = completeddict.keys()
    print "Completed Lessons:",completedlessons
    pg.event.poll()
    while lessonon:
        event = pg.event.wait()
        if event.type == pg.QUIT:
            raise SystemExit
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            pos = pg.mouse.get_pos()
            #if quitbutton.collidepoint(pos):
            #    raise SystemExit
            if menubutton.collidepoint(pos):
                lessonon = False
                break
            for folder in listoffolderlables:
                if folder.collidepoint(pos):
                    lesson = listoffolders[listoffolderlables.index(folder)]
                    print lesson
                    displayactivitychoice()
                    pg.display.quit
                    return lesson

#pronunciationpractice("emotions")
while True:
    unitmenu()
    if lessonon == True:
        if buttonresult == "mainlesson":
            mainlesson(lesson)
            if menupushed == False:
                displayscore(lesson)
        elif buttonresult == "read":
            text_only_lesson(lesson)
            if menupushed == False:
                displayscore(lesson)
        elif buttonresult == "pronunciation":
            pronunciationpractice(lesson)
        elif buttonresult == "spell":
            spell(lesson)
        else:
            unitmenu()
    else:
        unitmenu()


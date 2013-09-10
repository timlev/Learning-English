#!/usr/bin/env python2.7

#clocks was made by afconvert
#Unit1 Daily Actions will be made by mplayer

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
except:
    print "Ooops ... no pyaudio or wave ... Say will try SoX"
import glob
import platform
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
pg.event.set_allowed(None)
pg.event.set_allowed([pg.QUIT, pg.MOUSEBUTTONDOWN])
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
screen = pg.display.set_mode((0,0)) #full sized window mode pg.FULLSCREEN
screen.fill(background_colour)
size = screen.get_size()
w = size[0]
h = size[1]
pg.display.set_caption("RosettaTablet")
font = "DidactGothic.ttf"
myfont = pg.font.Font(font, 50)
mysmallfont = pg.font.Font(font, 40)

#correct/wrong sounds and pics
sound = pg.mixer.Sound('rails.wav')
wrong_sound = pg.mixer.Sound('CymbalCrash.wav')
correct_sound = pg.mixer.Sound('GuitarStrum.wav')
correctpic = pg.image.load("correct.png").convert_alpha()
wrongpic = pg.image.load("wrong.png").convert_alpha()
micpic = pg.image.load("mic.png").convert_alpha()

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
    for sym in [sym for sym in replacementsdict.keys() if sym in word_display]:
        word_display = word_display.replace(sym,replacementsdict[sym])
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
    for sym in [sym for sym in replacementsdict.keys() if sym in word_display]:
        word_display = word_display.replace(sym,replacementsdict[sym])
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
def recordinput():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 5
    global WAVE_OUTPUT_FILENAME
    WAVE_OUTPUT_FILENAME = "/tmp/input.wav"
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
    label1 = mysmallfont.render("Listen", 2, black)
    label2 = mysmallfont.render("Say", 2, black)
    label3 = mysmallfont.render("Read", 2, black)
    listen_width, listen_height = 100, h/2
    say_width, say_height = listen_width + 300, h/2
    read_width, read_height = say_width + 200, h/2
    listenlabel = screen.blit(label1,[listen_width,listen_height-100])
    saylabel = screen.blit(label2,[say_width,listen_height-100])
    readlabel = screen.blit(label3,[read_width,listen_height-100])
    drawmainbutton(listen_width,h/2)
    drawpronunciationbutton(say_width,h/2)
    drawreadbutton(read_width,h/2)
    drawmenubutton()
    pg.display.flip()
    looping = True
    while looping:
        for event in pg.event.get():
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
                if menubutton.collidepoint(pos):
                    looping = False
                    break
                #if quitbutton.collidepoint(pos):
                #    raise SystemExit
                #    break

def drawmainbutton(x,y):
    global mainbuttonpic, mainbutton
    mainbuttonpic = pg.image.load("pictures.png").convert_alpha()
    mainbutton = screen.blit(mainbuttonpic, [x,y])

def drawpronunciationbutton(x,y):
    global pronunciationbuttonpic, pronunciationbutton
    pronunciationbuttonpic = pg.image.load("mic.png")#.convert_alpha()
    pronunciationbutton = screen.blit(pronunciationbuttonpic, [x,y])

def drawreadbutton(x,y):
    global readbutton, readbuttonpic
    readbuttonpic = pg.image.load("Icon_Text.png")#.convert_alpha()
    readbutton = screen.blit(readbuttonpic, [x,y])

def drawquitbutton():
    global quitbuttontext,quitbuttonbox,quitbutton
    quitbuttontext = mysmallfont.render("Quit", 2, black)
    quitbuttonbox = pg.draw.rect(screen,white,((w-quitbuttontext.get_rect()[2])-3,0,quitbuttontext.get_width()+6,quitbuttontext.get_height()+6),0)
    quitbutton = screen.blit(quitbuttontext, [w-quitbuttontext.get_rect()[2]-3,0])

def drawmenubutton():
    global menubuttontext,menubuttonbox,menubutton
    menubuttontext = mysmallfont.render("Menu", 2, black)
    menubuttonbox = pg.draw.rect(screen,white,(w-menubuttontext.get_width()-3,0,menubuttontext.get_width()+6,menubuttontext.get_height()+6),0)
    menubutton = screen.blit(menubuttontext, [w-menubuttontext.get_rect()[2]-3,0])

def drawnextbutton():
    global nextbuttontext,nextbuttonbox,nextbutton
    nextbuttontext = mysmallfont.render("Next", 2, black)
    nextbuttonbox = pg.draw.rect(screen,white,((w-nextbuttontext.get_rect()[2])-3,0,nextbuttontext.get_width()+6,nextbuttontext.get_height()+6),0)
    nextbutton = screen.blit(nextbuttontext, [(w-nextbuttontext.get_rect()[2])/2,h-nextbuttontext.get_rect()[1]-200])


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
    soundpic = pg.image.load('sound.png')
    soundbutton = screen.blit(soundpic, (0,0))
    pg.display.flip()

def pronunciationpractice(lesson):
    global pronunciationbuttonpic, pronunciationbutton, menupushed
    menupushed = False
    screen.fill(background_colour)
    soundpic = pg.image.load('sound.png')
    recorddot = pg.image.load('recorddot.png')
    drawnextbutton()
    drawpronunciationbutton(w-200,h/2)
    #lesson = "emotions" #temporary lesson variable before getting sreen picked
    listofpics = [f for f in listdir(unit + "/" + lesson+"/pics/") if isfile(join(unit + "/" + lesson+"/pics/",f))] #pictures in lesson/pics/ folder
    original_length = len(listofpics)
    random.shuffle(listofpics) #shuffle order of lesson
    picpath = unit + "/" + lesson+"/pics/"
    soundpath = unit + "/" + lesson+"/sounds/"
    count_originals = 0
    for pic in listofpics:
        screen.fill(background_colour)
        soundbutton = screen.blit(soundpic, (0,0))
        drawnextbutton()
        drawpronunciationbutton(w-200,h/2)
        answer = pic
        word = answer[:answer.rindex(".")]
        word_display = word#.replace(".questionmark","?")
        for sym in [sym for sym in replacementsdict.keys() if sym in word_display]:
            word_display = word_display.replace(sym,replacementsdict[sym])
        if sys.platform == "darwin":
            outputdir = "/tmp/"
            sentence_corrected = word_display
            sentence = word
            os.system('say -o "' + str(outputdir+sentence)+'speech_google.WAVE" -f BEI16@44100 "' + sentence_corrected + '"')
            pg.time.wait(10)
            wordsound = pg.mixer.music.load(str(outputdir+sentence)+'speech_google.WAVE')    
        else:
            wordsound = pg.mixer.music.load(soundpath+word+"speech_google.wav")
        display_word(word_display)
        drawquitbutton()
        #drawmenubutton()
        picimage = pg.image.load(picpath + pic)
        picimage = pg.transform.smoothscale(picimage, getbestratio(screen.get_size()[1]-300,screen.get_size()[0]-300,float(picimage.get_size()[1]),float(picimage.get_size()[0]))) #(screenheight, screenwidht, picheight, picwidth)
        screen.blit(picimage,[5,100])
        #play word sound
        pg.display.flip()
        pg.mixer.music.play(0)
        #Figure out what to do with click event handler
        looping = True
        while looping:
            for event in pg.event.get():
                # exit conditions --> windows titlebar x click
                if event.type == pg.QUIT:
                    raise SystemExit
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pg.mouse.get_pos()
                    if soundbutton.collidepoint(pos): #Sound button is pressed
                        pg.mixer.music.play(0)
                    if pronunciationbutton.collidepoint(pos):
                        pg.draw.rect(screen,background_colour,(w-200,h/2,80,80),0)
                        pronunciationbuttonpic = pg.image.load("recorddot.png").convert_alpha()
                        pronunciationbutton = screen.blit(pronunciationbuttonpic, [w-200,h/2])
                        pg.display.update()
                        try:
                            recordinput()
                        except:
                            os.system("rec -c 2 /tmp/voice.aiff trim 0 00:05")
                        pg.draw.rect(screen,background_colour,(w-200,h/2,80,80),0)
                        drawpronunciationbutton(w-200,h/2)
                        pg.display.update()
                        pg.mixer.music.play(0)
                        while pg.mixer.music.get_busy():
                            pg.time.wait(10)
                        try:
                            playinput()
                        except:
                            output = pg.mixer.music.load("/tmp/input.wav")
                            pg.mixer.music.play(0)
                            os.system("play /tmp/voice.aiff")
                    if quitbutton.collidepoint(pos):
                        raise SystemExit
                    if nextbutton.collidepoint(pos):
                        while pg.mixer.music.get_busy():
                            pg.time.wait(10)
                        looping = False
                        break
def mainlesson(lesson):
    global scorelabel, score, incorrectscore, trycount, original_length, missed, menupushed
    menupushed = False
    missed = []
    score = 0
    incorrectscore = 0
    #lesson = "emotions" #temporary lesson variable before getting screen picked
    listofpics = [f for f in listdir(unit + "/" + lesson+"/pics/") if isfile(join(unit + "/" + lesson+"/pics/",f))] #pictures in unit/lesson/pics/ folder
    original_length = len(listofpics)
    random.shuffle(listofpics) #shuffle order of lesson
    picpath = unit + "/" + lesson+"/pics/"
    soundpath = unit + "/" + lesson+"/sounds/"
    count_originals = 0
    for pic in listofpics:
        trycount = 0
        count_originals += 1
        drawlessonstructure()
        answer = pic
        word = answer[:answer.rindex(".")]
        word_display = word
        for sym in [sym for sym in replacementsdict.keys() if sym in word_display]:
            word_display = word_display.replace(sym,replacementsdict[sym])
        if sys.platform == "darwin":
            outputdir = "/tmp/"
            sentence_corrected = word_display
            sentence = word
            os.system('say -o "' + str(outputdir+sentence)+'speech_google.WAVE" -f BEI16@44100 "' + sentence_corrected + '"')
            pg.time.wait(10)
            wordsound = pg.mixer.music.load(str(outputdir+sentence)+'speech_google.WAVE')    
        else:
            wordsound = pg.mixer.music.load(soundpath+word+"speech_google.wav")
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
        pic1 = pg.image.load(picpath+choice1)
        pic2 = pg.image.load(picpath+choice2)
        pic3 = pg.image.load(picpath+choice3)
        pic4 = pg.image.load(picpath+choice4)
        pics = [pic1,pic2,pic3,pic4]
        #scale pictures to max size without stretching
        pic1 = pg.transform.smoothscale(pic1, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic1.get_size()[1]),float(pic1.get_size()[0])))
        pic2 = pg.transform.smoothscale(pic2, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic2.get_size()[1]),float(pic2.get_size()[0])))
        pic3 = pg.transform.smoothscale(pic3, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic3.get_size()[1]),float(pic3.get_size()[0])))
        pic4 = pg.transform.smoothscale(pic4, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic4.get_size()[1]),float(pic4.get_size()[0])))
        #match to choiceboxes surfaces
        surf1 = pg.Surface.blit(screen,pic1,choicebox1)
        surf2 = pg.Surface.blit(screen,pic2,choicebox2)
        surf3 = pg.Surface.blit(screen,pic3,choicebox3)
        surf4 = pg.Surface.blit(screen,pic4,choicebox4)
        pics = [pic1,pic2,pic3,pic4]
        surfs = [surf1,surf2,surf3,surf4]    
        display_word(word_display)
        drawmenubutton()
        #play word sound
        pg.display.flip()
        pg.mixer.music.play(0)
        #Figure out what to do with click event handler
        looping = True
        while looping:
            for event in pg.event.get():
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
                        while pg.mixer.get_busy():
                            pg.time.wait(10)
                        pg.mixer.music.play(0)
                        trycount += 1
                    #Right answer is clicked
                    elif surfs[randomindex.index(0)].collidepoint(pos):
                        correct_sound.play()
                        screen.fill(background_colour)
                        try:
                            wordsound = pg.mixer.music.load(soundpath+word+"speech_google.ogg")
                        except:
                            wordsound = pg.mixer.music.load(soundpath+word+"speech_google.wav")
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
    listofpics = [f for f in listdir(unit + "/" + lesson+"/pics/") if isfile(join(unit + "/" + lesson+"/pics/",f))] #pictures in unit/lesson/pics/ folder
    original_length = len(listofpics)
    random.shuffle(listofpics) #shuffle order of lesson
    picpath = unit + "/" + lesson+"/pics/"
    soundpath = unit + "/" + lesson+"/sounds/"
    count_originals = 0
    for pic in listofpics:
        trycount = 0
        count_originals += 1
        drawlessonstructure()
        answer = pic
        word = answer[:answer.rindex(".")]
        word_display = word
        for sym in [sym for sym in replacementsdict.keys() if sym in word_display]:
            word_display = word_display.replace(sym,replacementsdict[sym])
        if sys.platform == "darwin":
            outputdir = "/tmp/"
            sentence_corrected = word_display
            sentence = word
            os.system('say -o "' + str(outputdir+sentence)+'speech_google.WAVE" -f BEI16@44100 "' + sentence_corrected + '"')
            pg.time.wait(10)
            wordsound = pg.mixer.music.load(str(outputdir+sentence)+'speech_google.WAVE')    
        else:
            wordsound = pg.mixer.music.load(soundpath+word+"speech_google.wav")
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
        pic1 = pg.image.load(picpath+choice1)
        pic2 = pg.image.load(picpath+choice2)
        pic3 = pg.image.load(picpath+choice3)
        pic4 = pg.image.load(picpath+choice4)
        pics = [pic1,pic2,pic3,pic4]
        #scale pictures to max size without stretching
        pic1 = pg.transform.smoothscale(pic1, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic1.get_size()[1]),float(pic1.get_size()[0])))
        pic2 = pg.transform.smoothscale(pic2, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic2.get_size()[1]),float(pic2.get_size()[0])))
        pic3 = pg.transform.smoothscale(pic3, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic3.get_size()[1]),float(pic3.get_size()[0])))
        pic4 = pg.transform.smoothscale(pic4, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic4.get_size()[1]),float(pic4.get_size()[0])))
        #render choice text
        #txt1 = text_display_word(choice1,choicebox1)
        txt1 = render_textrect(choice1, pg.Rect(choicebox1[0],choicebox1[1],choicebox1[2]-3,choicebox1[3]-3), (0, 0, 0), (255, 255, 255))
        surf1 = screen.blit(txt1, choicebox1.topleft)
        #surf1 = pg.Surface.blit(screen,txt1,choicebox1.topleft)
        txt2 = render_textrect(choice2, pg.Rect(choicebox2[0],choicebox2[1],choicebox2[2]-3,choicebox2[3]-3), (0, 0, 0), (255, 255, 255))
        surf2 = pg.Surface.blit(screen,txt2,choicebox2.topleft)
        txt3 = render_textrect(choice3, pg.Rect(choicebox3[0],choicebox3[1],choicebox3[2]-3,choicebox3[3]-3), (0, 0, 0), (255, 255, 255))
        surf3 = pg.Surface.blit(screen,txt3,choicebox3.topleft)
        txt4 = render_textrect(choice4, pg.Rect(choicebox4[0],choicebox4[1],choicebox4[2]-3,choicebox4[3]-3), (0, 0, 0), (255, 255, 255))
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
        while looping:
            for event in pg.event.get():
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
                        while pg.mixer.get_busy():
                            pg.time.wait(10)
                        pg.mixer.music.play(0)
                        trycount += 1
                    #Right answer is clicked
                    elif surfs[randomindex.index(0)].collidepoint(pos):
                        correct_sound.play()
                        screen.fill(background_colour)
                        try:
                            wordsound = pg.mixer.music.load(soundpath+word+"speech_google.ogg")
                        except:
                            wordsound = pg.mixer.music.load(soundpath+word+"speech_google.wav")
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
    global scorelabel,w,h, score,incorrectscore, completeddict
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
    chooselessonbuttontext = mysmallfont.render("Choose a lesson", 2, black)
    chooselessonbuttonbox = pg.draw.rect(screen,gray,((w/2)-(chooselessonbuttontext.get_rect()[2]/2)-3,h-200-3,chooselessonbuttontext.get_width()+6,chooselessonbuttontext.get_height()+6),0)
    chooselessonbutton = screen.blit(chooselessonbuttontext, [(w/2)-(chooselessonbuttontext.get_rect()[2]/2),h-200])
    repeatlessonbuttontext = mysmallfont.render("Repeat", 2, black)
    repeatlessonbuttonbox = pg.draw.rect(screen,gray,((w/2)-(repeatlessonbuttontext.get_rect()[2]/2)-3,h-200-3-65,repeatlessonbuttontext.get_width()+6,repeatlessonbuttontext.get_height()+6),0)
    repeatlessonbutton = screen.blit(repeatlessonbuttontext, [(w/2)-(repeatlessonbuttontext.get_rect()[2]/2),h-200-65])
    repeatpic = pg.image.load("repeat.png").convert_alpha()
    pencilpic = pg.image.load("pencil.png").convert_alpha()
    screen.blit(pencilpic, [w/2,h/2])
    rep = screen.blit(repeatpic, [repeatlessonbuttonbox[0]-75,repeatlessonbuttonbox[1]-3])
    drawquitbutton()
    pg.display.flip()
    completeddict[lesson] = int((float(score) / float(original_length))*100)
    looping = True
    while looping:
        for event in pg.event.get():
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
                if chooselessonbuttonbox.collidepoint(pos):
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
    listoffolders = [f for f in listdir("./") if isfile(join("./",f)) == False]
    try:
        listoffolders.remove("examplelesson") #remove blank lesson from menu
        listoffolders.remove("exampleunit")
        listoffolders.remove("Test")
        listoffolders.remove("RosettaTablet.app")
    except:
        pass
    listoffolderlables = [screen.blit(mysmallfont.render(str(listoffolders.index(folder)+1)+". "+folder.title(), 1, black),[20,45*listoffolders.index(folder)]) for folder in listoffolders]
    drawquitbutton()
    pg.display.flip()
    while uniton:
        for event in pg.event.get():
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
                        lessonmenu(unit)
                        pg.display.quit
                        return unit
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
    listoffolders = [f for f in listdir("./"+unit) if isfile(join("./"+unit,f)) == False]
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
    while lessonon:
        for event in pg.event.get():
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
            if menupushed == True:
                unitmenu()
        else:
            unitmenu()
    else:
        unitmenu()


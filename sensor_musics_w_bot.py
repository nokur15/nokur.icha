# Write your code here :-)
#python3 sensor_musics_w_bot.py
#DIY Motion Triggered Music Player

import time
from time import sleep
from threading import Thread
import RPi.GPIO as GPIO
import subprocess
import telepot
from multiprocessing import Process
import os
from telepot.loop import MessageLoop
from os import listdir
from os.path import isfile, join
from omxplayer.player import OMXPlayer
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO)

mypath = "/home/pi/Downloads"
musicfiles = [f for f in listdir(mypath) if (isfile(join(mypath, f)) and f.endswith(".mp3"))]
players=[]
var_pause = 0
for i in musicfiles:
    player_log = logging.getLogger("Player (%d)", % i)
    players[i] = OMXPlayer(musicfiles[i], 
                    dbus_name=('org.mpris.MediaPlayer2.omxplayer(%d)', % i))
    players[i].playEvent += lambda _: player_log.info("Play")
    players[i].pauseEvent += lambda _: player_log.info("Pause")
    players[i].stopEvent += lambda _: player_log.info("Stop")

class AutoTrigger():
    def call_omxplayer(self):
        j = 1
        while j<=len(players):
            for i in players:
                direc = self.mypath + "/" + i
                if i == players[1] or not players[j].is_playing():
                    print ("playing " + musicfiles[players.index(i)])
                    i.play()
            #info('pid_run')
            #pid =subprocess.Popen(["omxplayer", direc], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=lambda x: pid.communicate(["p"]), bouncetime=10)
        self.is_running = False
        #handle.play = True
    def play_song(self):
        if not self.is_running:
            self.song_thread = Thread(target= self.call_omxplayer, args=())
            self.song_thread.start()
            self.is_running = True
    def __init__(self,pin,mypath):
        self.pin = pin
        #self.player = players
        self.mypath = mypath
        self.is_running = False
        GPIO.setup(pin, GPIO.IN)
        '''
        This is a hack (the callback) thanks for python closures!
        '''
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=lambda x: self.play_song(), bouncetime=10)
def main(mypath):
    info('main')
    GPIO.setmode(GPIO.BOARD)
    AutoTrigger(11, mypath)
    print ("Ready: !")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()
        player.stop()
        player.quit()

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def handle(msg):
    info('handle')
    chat_id = msg['chat']['id']
    command = msg['text']
    
    print ('Received: ')
    print (command)
    
    if command == '/hi':
        bot.sendMessage (chat_id, str("Welcome to Study Comp!"))
    elif command == '/start':
        bot.sendMessage (chat_id, str("Starting device"))
    elif command == '/pause':
        for i in players:
            if i.is_playing():
                bot.sendMessage (chat_id, str("Pausing the song"))
                i.pause()
                var_pause = players.index(i)
    elif command == '/play':
        bot.sendMessage (chat_id, str("Playing the song"))
        players[var_pause].play()
    elif command == '/songlist':
        bot.sendMessage(chat_id, str("List lagu yang dapat dimainkan:"))
        for i in musicfiles:
            bot.sendMessage (chat_id, i)
    
        

if __name__ == '__main__':
    info('start')
    bot = telepot.Bot('1407746688:AAG7gxt9cahWBz_fKP0NbsuthWNNB9I-1vw')
    print (bot.getMe())
    
    print('Listening...')
    p1 = Process(target=MessageLoop(bot,handle).run_as_thread())
    p1.start()
    p2 = Process(target=main(mypath)
    p2.start()
    p1.join()
    p2.join()
    
    while 1:
        sleep(10)
    #main()

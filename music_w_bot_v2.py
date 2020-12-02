#python3 sensor_musics_w_bot.py
#DIY Motion Triggered Music Player

import time
import asyncio
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
            player_log = logging.getLogger("Player " + str(musicfiles.index(i)))
            direc = mypath + "/" + i
            players.append(OMXPlayer(direc, 
                    dbus_name=('org.mpris.MediaPlayer2.omxplayer' + str(musicfiles.index(i)+1))))
            players[musicfiles.index(i)].pause()
            players[musicfiles.index(i)].playEvent += lambda _: player_log.info("Play")
            players[musicfiles.index(i)].pauseEvent += lambda _: player_log.info("Pause")
            players[musicfiles.index(i)].stopEvent += lambda _: player_log.info("Stop")

class AutoTrigger():
    def call_omxplayer(self):
        #for i in musicfiles:
        #    player_log = logging.getLogger("Player " + str(musicfiles.index(i)))
        #    direc = mypath + "/" + i
        #    players.append(OMXPlayer(direc, 
        #            dbus_name=('org.mpris.MediaPlayer2.omxplayer' + str(musicfiles.index(i)+1))))
        #    players[musicfiles.index(i)].playEvent += lambda _: player_log.info("Play")
        #    players[musicfiles.index(i)].pauseEvent += lambda _: player_log.info("Pause")
        #    players[musicfiles.index(i)].stopEvent += lambda _: player_log.info("Stop")
        #    if players[musicfiles.index(i)-1].is_playing():
        #        players[musicfiles.index(i)].pause

        for i in players:
            #if i == players[0] or not players[j].is_playing():
            self.pause_time = 0
            print ("playing " + musicfiles[players.index(i)])
            i.play()
            sleep(i.duration())
            if self.has_paused:
                sleep(self.pause_time)
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
            self.is_paused = False

    def handle(self,msg):
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
                    self.start_time = time.time()
                    self.var_pause = players.index(i)
                    self.has_paused = True
        elif command == '/play':
            bot.sendMessage (chat_id, str("Playing the song"))
            bot.sendMessage (chat_id, self.var_pause)
            players[self.var_pause].play()
            self.end_time = time.time()
            time_lapse = self.end_time-self.start_time
            self.pause_time += time_lapse
        elif command == '/songlist':
            bot.sendMessage(chat_id, str("List lagu yang dapat dimainkan:"))
            for i in musicfiles:
                bot.sendMessage (chat_id, i)
    
    def __init__(self,pin, bot, mypath):
        self.pin = pin
        #self.player = players
        self.bot = bot
        self.mypath = mypath
        self.is_running = False
        self.var_pause = 0
        self.has_paused = True
        self.start_time = 0
        self.end_time = 0
        self.pause_time = 0
        GPIO.setup(pin, GPIO.IN)
        MessageLoop(bot=self.bot,handle=self.handle).run_as_thread()
        #self.message_thread = Thread(target=MessageLoop(self.bot,self.handle).run_as_thread())
        #self.message_thread.start()
        '''
        This is a hack (the callback) thanks for python closures!
        '''
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=lambda x: self.play_song(), bouncetime=10)

def main(bot,mypath):
    info('main')
    GPIO.setmode(GPIO.BOARD)
    AutoTrigger(11, bot, mypath)
    print ("Ready: !")
    print('Listening...')
    try:
        while True:
            pass
            #MessageLoop(bot,handle).run_as_thread()
    except KeyboardInterrupt:
        GPIO.cleanup()
        for i in players:
            i.stop()
            i.quit()

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

'''
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
                global var_pause
                bot.sendMessage (chat_id, str("Pausing the song"))
                i.pause()
                var_pause = players.index(i)
    elif command == '/play':
        bot.sendMessage (chat_id, str("Playing the song"))
        bot.sendMessage (chat_id, var_pause)
        players[var_pause].play()
    elif command == '/songlist':
        bot.sendMessage(chat_id, str("List lagu yang dapat dimainkan:"))
        for i in musicfiles:
            bot.sendMessage (chat_id, i)
'''  
        

if __name__ == '__main__':
    #Proses connecting dengan bot Telegram
    info('start')
    bot = telepot.Bot('1407746688:AAG7gxt9cahWBz_fKP0NbsuthWNNB9I-1vw')
    print (bot.getMe()) #Bot Telegram connected
    
    main(bot,mypath)
    #p1 = Process(target=MessageLoop(bot,handle).run_as_thread())
    #p1.start()
    #p2 = Process(target=main(mypath))
    #p2.start()
    #p1.join()
    #p2.join()
    
    while 1:
        sleep(10)
    #main()

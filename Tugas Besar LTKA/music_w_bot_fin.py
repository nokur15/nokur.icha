'''
example for custom directory
python3 music_w_bot_fin.py --directory /home/pi/Downloads/Songs
using default directory
python3 music_w_bot_fin.py

IoT Music Player for Study Companion
By Thirza Nabila S (18117011) & M. Naufal Kurniawan (18117012)

Credits to:
DIY Motion Triggered Music Player
'''

#Main library : time, GPIO, Thread, telepot, os, OMXPlayer, argparse
import time
from time import sleep
from threading import Thread
import RPi.GPIO as GPIO
import telepot
from telepot.loop import MessageLoop
import os
from os import listdir
from os.path import isfile, join
from omxplayer.player import OMXPlayer
from pathlib import Path
import argparse
import logging
logging.basicConfig(level=logging.INFO)

#Early initialization
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", type=str, 
                default="/home/pi/Downloads", help="Path folder containing the songs")
args = vars(ap.parse_args())

mypath = args["directory"]
musicfiles = [f for f in listdir(mypath) if (isfile(join(mypath, f)) and f.endswith(".mp3"))]


#Detecting motion to play music while also receiving commands from Telegram Bot
class AutoTrigger():
    #Play the music from musicfiles list
    def call_omxplayer(self):
        for i in self.players:
            self.pause_time = 0
            self.playing = i
            self.song = musicfiles[self.players.index(i)]
            print ("playing " + self.song)
            self.playing.play()
            sleep(self.playing.duration())
            if self.has_paused:
                sleep(self.pause_time)
        self.is_running = False

    '''
    If PIR sensor detects motion, there are 3 possibilities:
    - First time: Executing call_omxplayer function
    - If the song is in play : Pausing the song
    - If the song is in pause : Playing the song
    '''
    def play_song(self):
        if not self.is_running:
            #Making call_omxplayer as the 2nd Thread
            self.song_thread = Thread(target= self.call_omxplayer, args=())
            self.song_thread.start()
            self.is_running = True
            self.has_paused = False
        elif self.playing.is_playing():
            self.playing.pause()
            self.start_time = time.time()
            self.has_paused = True
        elif not self.playing.is_playing():
            self.playing.play()
            self.end_time = time.time()
            time_lapse = self.end_time-self.start_time
            self.pause_time += time_lapse

    '''
    Executing responses from the Telegram Bot
    Command /start to execute play_song and call_omxplayer as 2nd Thread
    '''
    def handle(self,msg):
        chat_id = msg['chat']['id']
        command = msg['text']
    
        print ('Received: ')
        print (command)
    
        if command == '/hi':
            bot.sendMessage (chat_id, str("""Welcome to Study Comp!
Give command "/help" to see the list of commands"""))
        elif command == '/start':
            bot.sendMessage (chat_id, str("Starting the device"))
            self.players = []
            #Setting GPIO pin 11
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.pin, GPIO.IN)
            #Entering list of songs into OMXPlayer class
            for i in musicfiles:
                player_log = logging.getLogger("Player " + str(musicfiles.index(i)))
                direc = mypath + "/" + i
                self.players.append(OMXPlayer(direc, 
                            dbus_name=('org.mpris.MediaPlayer2.omxplayer' + str(musicfiles.index(i)+1))))
                self.players[musicfiles.index(i)].pause()
                self.players[musicfiles.index(i)].playEvent += lambda _: player_log.info("Play")
                self.players[musicfiles.index(i)].pauseEvent += lambda _: player_log.info("Pause")
                self.players[musicfiles.index(i)].stopEvent += lambda _: player_log.info("Stop")
            #Detecting Motion from PIR Sensor
            GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=lambda x: self.play_song(), bouncetime=10)
        elif command == '/pause':
            bot.sendMessage (chat_id, str("Pausing the song"))
            bot.sendMessage (chat_id, self.song)
            self.playing.pause()
            self.start_time = time.time()
            self.has_paused = True
        elif command == '/play':
            bot.sendMessage (chat_id, str("Playing the song"))
            bot.sendMessage (chat_id, self.song)
            self.playing.play()
            self.end_time = time.time()
            time_lapse = self.end_time-self.start_time
            self.pause_time += time_lapse
        elif command == '/songlist':
            bot.sendMessage(chat_id, str("List of songs to be played:"))
            for i in musicfiles:
                bot.sendMessage (chat_id, i)
        elif command == '/showvol':
            bot.sendMessage(chat_id, self.playing.volume())
            bot.sendMessage (chat_id, str("Volume range from 0-10"))
        elif command == '/incvol':
            bot.sendMessage(chat_id, str("Increasing volume by 1"))
            self.new_vol = self.playing.volume() + 1
            self.playing.set_volume(self.new_vol)
        elif command == '/decvol':
            bot.sendMessage(chat_id, str("Decreasing volume by 1"))
            self.new_vol = self.playing.volume() - 1
            self.playing.set_volume(self.new_vol)
        elif command == '/about':
            bot.sendMessage(chat_id, str("""This bot is for LTKA Final Assignment.
Created by Thirza Nabila Syafriady and M. Naufal Kurniawan.
This bot will enable users to control Raspberry Pi by Pausing, Playing and Showing the list of songs.
Please do activate the Raspberry Pi before using this Bot."""))
        elif command == '/help':
            bot.sendMessage(chat_id, str("""List of available commands:
/hi : Introduction Message
/start : Starting the program
/about : Showing Information about the Bot and Project
/songlist : Showing list of songs to be played
/play : Play the song after being paused *
/pause : Pause the song after being played *
/showvol : Showing the volume level (range from 0-10) *
/decvol : Decreasing the volume by 1 *
/incvol : Increasing the volume by 1 *
/end : Closing the program *
* Commands cannot activate if "/start" hasn't been executed"""))
        elif command == '/end':
            bot.sendMessage(chat_id, str("Ending the device"))
            GPIO.cleanup()
            for i in self.players:
                i.stop()
                i.quit()
            self.is_running = False
    
    #initialize class variables, executing Thread to handle
    def __init__(self,pin, bot):
        self.pin = pin      #Pin to receive input from PIR Sensor
        self.bot = bot      #Passing bot variable
        self.is_running = False
        self.has_paused = True
        self.start_time = 0
        self.end_time = 0
        self.pause_time = 0
        self.players = []
        #Creating MessageLoop as the 1st Thread
        MessageLoop(bot=self.bot,handle=self.handle).run_as_thread()

#Main program initialization (pin location, call AutoTrigger, stops program from KeyboardInterrupt)
def main(bot):
    trig = AutoTrigger(11, bot)
    trig
    print ("Ready: !")
    print('Listening...')
    try:
        while True:
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()
        for i in trig.players:
            i.stop()
            i.quit()      

if __name__ == '__main__':
    #Connecting to bot Telegram
    bot = telepot.Bot('1407746688:AAG7gxt9cahWBz_fKP0NbsuthWNNB9I-1vw')
    print (bot.getMe()) #Bot Telegram connected
    
    #executing main function
    main(bot)
    
    while 1:
        sleep(10)

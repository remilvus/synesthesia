import pyaudio
import numpy as np
import threading
from random import randrange
import sys
from os import path
from datetime import datetime as date
from time import sleep, time
import readchar


def play(stream, sample):
   global dead
   while not dead:
      stream.write(sample)


if __name__=="__main__":
   global dead      #for stopping threads
   #frequencies = [(11*2**i + 11*2**(i+1))/2 for i in range(11)]
   frequencies = [16.351 *2**i for i in range(11)]
   fs = 44100       # sampling rate, Hz
   duration = 5     # in seconds
   p = pyaudio.PyAudio()
   stream = p.open(format=pyaudio.paFloat32,
                   channels=1,
                   rate=fs,
                   output=True)

   if path.isfile("synesthesia_log.txt"):
      log = open("synesthesia_log.txt","a+")
      print("log file opened")
   else:
     print("creating log file...")
     log = open("synesthesia_log.txt","a")
     log.write("abc")
     print("log file created")

   while True:
      idx = randrange(11)
      freq = frequencies[idx]

      #make sine wave of given frequency
      sound = np.sin(2*np.pi*np.arange(fs*duration)*freq/fs)
      sound = sound.astype(np.float32).tobytes()
      
      dead = False
      thr = threading.Thread(target=play, args=(stream, sound))
      thr.start()
      print("Press q to exit or anything else to continue:")
      x = readchar.readkey()
      print(str(x))
      dead = True
      t = time()
      if x=='q':
         print("ending")
         break

      description = input("Type \"end\" to exit,\nWhat did you see?:\n")
      if description=="end":
         break
      vol = input("What is the system volume?(0-100): ")
      t2=time()
      if duration-t2+t > 0:
         sleep(duration-t2+t) #wait for thread to stop playing
      now = date.now().strftime("%Y-%m-%d %H:%M")
      log.write(f"Hz: {frequencies[idx]} vol: {vol} date: {now} description: {description}\n")


   stream.stop_stream()
   stream.close()
   p.terminate()
   log.close()
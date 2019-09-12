import tkinter
from tkinter.colorchooser import askcolor  # returns tuple ((r, g, b), 'hex')
from tkinter.simpledialog import askinteger
import pyaudio
import numpy as np
import threading
from random import randrange
import sys
from os import path
from datetime import datetime as date
from time import sleep, time
import readchar


def play_sound(stream, sample, dead):
    while not dead[0]:
        stream.write(sample[0])


def save(colors, played_frequencies):
    if path.isfile("synesthesia_log.txt"):
        log = open("synesthesia_log.txt", "a+")
        print("log file opened")
    else:
        print("creating log file...")
        log = open("synesthesia_log.txt", "a")
        log.write("date,frequency,volume,colors\n")
        print("log file created")

    now = date.now().strftime("%Y-%m-%d %H:%M")
    vol = 0

    for f, c in zip (played_frequencies, colors):
        if c:
            line = now + "," + str(f[0])+ "," + str(f[1]) + "," + ",".join(c) + "\n"
            log.write(line)
    log.close()

def set_volume(volume):
    while True:
        v = askinteger("System Volume", "Input current system volume")
        if v:
            volume[0] = v
            return


def play(thr, stream, sound, dead, FREQ, played_freq, colors, canvas, volume):
    dead[0] = False
    if volume[0] == -1:
        set_volume(volume)
    if not thr:
        next_sound(FREQ, played_freq, sound, colors, canvas, volume)
        thr.append(threading.Thread(target=play_sound, args=(stream, sound, dead), daemon=True))
        thr[0].start()
    elif not thr[0].is_alive():
        thr[0] = threading.Thread(target=play_sound, args=(stream, sound, dead), daemon=True)
        thr[0].start()


def stop(dead, thr):
    dead[0] = True
    if thr:
        thr[0].join()


def next_sound(FREQ, played_freq, sound, colors, canvas, volume):
    if volume[-1] != -1:
        idx = randrange(11)
        played_freq.append([FREQ[idx], volume[-1]])

        # make sine wave of given frequency
        sound_tmp = np.sin(2 * np.pi * np.arange(FS * T) * played_freq[-1][0] / FS)
        sound[0] = sound_tmp.astype(np.float32).tobytes()

        colors.append([])
        canvas.delete("all")


def add_color(colors, canvas):
    if colors:
        if len(colors[-1]) < 16:
            color = askcolor()
            color = color[1]
            SIDE = 100
            PAD = 5
            x = (len(colors[-1]) % 4 ) * (SIDE + PAD)
            y = int(len(colors[-1]) / 4 ) * (SIDE + PAD)
            canvas.create_rectangle(x, y, x + SIDE, y + SIDE, fill=color, outline=color)
            colors[-1].append(color)


if __name__ == "__main__":

    FREQ = [16.351 * 2 ** i for i in range(11)]
    FS = 44100  # sampling rate, Hz
    T = 5  # in seconds
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=FS,
                    output=True)

    dead = [False]
    sound = [0]
    dead = [True]
    played_freq = []
    thr = []
    colors = []
    volume = [-1]

    root = tkinter.Tk()

    canvas = tkinter.Canvas(root)
    canvas.pack(fill=tkinter.BOTH, expand=1)

    menu_bar = tkinter.Menu(root)
    menu_bar.add_command(label="Play", command=lambda: play(thr, stream, sound, dead, FREQ, played_freq, colors, canvas, volume))
    menu_bar.add_command(label="Next", command=lambda: next_sound(FREQ, played_freq, sound, colors, canvas, volume))
    menu_bar.add_command(label="Stop", command=lambda: stop(dead, thr))
    menu_bar.add_command(label="Add Color", command=lambda: add_color(colors, canvas))
    menu_bar.add_command(label="Set volume", command=lambda: set_volume(volume))
    menu_bar.add_command(label="Save", command=lambda: save(colors, played_freq))
    root.config(menu=menu_bar)
    root.geometry("420x420")
    root.mainloop()

    if thr:
        thr[-1].join()
    stream.stop_stream()
    stream.close()
    p.terminate()
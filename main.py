import os
import wave
import math
import json
import time
import random
from pathlib import Path
import pygame
from scipy.ndimage import interpolation
import audioop
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg
)
import numpy as np
import tkinter as tk

guitar_clip = "./guitar_mono.wav"
orchestral_clip = "./orchestral_mono.wav"
voice_clip = "./voice_mono.wav"

is_playing = False
my_thread = None

is_testing = False

pygame.mixer.init()


class Manager:
    def __init__(self):
        self.active_clip = guitar_clip
        self.working_clip = self.active_clip
        self.compression_mod = "None"
        self.frequency_mod = 44100
        self.bitdepth_mod = 16
        self.original_frequency = 44100
        self.original_signal = self.read_signal()
        self.working_signal = np.copy(self.original_signal)

    def change_active_clip(self, new_clip):
        self.active_clip = new_clip
        self.working_clip = self.active_clip
        self.compression_mod = "None"
        self.frequency_mod = 44100
        self.bitdepth_mod = 16
        self.original_signal = self.read_signal()
        self.working_signal = np.copy(self.original_signal)

    def read_signal(self):
        wf = wave.open(self.active_clip, 'rb')
        self.original_frequency = wf.getframerate()
        signal = wf.readframes(-1)
        return np.fromstring(signal, "Int16")

    def create_wave(self, file='./temp.wav'):
        if (Path(file).exists()):
            os.remove(file)
        obj = wave.open(file, 'w')
        obj.setnchannels(1)
        obj.setsampwidth(2)
        obj.setframerate(self.get_frequency_mod())
        obj.writeframesraw(self.working_signal)
        obj.close()
        return file


    def modify_signal(self):
        self.working_signal = np.copy(self.original_signal)
        if (self.compression_mod != "None"):
            self.compress()
        self.change_frequency()
        if (self.bitdepth_mod != 16):
            self.change_bitdepth()

    def change_mod(self, mod, new_value):
        if (mod == "frequency"):
            print("Changing frequency to {}".format(new_value))
            self.frequency_mod = new_value
            self.modify_signal()
        if (mod == "compression"):
            print("Changing compression to {}".format(new_value))
            self.compression_mod = new_value
            self.modify_signal()
        if (mod == "bitdepth"):
            print("Changing bitdepth to {}".format(new_value))
            self.bitdepth_mod = new_value
            self.modify_signal()

    def compress(self):
        read = wave.open(self.create_wave(), 'rb')
        string_wav = np.fromstring(read.readframes(-1), 'Int16')

        if (self.compression_mod == "a-LAW"):
            compressed_string = audioop.lin2alaw(string_wav, read.getsampwidth())
            compressed_string = audioop.alaw2lin(compressed_string, read.getsampwidth())
            self.working_signal = np.frombuffer(compressed_string, dtype='Int16')
        if (self.compression_mod == "u-LAW"):
            compressed_string = audioop.lin2ulaw(string_wav, read.getsampwidth())
            compressed_string = audioop.ulaw2lin(compressed_string, read.getsampwidth())
            self.working_signal = np.frombuffer(compressed_string, dtype='Int16')
        if (self.compression_mod == "ADPCM"):
            compressed_string = audioop.lin2adpcm(string_wav, read.getsampwidth(), None)
            compressed_string = audioop.adpcm2lin(compressed_string[0], read.getsampwidth(), None)
            self.working_signal = np.frombuffer(compressed_string[0], dtype='Int16')

    def change_frequency(self):
        z = self.frequency_mod / 44100
        self.working_signal = interpolation.zoom(self.working_signal, z)

    def change_bitdepth(self):
        bitdepth_scale = (2 ** 16) / (2 ** self.bitdepth_mod)
        for i in range(self.working_signal.shape[0]):
            self.working_signal[i] = self.working_signal[i] - (self.working_signal[i] % bitdepth_scale)

    def get_active_clip(self):
        return self.active_clip

    def get_compression_mod(self):
        return self.compression_mod

    def get_frequency_mod(self):
        return self.frequency_mod

    def get_bitdepth_mod(self):
        return self.bitdepth_mod

    def get_working_signal(self):
        return self.working_signal

    def get_original_signal(self):
        return self.original_signal

    def get_width(self):
        if self.bitdepth_mod == 16:
            return 4
        if self.bitdepth_mod == 8:
            return 3
        if self.bitdepth_mod == 4:
            return 2
        if self.bitdepth_mod == 2:
            return 1

def upscale_signal(signal, desired):

    z = desired / len(signal)
    return interpolation.zoom(signal, z)

def play_audio(man, signal):
    global is_playing

    if pygame.mixer.music.get_busy():
        press_button_stop()

    if signal == "original":
        pygame.mixer.music.load(man.get_active_clip())
    else:
        pygame.mixer.music.load(man.create_wave('./play.wav'))

    pygame.mixer.music.play(loops=0)
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.unload()

def press_button_stop():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()

def update_labels(label, man):
    label[0].set("Active sound clip: {}".format(man.get_active_clip()))
    label[1].set("Active compression mod: {}".format(man.get_compression_mod()))
    label[2].set("Active frequency mod: {}".format(man.get_frequency_mod()))
    label[3].set("Active bitdepth mod: {}".format(man.get_bitdepth_mod()))
    label[4].set("PSNR: {}".format(PSNR(man.get_original_signal(), man.get_working_signal(), man)))

def update_plots(ax, man):
    ax[0].clear()
    ax[1].clear()
    ax[0].plot(man.get_original_signal())
    ax[1].plot(man.get_working_signal())

    canvas.draw()
    canvas.flush_events()

def PSNR(original, compressed, man):
    if len(original) != len(compressed):
        compressed = upscale_signal(compressed, len(man.get_original_signal()))
    mse = np.mean(np.square(np.array(np.subtract(original, compressed), dtype='int64')))
    print(np.square(np.subtract(original, compressed)))
    if (mse == 0):
        return 100
    max_pixel = 32767.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    print(psnr)
    return psnr

def save_to_json(man):
    global score
    return ({
        "Clip": man.get_active_clip(),
        "PSNR": PSNR(man.get_original_signal(), man.get_working_signal(), man),
        "Compression": man.get_compression_mod(),
        "Frequency": man.get_frequency_mod(),
        "Bitdepth": man.get_bitdepth_mod(),
        "Score": score
    })

def whole_test(man):
    global is_testing
    if is_testing:
        return
    is_testing = True

    results = []

    walk1 = list(range(1,12))
    walk2 = list(range(12,23))
    walk3 = list(range(23,34))
    random.shuffle(walk1)
    random.shuffle(walk2)
    random.shuffle(walk3)

    results.append(dry_test(man, 77))
    for choice in walk1:
        results.append(dry_test(man, choice))
    results.append(dry_test(man, 88))
    for choice in walk2:
        results.append(dry_test(man, choice))
    results.append(dry_test(man, 99))
    for choice in walk3:
        results.append(dry_test(man, choice))

    if (Path("./results.json").exists()):
        os.remove("./results.json")

    with open("./results.json", 'w') as f:
        json.dump(results, f, indent=2)

    is_testing = False


def dry_test(man, choice):
    ## Guitar clip results
    print(choice)
    if choice == 1:
        man.change_active_clip(guitar_clip)
        man.change_mod("compression", "a-LAW")

    if choice == 2:
        man.change_active_clip(guitar_clip)
        man.change_mod("compression", "u-LAW")

    if choice == 3:
        man.change_active_clip(guitar_clip)
        man.change_mod("compression", "ADPCM")

    if choice == 4:
        man.change_active_clip(guitar_clip)
        man.change_mod("frequency", 22000)

    if choice == 5:
        man.change_active_clip(guitar_clip)
        man.change_mod("frequency", 11000)

    if choice == 6:
        man.change_active_clip(guitar_clip)
        man.change_mod("frequency", 8000)

    if choice == 7:
        man.change_active_clip(guitar_clip)
        man.change_mod("frequency", 4000)

    if choice == 8:
        man.change_active_clip(guitar_clip)
        man.change_mod("frequency", 2000)

    if choice == 9:
        man.change_active_clip(guitar_clip)
        man.change_mod("bitdepth", 8)

    if choice == 10:
        man.change_active_clip(guitar_clip)
        man.change_mod("bitdepth", 4)

    if choice == 11:
        man.change_active_clip(guitar_clip)
        man.change_mod("bitdepth", 2)

    ## Orchestral clip results

    if choice == 12:
        man.change_active_clip(orchestral_clip)
        man.change_mod("compression", "a-LAW")

    if choice == 13:
        man.change_active_clip(orchestral_clip)
        man.change_mod("compression", "u-LAW")

    if choice == 14:
        man.change_active_clip(orchestral_clip)
        man.change_mod("compression", "ADPCM")

    if choice == 15:
        man.change_active_clip(orchestral_clip)
        man.change_mod("frequency", 22000)

    if choice == 16:
        man.change_active_clip(orchestral_clip)
        man.change_mod("frequency", 11000)

    if choice == 17:
        man.change_active_clip(orchestral_clip)
        man.change_mod("frequency", 8000)

    if choice == 18:
        man.change_active_clip(orchestral_clip)
        man.change_mod("frequency", 4000)

    if choice == 19:
        man.change_active_clip(orchestral_clip)
        man.change_mod("frequency", 2000)

    if choice == 20:
        man.change_active_clip(orchestral_clip)
        man.change_mod("bitdepth", 8)

    if choice == 21:
        man.change_active_clip(orchestral_clip)
        man.change_mod("bitdepth", 4)

    if choice == 22:
        man.change_active_clip(orchestral_clip)
        man.change_mod("bitdepth", 2)

    ## Voice clip results

    if choice == 23:
        man.change_active_clip(voice_clip)
        man.change_mod("compression", "a-LAW")

    if choice == 24:
        man.change_active_clip(voice_clip)
        man.change_mod("compression", "u-LAW")

    if choice == 25:
        man.change_active_clip(voice_clip)
        man.change_mod("compression", "ADPCM")

    if choice == 26:
        man.change_active_clip(voice_clip)
        man.change_mod("frequency", 22000)

    if choice == 27:
        man.change_active_clip(voice_clip)
        man.change_mod("frequency", 11000)

    if choice == 28:
        man.change_active_clip(voice_clip)
        man.change_mod("frequency", 8000)

    if choice == 29:
        man.change_active_clip(voice_clip)
        man.change_mod("frequency", 4000)

    if choice == 30:
        man.change_active_clip(voice_clip)
        man.change_mod("frequency", 2000)

    if choice == 31:
        man.change_active_clip(voice_clip)
        man.change_mod("bitdepth", 8)

    if choice == 32:
        man.change_active_clip(voice_clip)
        man.change_mod("bitdepth", 4)

    if choice == 33:
        man.change_active_clip(voice_clip)
        man.change_mod("bitdepth", 2)

    if choice == 77:
        man.change_active_clip(guitar_clip)
    if choice == 88:
        man.change_active_clip(orchestral_clip)
    if choice == 99:
        man.change_active_clip(voice_clip)

    if choice < 40:
        play_audio(man, "modified")
    else:
        play_audio(man, "original")

    score = tk.IntVar()
    waiter = tk.IntVar()
    score.set(0)

    commandframe = tk.Frame(root)
    commandframe.pack(side=tk.TOP)

    b19_button = tk.Button(commandframe, text="Score 1")
    b19_button["command"] = lambda: score.set(1)
    b19_button.pack(side=tk.RIGHT)

    b20_button = tk.Button(commandframe, text="Score 2")
    b20_button["command"] = lambda: score.set(2)
    b20_button.pack(side=tk.RIGHT)

    b21_button = tk.Button(commandframe, text="Score 3")
    b21_button["command"] = lambda:  score.set(3)
    b21_button.pack(side=tk.RIGHT)

    b22_button = tk.Button(commandframe, text="Score 4")
    b22_button["command"] = lambda:  score.set(4)
    b22_button.pack(side=tk.RIGHT)

    b23_button = tk.Button(commandframe, text="Score 5")
    b23_button["command"] = lambda:  score.set(5)
    b23_button.pack(side=tk.RIGHT)

    b24_button = tk.Button(commandframe, text="Confirm score")
    b24_button["command"] = lambda: waiter.set(1)
    b24_button.pack(side=tk.RIGHT)

    b24_button.wait_variable(waiter)
    commandframe.destroy()
    return ({
        "Clip": man.get_active_clip(),
        "PSNR": PSNR(man.get_original_signal(), man.get_working_signal(), man),
        "Compression": man.get_compression_mod(),
        "Frequency": man.get_frequency_mod(),
        "Bitdepth": man.get_bitdepth_mod(),
        "Score": score.get()
    })

def set_wait(flag):
    global waiting
    waiting = flag

def set_score(set):
    global score
    score = set

if __name__ == '__main__':
    man = Manager()
    root = tk.Tk()

    l1_text = tk.StringVar()
    l2_text = tk.StringVar()
    l3_text = tk.StringVar()
    l4_text = tk.StringVar()
    l5_text = tk.StringVar()
    labels = [l1_text, l2_text, l3_text, l4_text, l5_text]
    update_labels(labels, man)

    labelframe = tk.Frame(root)
    labelframe.pack(side=tk.TOP)

    figure, ax = plt.subplots(2, 1, figsize=(5, 4), dpi=150)
    ax[0].plot(man.get_original_signal())
    ax[1].plot(man.get_working_signal())

    # fig = plt.Figure(figsize=(5,4), dpi=100)

    canvas = FigureCanvasTkAgg(figure, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
    canvas.flush_events()

    freqframe = tk.Frame(root)
    freqframe.pack(side=tk.BOTTOM)

    quantframe = tk.Frame(root)
    quantframe.pack(side=tk.BOTTOM)

    compressframe = tk.Frame(root)
    compressframe.pack(side=tk.BOTTOM)

    fileframe = tk.Frame(root)
    fileframe.pack(side=tk.BOTTOM)

    playframe = tk.Frame(root)
    playframe.pack(side=tk.TOP)

    commandframe = tk.Frame(root)
    commandframe.pack(side=tk.TOP)

    b1_button = tk.Button(fileframe, text="Load guitar.wav")
    b1_button["command"] = lambda: [man.change_active_clip(guitar_clip),
                                    update_labels(labels, man),
                                    update_plots(ax, man)]
    b1_button.pack(side=tk.LEFT)

    b2_button = tk.Button(fileframe, text="Load orchestral.wav")
    b2_button["command"] = lambda: [man.change_active_clip(orchestral_clip), update_labels(labels, man),
                                    update_plots(ax, man)]
    b2_button.pack(side=tk.LEFT)

    b3_button = tk.Button(fileframe, text="Load voice.wav")
    b3_button["command"] = lambda: [man.change_active_clip(voice_clip), update_labels(labels, man),
                                    update_plots(ax, man)]
    b3_button.pack(side=tk.LEFT)

    b4_button = tk.Button(freqframe, text="Change frequency to 22khz")
    b4_button["command"] = lambda: [man.change_mod("frequency", 22000), update_labels(labels, man),
                                    update_plots(ax, man)]
    b4_button.pack(side=tk.RIGHT)

    b5_button = tk.Button(freqframe, text="Change frequency to 11khz")
    b5_button["command"] = lambda: [man.change_mod("frequency", 11000), update_labels(labels, man),
                                    update_plots(ax, man)]
    b5_button.pack(side=tk.RIGHT)

    b6_button = tk.Button(freqframe, text="Change frequency to 8khz")
    b6_button["command"] = lambda: [man.change_mod("frequency", 8000), update_labels(labels, man),
                                    update_plots(ax, man)]
    b6_button.pack(side=tk.RIGHT)

    b7_button = tk.Button(freqframe, text="Change frequency to 4khz")
    b7_button["command"] = lambda: [man.change_mod("frequency", 4000), update_labels(labels, man),
                                    update_plots(ax, man)]
    b7_button.pack(side=tk.RIGHT)

    b8_button = tk.Button(freqframe, text="Change frequency to 2khz")
    b8_button["command"] = lambda: [man.change_mod("frequency", 2000), update_labels(labels, man),
                                    update_plots(ax, man)]
    b8_button.pack(side=tk.RIGHT)

    b9_button = tk.Button(quantframe, text="Quantization to 8 bits")
    b9_button["command"] = lambda: [man.change_mod("bitdepth", 8), update_labels(labels, man),
                                    update_plots(ax, man)]
    b9_button.pack(side=tk.RIGHT)

    b10_button = tk.Button(quantframe, text="Quantization to 4 bits")
    b10_button["command"] = lambda: [man.change_mod("bitdepth", 4), update_labels(labels, man),
                                     update_plots(ax, man)]
    b10_button.pack(side=tk.RIGHT)

    b11_button = tk.Button(quantframe, text="Quantization to 2 bits")
    b11_button["command"] = lambda: [man.change_mod("bitdepth", 2), update_labels(labels, man),
                                     update_plots(ax, man)]
    b11_button.pack(side=tk.RIGHT)

    b12_button = tk.Button(compressframe, text="Compress a-LAW")
    b12_button["command"] = lambda: [man.change_mod("compression", "a-LAW"), update_labels(labels, man),
                                     update_plots(ax, man)]
    b12_button.pack(side=tk.RIGHT)

    b13_button = tk.Button(compressframe, text="Compress u-LAW")
    b13_button["command"] = lambda: [man.change_mod("compression", "u-LAW"), update_labels(labels, man),
                                     update_plots(ax, man)]
    b13_button.pack(side=tk.RIGHT)

    b14_button = tk.Button(compressframe, text="Compress ADPCM")
    b14_button["command"] = lambda: [man.change_mod("compression", "ADPCM"), update_labels(labels, man),
                                     update_plots(ax, man)]
    b14_button.pack(side=tk.RIGHT)

    b15_button = tk.Button(playframe, text="PLAY ORIGINAL")
    b15_button["command"] = lambda: play_audio(man, "original")
    b15_button.pack(side=tk.RIGHT)

    b16_button = tk.Button(playframe, text="PLAY MODIFIED")
    b16_button["command"] = lambda: play_audio(man, "modified")
    b16_button.pack(side=tk.RIGHT)

    b17_button = tk.Button(playframe, text="STOP")
    b17_button["command"] = lambda: press_button_stop()
    b17_button.pack(side=tk.RIGHT)

    b18_button = tk.Button(commandframe, text="Whole test")
    b18_button["command"] = lambda: whole_test(man)
    b18_button.pack(side=tk.RIGHT)

    l1 = tk.Label(labelframe, textvariable=l1_text)
    l1.pack()

    l2 = tk.Label(labelframe, textvariable=l2_text)
    l2.pack()

    l3 = tk.Label(labelframe, textvariable=l3_text)
    l3.pack()

    l4 = tk.Label(labelframe, textvariable=l4_text)
    l4.pack()

    l5 = tk.Label(labelframe, textvariable=l5_text)
    l5.pack()

    root.mainloop()

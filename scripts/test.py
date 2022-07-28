import csv
from datetime import datetime
import json
import glob
import os
import time
import sys
from tkinter import E
from utils import *
import random
import string
import threading
import re
from tqdm import tqdm
import dateutil.parser
import logging
import random
import matplotlib.pyplot as plt
import numpy as np
from analysis_utils import *


def analyze():
    global threads, headers
    data = get_json(
        "C:/Users/Ibrahim.Moghul/Desktop/Data Analysis Scripts/OUTPUT/Chambers/data.json")
    # print(data[list(
    # data.keys())[0]])
    with open("C:/Users/Ibrahim.Moghul/Desktop/Data Analysis Scripts/OUTPUT/Chambers/test.csv", 'w') as out:
        writer = csv.writer(out)
        dataKeys = list(data.keys())
        random.shuffle(dataKeys)
        bar = tqdm(dataKeys)
        for fn in bar:
            interest = data[fn]

            t = interest["Test Time"]
            watts = interest["Watt"]
            wattHrs = watts.copy()
            # for i, v in enumerate(wattHrs):
            #     wattHrs[i] = (v*t[i])//3600
            # watts = smoothNoiseChunks(t,watts,2,1,1)

            origWatts = watts.copy()
            watts = smoothNoiseChunks(t, watts)
            dwattsdt = dt(t, watts)
            wattsPeaks = getCleanPeaks(t, watts)
            wattsPeaksDirty = getPeaks(t,watts)
            writer.writerow(["Time (s): "]+t)
            writer.writerow(["Original Watts: "] + [str(i) for i in origWatts])
            writer.writerow(["Watts: "]+[str(i) for i in watts])
            # writer.writerow(
            #     ["Watts Peaks:"]+['1' if i in wattsPeaks else '' for i, _ in enumerate(watts)])
            # writer.writerow(["dwatts/dt",""]+[str(i) for i in dt(t, watts)])
            writer.writerow(["-"*len(t)])


            plt.figure()

            # plt.subplot(211)
            # plt.plot(t, origWatts, "paleturquoise")
            # plt.plot(t, watts, "black")
            # plt.plot([t[i] for i in wattsPeaks], [watts[i]
            #          for i in wattsPeaks], "o")
            # plt.title("watts")


            

            # plt.subplot(212)
            # plt.plot(t[1:], dwattsdt, "brown")
            # plt.title("dwatts/dt")

            # plt.show()

            w = plt.subplot(211)
            w.plot(t, interest["Watt"], "paleturquoise")
            w.plot(t, origWatts, "turquoise")
            w.plot(t, watts, "b")
            for i in getNoiseChunks(t,origWatts):
                plt.plot( t[i[0]:i[1]] ,origWatts[i[0]:i[1]],"black")
            w.scatter([t[i] for i in wattsPeaksDirty], [watts[i]
                     for i in wattsPeaksDirty], c="red")
            w.scatter([t[i] for i in wattsPeaks], [watts[i]
                     for i in wattsPeaks], c="green")

            
            plt.title("watts")
            

            dw = plt.subplot(212,sharex = w)
            plt.title("dwatts/dt")
            dw.plot(t[1:], dwattsdt, "o")

            plt.show()


def get_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)


analyze()
# x = np.linspace(0,2*np.pi,100)
# x+=x[-1]*10
# y = np.sin(x) + np.random.random(100) * 0.8
# y+=y[-1]*10
# def smooth(y, box_pts):
#     box = np.ones(box_pts)/box_pts
#     y_smooth = np.convolve(y, box, mode='same')
#     return y_smooth

# plt.plot(x, y,'b')
# plt.plot(x, smooth(y,3), 'orange', lw=2)
# plt.plot(x, smooth(y,19), 'black', lw=2)
# plt.plot(x[10:-10], smooth(y,3)[10:-10], 'r-', lw=2)
# plt.plot(x[10:-10], smooth(y,19)[10:-10], 'g-', lw=2)

# plt.show()

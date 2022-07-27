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
            for i, v in enumerate(wattHrs):
                wattHrs[i] = (v*t[i])//3600

            # origwattHrs = wattHrs.copy()
            # wattHrs = getSmooth(t, wattHrs)
            # dwattHrsdt = getSmooth(t, dt(t, wattHrs))

            origWatts = watts.copy()
            watts = getSmooth(t, watts)
            dwattsdt = getSmooth(t, dt(t, watts))

            # wattHrsPeaks = getPeaks(t, wattHrs)
            wattsPeaks = getPeaks(t, watts)

            writer.writerow(["Time (s): "]+t)
            writer.writerow(["Original Watts: "] + [str(i) for i in origWatts])
            writer.writerow(["Watts: "]+[str(i) for i in watts])
            writer.writerow(
                ["Watts Peaks:"]+['1' if i in wattsPeaks else '' for i, _ in enumerate(watts)])
            writer.writerow(["dwatts/dt",""]+[str(i) for i in dt(t, watts)])

            plt.figure()

            # plt.subplot(221)
            # plt.plot(t, origwattHrs, "lightcoral")
            # plt.plot(t, wattHrs, "r")
            # plt.plot([t[i] for i in wattHrsPeaks], [wattHrs[i]
            #          for i in wattHrsPeaks], "o")
            # plt.title("wattHrs")

            plt.subplot(211)
            plt.plot(t, origWatts, "paleturquoise")
            # plt.plot(t, origWatts, "o")

            plt.plot(t,smoothNoiseChunks(t,origWatts),"black")
            for i in getNoiseChunks(t,origWatts):
                plt.plot( t[i[0]:i[1]] ,origWatts[i[0]:i[1]],"b")
            # plt.plot(t, watts, "b")
            # plt.plot([t[i] for i in wattsPeaks], [watts[i]
            #          for i in wattsPeaks], "o")
            plt.title("watts")
            writer.writerow(["-"*len(t)])

            # plt.subplot(223)
            # plt.plot(t[1:], dwattHrsdt, "g")
            # plt.title("dwattHrs/dt")

            plt.subplot(212)
            plt.plot(t[1:], dwattsdt, "brown")
            plt.title("dwatts/dt")

            plt.show()
            # print(data[fn])

            # if(i>100):break'


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

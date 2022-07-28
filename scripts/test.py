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


            iterations = 4
            subplots = [200+iterations*10+j+1 for j in range(2*iterations)]
            for iter in getIterable(range(iterations)):
                origWatts = watts.copy()
                watts = smoothNoiseChunks(t, watts)
                dwattsdt = dt(t, watts)
                wattsPeaksDirty = getPeaks(t,watts)
                wattsPeaks = getCleanPeaks(t, watts,wattsPeaksDirty)
                # writer.writerow(["Time (s): "]+t)
                # writer.writerow(["Original Watts: "] + [str(i) for i in origWatts])
                # writer.writerow(["Watts: "]+[str(i) for i in watts])
                # writer.writerow(
                #     ["Watts Peaks:"]+['1' if i in wattsPeaks else '' for i, _ in enumerate(watts)])
                # writer.writerow(["dwatts/dt",""]+[str(i) for i in dt(t, watts)])
                # writer.writerow(["-"*len(t)])

                plt.figure(fn)
                w = plt.subplot(subplots[iter])#(211)
                w.plot(t, interest["Watt"], "paleturquoise")
                w.plot(t, origWatts, "turquoise")
                w.plot(t, watts, "b")
                # w.scatter(t, watts, c="blue")
                for i in getNoiseChunks(t,origWatts):
                    plt.plot( t[i[0]:i[1]] ,origWatts[i[0]:i[1]],"black")
                w.scatter([t[i] for i in wattsPeaksDirty], [watts[i]
                        for i in wattsPeaksDirty], c="red")
                w.scatter([t[i] for i in wattsPeaks], [watts[i]
                        for i in wattsPeaks], c="green")
                plt.title("watts %d"%(iter+1))
                

                p = plt.subplot(subplots[iter+iterations],sharex = w)
                plt.title("peaks %d"%(iter+1))
                peaksT = [t[i] for i in wattsPeaksDirty]
                peaksData = [watts[i]for i in wattsPeaksDirty]
                p.plot(peaksT, peaksData,"red")
                peaksData = smoothNoiseChunks(peaksT,peaksData)
                p.plot(peaksT,peaksData)
                peaksPeaksDirty = getPeaks(peaksT,peaksData)
                peaksPeaks = getCleanPeaks(peaksT, peaksData,peaksPeaksDirty)
                p.scatter([peaksT[i] for i in peaksPeaksDirty], [peaksData[i]
                        for i in peaksPeaksDirty], c="red")
                p.scatter([peaksT[i] for i in peaksPeaks], [peaksData[i]
                        for i in peaksPeaks], c="green")

            plt.show()


def get_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)


analyze()
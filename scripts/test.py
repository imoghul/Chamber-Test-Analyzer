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

            iterations = 4
            subplots = [200+iterations*10+j+1 for j in range(2*iterations)]
            for iter in getIterable("Iterations",range(iterations)):
                origWatts = watts.copy()
                noiseChunks = getNoiseChunks(t,origWatts)
                watts = smoothNoiseChunks(t, watts,noiseChunks)
                wattsPeaksDirty = getPeaks(t,watts)
                wattsPeaks = getCleanPeaks(t, watts,wattsPeaksDirty)

                plt.figure(fn)
                w = plt.subplot(subplots[iter])#(211)
                w.plot(t, interest["Watt"], "paleturquoise")
                w.plot(t, origWatts, "turquoise")
                w.plot(t, watts, "blue")
                for i in noiseChunks:
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
                peaksData = smoothNoiseChunks(peaksT,peaksData,getNoiseChunks(peaksT,peaksData))
                p.plot(peaksT,peaksData)
                peaksPeaksDirty = getPeaks(peaksT,peaksData)
                peaksPeaks = getCleanPeaks(peaksT, peaksData,peaksPeaksDirty)
                p.scatter([peaksT[i] for i in peaksPeaksDirty], [peaksData[i]
                        for i in peaksPeaksDirty], c="red")
                p.scatter([peaksT[i] for i in peaksPeaks], [peaksData[i]
                        for i in peaksPeaks], c="green")

            
            writer.writerow(["Time (s): "]+t)
            writer.writerow(["Original Watts: "] + [str(i) for i in interest["Watt"]])
            writer.writerow(["Refined Watts: "]+[str(i) for i in watts])
            writer.writerow(
                ["Watts Peaks:"]+['1' if i in wattsPeaks else '' for i, _ in enumerate(watts)])
            writer.writerow(["Peaks"]+[peaksData[i] if v in t else "" for i,v in enumerate(peaksT)])
            writer.writerow(["Peaks Peaks"]+[peaksData[i] if (v in t and i in peaksPeaksDirty) else "" for i,v in enumerate(peaksT)])
            outTimeline = ["Timeline:"]
            for i,v in enumerate(getTimeline(t,peaksPeaksDirty)):
                for j in range((t.index(peaksT[i+1]) if i!=(len(peaksT)-1) else len(peaksT)-1)-t.index(peaksT[i])):outTimeline.append(v)
            writer.writerow(outTimeline)
            writer.writerow(["-"*len(t)])

            plt.show()


def get_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)


analyze()
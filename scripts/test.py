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
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import numpy as np
from analysis_utils import *
from scipy.signal import savgol_filter


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
            # for iter in getIterable("Iterations",range(iterations)):
            origWatts = watts.copy()#smooth(t,watts.copy(),sigma = 1)
            # origWatts = savgol_filter(origWatts, 101, 2)
            noiseChunks = getNoiseChunks(t,origWatts)
            watts = smoothNoiseChunks(t, watts,noiseChunks)
            # watts = smoothNoiseChunks(t,watts,getNoiseChunks(t,watts))
            wattsPeaksDirty = getPeaks(t,watts)
            wattsPeaks = getCleanPeaks(t, watts,wattsPeaksDirty)

            plt.figure(fn)
            grid = plt.GridSpec(2, iterations, wspace =0.3, hspace = 0.3)
            
            w = plt.subplot(grid[0, 0:2])#plt.subplot(2,iterations,1)
            w.plot(t, interest["Watt"], "paleturquoise")
            w.plot(t, origWatts, "turquoise")
            w.plot(t, watts, "blue")
            for i in noiseChunks:
                plt.plot( t[i[0]:i[1]+1] ,origWatts[i[0]:i[1]+1],"black")
            w.scatter([t[i] for i in wattsPeaksDirty], [watts[i]
                    for i in wattsPeaksDirty], c="red")
            w.scatter([t[i] for i in wattsPeaks], [watts[i]
                    for i in wattsPeaks], c="green")
            plt.title("watts")#("watts %d"%(iter+1))

            e = plt.subplot(grid[0, 2:4],sharex = w,sharey = w)#plt.subplot(2,iterations,3)
            e.plot(t, watts, "blue")
            plt.title("processed watts")
                
            for iter in getIterable("Iterations",range(iterations)):
                wattsPeaksDirty = getPeaks(t,watts)
                wattsPeaks = getCleanPeaks(t, watts,wattsPeaksDirty)
                p = plt.subplot(grid[1,iter])#plt.subplot(subplots[iter+iterations],sharex = w)
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
            writer.writerow(["Watts Peaks Refined:"]+[watts[i] if i in wattsPeaks else '' for i, _ in enumerate(watts)])
            writer.writerow(["Watts Peaks Unrefined:"]+[watts[i] if i in wattsPeaksDirty else '' for i, _ in enumerate(watts)])
            writer.writerow(["Peaks Peaks Dirty:"]+[watts[i] if i in peaksPeaksDirty else '' for i, _ in enumerate(watts)])
            outTimeline = ["Timeline:"]
            timeline = getTimeline(t,watts,peaksPeaksDirty)
            for i,v in enumerate(timeline):
                outTimeline.append(v if timeline[i-1] != v else "")
                for j in range(((t.index(peaksT[i+1]) if i!=(len(peaksT)-1) else len(peaksT)-1)-t.index(peaksT[i]))-1):outTimeline.append("")
            writer.writerow(outTimeline)
            writer.writerow(["-"*len(t)])

            plt.show()


def get_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)


analyze()
print("Importing Libraries")
import sys
sys.settrace
import csv
from datetime import datetime
import json
import glob
import os
import time
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
print("Finished")

def analyze(fn,writer):
    interest = get_json(fn)#data[fn]

    t = interest["Test Time"]
    watts = interest["Watt"]

    iterations = 3
    showFrom = 1
    showFrom-=1
    plt.figure(fn)
    grid = plt.GridSpec(iterations-showFrom, 4, wspace =0.3, hspace = 0.3)
    for iter in getIterable("Iterations",range(iterations)):
        origWatts = watts.copy()#smooth(t,watts.copy(),sigma = 1)
        # origWatts = savgol_filter(origWatts, 101, 2)
        noiseChunks = getNoiseChunks(t,origWatts)
        watts = smoothNoiseChunks(t, watts,noiseChunks)
        linParts = getLinearParts(t,origWatts)#getLinParts_LinReg(t,origWatts)
        # watts = straightenLinearParts(t,watts,linParts)
        # watts = smoothNoiseChunks(t,watts,getNoiseChunks(t,watts))
        wattsPeaksDirty = getInterestPoints(t,watts)
        wattsPeaks = getCleanInterests(t, watts,wattsPeaksDirty)

        if(iter>=showFrom):

            e = plt.subplot(grid[iter-showFrom, 0:2]) if iter==showFrom else plt.subplot(grid[iter-showFrom, 0:2],sharex=e,sharey = e)#plt.subplot(2,iterations,1)#plt.subplot(grid[iter-showFrom, 1:3],sharex = w,sharey = w)
            e.plot(t, interest["Watt"], "paleturquoise")
            # e.plot(t,straightenLinearParts(t,watts,linParts),"black")
            e.plot(t, watts, "blue")
            for i in linParts:
                e.plot( t[i[0]:i[1]+1] ,watts[i[0]:i[1]+1],color="green",linewidth = 2)
            plt.title("Processed Watts")


            timelineData = range(len(watts))#([0] if 0 not in wattsPeaksDirty else [])+wattsPeaksDirty.copy()
            tP = plt.subplot(grid[iter-showFrom, 2:4],sharex = e,sharey = e)
            tP.plot(t, interest["Watt"], "paleturquoise")
            timeline = getTimeline(t,watts,timelineData)
            for i,v in enumerate(timelineData[:-1]):
                # if(i==0):continue
                color = "black"
                if(timeline[i]=="pulling down"):
                    color = "red"
                elif (timeline[i]=="cooling off"):
                    color = "green"
                tP.plot(t[v:timelineData[i+1]+1],watts[v:timelineData[i+1]+1],color = color)
            plt.title("Watts Timeline")
        


    writer.writerow(["Time (s): "]+t)
    writer.writerow(["Original Watts: "] + [str(i) for i in interest["Watt"]])
    writer.writerow(["Ambient Temperature: "] + [str(i) for i in interest["Ambients"]])
    writer.writerow(["Refined Watts: "]+[str(i) for i in watts])
    writer.writerow(["Watts Peaks Refined:"]+[watts[i] if i in wattsPeaks else '' for i, _ in enumerate(watts)])
    writer.writerow(["Watts Peaks Unrefined:"]+[watts[i] if i in wattsPeaksDirty else '' for i, _ in enumerate(watts)])
    outTimeline = ["Timeline:"]
    for i,v in enumerate(timeline):
        outTimeline.append(v if timeline[i-1] != v or i==0 else "")
        for j in range((( (timelineData[i+1]-timelineData[i])) ) -1 ):outTimeline.append("")
    writer.writerow(outTimeline)
    writer.writerow(["-"*len(t)])
    plt.show()

            

def get_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)




print("Getting data")
dataFiles = glob.glob("L:/Engineering_Services/View/PerformanceTest/rts summary/data/*.json")
# print(dataFiles)
print("Finished")
# print(data[list(
# data.keys())[0]])
with open("C:/Users/Ibrahim.Moghul/Desktop/Data Analysis Scripts/OUTPUT/Chambers/test.csv", 'w') as out:
    writer = csv.writer(out)
    dataKeys = dataFiles#list(data.keys())
    random.shuffle(dataKeys)
    bar = tqdm(dataKeys)
    for fn in bar:
        analyze(fn,writer)
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
import matplotlib.pyplot as plt
import numpy as np
from analysis_utils import *

def analyze():
    global threads, headers
    data = get_json("C:/Users/Ibrahim.Moghul/Desktop/Data Analysis Scripts/OUTPUT/Chambers/data.json")
    # print(data[list(
    # data.keys())[0]])
    bar = tqdm(data)
    for fn in bar:
        interest = data[fn]
        if("P Temp chamber" not in interest):
            continue
        if(-999 in interest["P Temp chamber"]): continue

        t = interest["Test Time"]
        ptemp = interest["P Temp chamber"]
        watts = interest["Watt"]
        phps = interest["PHPs"]

        # ptemp = 10000*[ptemp[0]] + ptemp + 10000*[ptemp[-1]]
        # t = 10000*[t[0]] + t + 10000*[t[-1]]
        # print(ptemp)
        print(fn)
        bpoints = len(t)//10
        plt.figure()
        plt.subplot(221)
        plt.plot(t,ptemp,"r")
        plt.subplot(222)
        smoov = smooth(ptemp,bpoints)
        smoov = smooth(smoov,bpoints)

        # smoovdt = smooth(dt(t,ptemp),50)
        dtsmoov = dt(t,smoov)
        smooovdtsmoov = smooth(dt(t,smoov),bpoints)
        plt.plot(t,smoov,"brown")
        plt.plot(t[bpoints:-bpoints],smoov[bpoints:-bpoints],"b")
        plt.subplot(223)
        # plt.plot(t[50:-50],smoovdt[50:-50],"g")
        plt.plot(t,smooovdtsmoov,"blue")
        plt.plot(t[bpoints**1:-(bpoints**1)],smooovdtsmoov[bpoints**1:-(bpoints**1)],"g")
        plt.subplot(224)
        plt.plot(t[bpoints:-bpoints],dtsmoov[bpoints:-bpoints],"orange")
        plt.show()
        # print(data[fn])
        
        # if(i>100):break'


def get_json(filename):
    with open(filename,'r') as file:
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
import enum
import threading
import numpy as np
import statistics
from utils import *
import statsmodels.api as sm
import scipy
import os
from tqdm import tqdm

progBars = True

def getIterable(title,d):
    return tqdm(d,desc=title,leave=False) if progBars else d

def dt(time, data):
    data = data.copy()
    if(len(time)!=len(data)):
        raise Exception("incorrect sizes")
    return np.diff(data)/np.diff(time)

def getPeaks(t, data):
    res = []
    diff = dt(t, data)
    for i, v in  getIterable("Calculating maxima/minima",enumerate(diff)):
        if(v == 0 or (i != 0 and v*diff[i-1] <= 0)):
            res.append(i)

    return res

def getCleanPeaks(t,data,peaks,errorMax=.05):
    peaks = peaks.copy()
    rm = []
    for i,p in getIterable("Cleaning up maxima/minima",enumerate(peaks)):
        try:
            if(abs(data[p-1]-data[p])<=errorMax and abs(data[p+1]-data[p])<=errorMax):
                rm.append(p)
        except:
            pass
    
    for i in rm:
        peaks.remove(i)
    return peaks

def smooth(arr, span):
    cumsum_vec = np.cumsum(arr)
    moving_average = (cumsum_vec[2 * span:] -
                      cumsum_vec[:-2 * span]) / (2 * span)

    # The "my_average" part again. Slightly different to before, because the
    # moving average from cumsum is shorter than the input and needs to be padded
    front, back = [np.average(arr[:span])], []
    for i in range(1, span):
        front.append(np.average(arr[:i + span]))
        back.insert(0, np.average(arr[-i - span:]))
    back.insert(0, np.average(arr[-2 * span:]))
    return np.concatenate((front, moving_average, back))


def getSpan(t, y):
    span = len(getPeaks(t, y))//50
    if(span < 2):
        span = 2
    return span

def getIterations(t,y):
    try:
        iterations = round(5/statistics.stdev(y))
    except:
        iterations = 0

    if(iterations < 5):
        iterations = 5
    if(iterations > 5000):
        iterations = 5000
    return iterations

def getSmooth(t, y, iterations=None, span=None):
    if(iterations == None):
        iterations = getIterations(t,y)
    if(span == None):
        span = getSpan(t, y)
    if(len(y)<2*span): return y
        # if(len(y)):return len(y)*[average(y)]
        # else:return y
    smoov = smooth(y, span)
    for i in getIterable("Smoothing",range(iterations-1)):
        smoov = smooth(smoov, span)
    return smoov




def getNoiseChunks(t,y,margin=1.5): # returns [[a,b],[c,d],[e,f]...]
    chunks = []
    temp = []
    for i,v in getIterable("Calculating noisy chunks",enumerate(y[:-1])):
        if(abs(v-y[i+1])<=margin):
            if(temp==[]):temp = [i,i+1]
            else:
                temp[1] = i+1
        else:
            if(len(temp)>1):chunks.append(temp)
            temp = []
    if(len(temp)>1):chunks.append(temp)
    return chunks
def smoothNoiseChunks(t,y,chunks,margin = 1.5,iterations = None, span = None):
    y = y.copy()
    threads = []
    for chunk in chunks:#getNoiseChunks(t,y,margin):#getIterable("Smoothing noisy chunks",getNoiseChunks(t,y,margin)):
        def run(y):
            y[chunk[0]:chunk[1]] = getSmooth(t[chunk[0]:chunk[1]],y[chunk[0]:chunk[1]],iterations,span)
        threads.append(threading.Thread(target = run,args=[y]))
    runThreads(threads,100,"Smoothing noisy chunks",leave=False)
    return y



def getTimeline(t,peaks):
    res = []
    for i,v in enumerate(peaks[:-1]):
        diff = (peaks[i+1]-v)/(t[i+1]-t[i])
        if diff>2:
            res.append("pulling down")
        elif diff<-2:
            res.append("cooling off")
        else:
            res.append("steady state")
    return res
import enum
import threading
import numpy as np
import statistics
from utils import *
from scipy.ndimage.filters import gaussian_filter1d
import scipy
import os
from sklearn.neighbors import KNeighborsRegressor
from tqdm import tqdm

progBars = True

def getIterable(title,d):
    return tqdm(d,desc=title,leave=False) if progBars else d

def dt(time, data):
    data = data.copy()
    if(len(time)!=len(data)):
        raise Exception("incorrect sizes")
    return np.diff(data)/np.diff(time)

def getPeaks(t, data): # returns list of indexes
    res = []
    if(not len(data)):return []
    if(len(data)<=3):return [data.index(max(data))]
    # diff = dt(t, data)
    # for i, v in  getIterable("Calculating maxima/minima",enumerate(diff)):
    #     if(v == 0 or (i != 0 and v*diff[i-1] <= 0)):
    #         res.append(i)
    for i,_ in getIterable("Calculating maxima/minima",enumerate(data)):
        if(i==0 or i == len(data)-1):continue
        if(data[i]>data[i-1] and data[i]>data[i+1]) or (data[i]<data[i-1] and data[i]<data[i+1]):
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

def smooth(t,arr, sigma):
    # clf = KNeighborsRegressor(n_neighbors=100, weights='uniform')
    # clf.fit(df.index.values[:, np.newaxis], 
    #         df.iloc[:, 0])
    # y_pred = clf.predict(df.index.values[:, np.newaxis])
    # return y_pred
    # # 
    return gaussian_filter1d(arr, sigma=sigma)

def getSigma(t,y):
    # try:
    #     return 10/average([abs(v-y[i-1]) for i,v in enumerate(y)])
    # except:
        return 1

def getIterations(t,y):
    return 20
    try:
        iterations = round(30/statistics.stdev(y))
    except:
        iterations = 0

    if(iterations < 5):
        iterations = 5
    if(iterations > 100):
        iterations = 100
    return iterations

def getSmooth(t, y, iterations=None,sigma = None):
    if(iterations == None):
        iterations = getIterations(t,y)
    if(sigma ==  None):
        sigma = getSigma(t,y)
    smoov = smooth(t,y,sigma = sigma)
    for i in getIterable("Smoothing",range(iterations-1)):
        smoov = smooth(t,smoov,sigma = sigma)
    return smoov




def getNoiseChunks(t,y,margin=10,sumMargin = 5): # returns [[a,b],[c,d],[e,f]...]
    chunks = []
    temp = []
    diff = dt(t,y)
    for i,v in getIterable("Calculating noisy chunks",enumerate(y[:-1])):
        if abs(v-y[i+1])<=margin:# and (all([abs(v-j)<=sumMargin for j in y[temp[0]:temp[1]+1]]) if len(temp) else True):
            if(temp==[]):temp = [i,i+1]
            else:
                temp[1] = i+1
        else:
            if(len(temp)>1):chunks.append(temp)
            temp = []
    if(len(temp)>1):chunks.append(temp)
    return chunks
def smoothNoiseChunks(t,y,chunks,iterations = None, sigma = None):
    y = y.copy()
    for chunk in chunks:
        y[chunk[0]:chunk[1]+1] = getSmooth(t[chunk[0]:chunk[1]+1],y[chunk[0]:chunk[1]+1],iterations = iterations,sigma = sigma)
    # y = getSmooth(t,y,10,sigma=1)
    return y



def getTimeline(t,y,peaks):
    res = []
    for i in peaks[:-1]:
        diff = (y[i+1]-y[i])/(t[i+1]-t[i])
        if diff>1e-6:
            res.append("pulling down")
        elif diff<-1e-6:
            res.append("cooling off")
        else:
            res.append("steady state")
    return res
import enum
from linecache import getline
from pydoc import plainpager
import threading
from xml.etree.ElementInclude import include
import numpy as np
import statistics
from utils import *
from scipy.ndimage.filters import gaussian_filter1d
import scipy
import os
from sklearn.neighbors import KNeighborsRegressor
from tqdm import tqdm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from constants import *
import matplotlib.pyplot as plt

progBars = True


def getIterable(title, d):
    return tqdm(d, desc=title, leave=False) if progBars else d


def dt(time, data):
    data = data.copy()
    if(len(time) != len(data)):
        raise Exception("incorrect sizes")
    try:
        return np.diff(data)/np.diff(time)
    except:
        print(len(data), len(time), data, time)
        try:
            print("data diff: ", np.diff(data))
        except:
            pass
        try:
            print("time diff: ", np.diff(time))
        except:
            pass
        exit()


def getLinearParts(time, data, margin=LinearChunksMargin, regressionScore = LinearChunksRegressionScore):  # 5e-7):
    d1 = dt(time, data)
    d2 = dt(time[1:], d1)
    chunks = []
    temp = []
    for i, v in getIterable("Finding linear parts", enumerate(data)):
        if(i < 2):
            continue
        if abs(d2[i-2]) <= margin:
        # if (getLinRegScore(time[temp[0]:temp[1]+1],data[temp[0]:temp[1]+1])>regressionScore if len(temp) else True):
            if(temp == []):
                temp = [i, i+1]
            else:
                temp[1] = i+1
        else:
            if(len(temp) > 1 and temp[1]-temp[0] > 2):
                chunks.append([temp[0], temp[1]-1])
            temp = []
    if(len(temp) > 1 and temp[1]-temp[0] > 2):
        chunks.append([temp[0], temp[1]-1])
    return chunks


def getPeaks(t, data):  # returns list of indexes
    res = []
    if(not len(data)):
        return []
    if(len(data) <= 3):
        return [data.index(max(data))]
    # diff = dt(t, data)
    # for i, v in  getIterable("Calculating maxima/minima",enumerate(diff)):
    #     if(v == 0 or (i != 0 and v*diff[i-1] <= 0)):
    #         res.append(i)
    for i, _ in getIterable("Calculating maxima/minima", enumerate(data)):
        if(i == 0 or i == len(data)-1):
            continue
        if(data[i] > data[i-1] and data[i] > data[i+1]) or (data[i] < data[i-1] and data[i] < data[i+1]):
            res.append(i)
    return res


def getInterestPoints(t, data):
    peaks = getPeaks(t, data)
    _linParts = getLinearParts(t, data)#+getLinParts_LinReg(t,data)
    linParts = [i[0] for i in _linParts] + [i[1] for i in _linParts]
    res = []
    for i in getIterable("Calculating Points of Interest",peaks + linParts):
        if i not in res:
            res.append(i)
    res.sort()
    return res


def getCleanInterests(t, data, peaks, errorMax=InterestsBounceMax):
    peaks = peaks.copy()
    rm = []
    for i, p in getIterable("Cleaning up maxima/minima", enumerate(peaks)):
        try:
            if(abs(data[p-1]-data[p]) <= errorMax and abs(data[p+1]-data[p]) <= errorMax):
                rm.append(p)
        except:
            pass

    for i in rm:
        peaks.remove(i)
    return peaks


def smooth(t, arr, sigma):
    # clf = KNeighborsRegressor(n_neighbors=100, weights='uniform')
    # clf.fit(df.index.values[:, np.newaxis],
    #         df.iloc[:, 0])
    # y_pred = clf.predict(df.index.values[:, np.newaxis])
    # return y_pred
    # #
    return gaussian_filter1d(arr, sigma=sigma)


def getSigma(t, y):
    sigma = SigmaHardMin
    try:
        sigma = (max(y)-min(y))/SigmaRangeDivisor
    except:
        pass

    sigma = max(SigmaHardMin, sigma)

    return min(sigma, SigmaHardMax)


def getIterations(t, y):
    # return 25
    try:
        iterations = round(IterationsCalculationConstant/statistics.stdev(y))
    except:
        iterations = 0

    if(iterations < IterationsHardMin):
        iterations = IterationsHardMin
    if(iterations > IterationsHardMax):
        iterations = IterationsHardMax
    return iterations


def getSmooth(t, y, iterations=None, sigma=None, maxError = SmoothnessMaxError):
    if(iterations == None):
        iterations = getIterations(t, y)
    if(sigma == None):
        sigma = getSigma(t, y)
    
    smoov = smooth(t, y, sigma=sigma)
    for i in getIterable("Smoothing", range(iterations-1)):
        smoov = smooth(t, smoov, sigma=sigma)
    
    while(max([abs(v-y[i]) for i,v in enumerate(smoov)])>maxError and sigma>SigmaHardMin):
        sigma-=.1
        smoov = smooth(t, y, sigma=sigma)
        for i in getIterable("Smoothing", range(iterations-1)):
            smoov = smooth(t, smoov, sigma=sigma)
        
    return smoov


def getNoiseChunks(t, y, margin=NoiseChunksMargin, minLen=NoiseChunksMinLen):  # returns [[a,b],[c,d],[e,f]...]
    chunks = []
    temp = []
    diff = dt(t, y)
    for i, v in getIterable("Calculating noisy chunks", enumerate(y[:-1])):
        # if(len(temp)):
        #     print(getLinRegScore(t[temp[0]:temp[1]+1],y[temp[0]:temp[1]+1]))
        # and (all([abs(v-j)<=sumMargin for j in y[temp[0]:temp[1]+1]]) if len(temp) else True):
        if abs(v-y[i+1]) <= margin:
            if(temp == []):
                temp = [i, i+1]
            else:
                temp[1] = i+1
        else:
            if(len(temp) > 1 and temp[1]-temp[0] > minLen):
                chunks.append(temp)
            temp = []
    if(len(temp) > 1 and temp[1]-temp[0] > minLen):
        chunks.append(temp)
    return chunks


def smoothNoiseChunks(t, y, chunks, iterations=None, sigma=None):
    y = y.copy()
    for chunk in getIterable("Smoothing Chunks",chunks):
        y[chunk[0]:chunk[1]+1] = getSmooth(t[chunk[0]:chunk[1]+1],
                                           y[chunk[0]:chunk[1]+1], iterations=iterations, sigma=sigma)
    # y = getSmooth(t,y,10,sigma=1)
    return y


def straightenLinearParts(t, y, chunks):
    y = y.copy()
    for chunk in chunks:
        if(chunk[1]-chunk[0] == 0):
            continue
        if(chunk[1] == len(y)):
            chunk[1] -= 1

        patch = y[chunk[0]:chunk[1]+1]
        # print(len(y),len(t),chunk[0],chunk[1])
        slope = (patch[-1]-patch[0])/(t[chunk[1]]-t[chunk[0]])
        # print(slope)

        for i, v in enumerate(patch):
            if(i == 0):
                continue
            patch[i] = patch[i-1]+slope*(t[chunk[0]+i]-t[chunk[0]+i-1])
        y[chunk[0]:chunk[1]+1] = patch
    return y

# peaks should be list of indexes in t and y


def getTimeline(t, y, peaks):
    res = []
    for i, v in getIterable("Generating Timeline",enumerate(peaks[:-1])):
        diff = (y[peaks[i+1]]-y[v])/(t[peaks[i+1]]-t[v])
        if diff > PulldownRate:
            res.append("pulling down")
        elif diff < CoolingRate:
            res.append("cooling off")
        else:
            res.append("steady state")
    return res


def getLinRegScore(t,y):
    # time = []
    # for i,t in enumerate(t):
    #     time.append([t])
    # time = np.array(time)
    # data = np.array(y)
    # # time = np.hstack((time,time*time))
    # lin_reg = LinearRegression()
    # lin_reg.fit(time, data)
    # return lin_reg.score(time, data)

    
    X = []
    for i,t in enumerate(t):
        X.append([t])
    X = np.array(X)
    # X = np.hstack((X, X*X))
    regressor = LinearRegression().fit(X, y)
    return r2_score(regressor.predict(X), y)



def getLinParts_LinReg(t,y,regScore = LinearChunksLinRegRegressionScore):
    chunks = []
    start = 0
    while start<len(y):
        end = start+1
        while end<len(y):
            # print(end)
            if(getLinRegScore(t[start:end+1],y[start:end+1])>=regScore):
                end+=1
            else:break
        chunk = start,min(end,len(y)-1)
        if(abs(chunk[1]-chunk[0])>1):chunks.append(chunk)
        start = end
    print(chunks)
    return chunks
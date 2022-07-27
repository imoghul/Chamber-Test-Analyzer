import enum
import numpy as np
import statistics
import statsmodels.api as sm
import scipy

def dt(time, data):
    res = []
    for i, v in enumerate(data):
        if i == 0:
            continue
        res.append((v-data[i-1])/(float(time[i])-float(time[i-1])))
    return res


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
    # return scipy.signal.savgol_filter(arr, span * 2 + 1, 0)


def getSpan(t, y):
    span = len(getPeaks(t, y))//50
    if(span < 5):
        span = 5
    return 2#span

def getIterations(t,y):
    try:
        # len(getPeaks(t,y))//100
        iterations = round(5/statistics.stdev(y))
    except:
        iterations = 0

    # iterations*=50
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
    smoov = smooth(y, span)
    for i in range(iterations-1):
        smoov = smooth(smoov, span)
    return smoov


def getPeaks(t, data):
    res = []
    diff = dt(t, data)
    for i, v in enumerate(diff):
        if(v == 0 or (i != 0 and v*diff[i-1] < 0)):
            res.append(i)

    # clean up bouncing
    bounces = []
    for i, v in enumerate(res[1:]):
        if(v == res[i-1]+1):
            bounces.append(v)
    for i in bounces:
        res.remove(i)
    return res


def getNoiseChunks(t,y,margin = 2): # returns [[a,b],[c,d],[e,f]...]
    marginChunks = []
    peaks = getPeaks(t,y)
    temp = []
    currChunk = []
    for i,v in enumerate(y):
        currChunk.append(v)
        if(all([abs(j-v)<=margin for j in currChunk[0:-1]])):#(i!=0 and abs(v-y[i-1])<=margin)
            if temp==[]:temp.append(i)
            else: 
                if(len(temp)==1):temp.append(0)
                temp[1]=i
        elif len(temp)>1:
            # print (t[temp[0]:temp[1]])
            if((temp[1]-temp[0])!=0):marginChunks.append(temp.copy())
            temp = []
            currChunk = []
        else:
            currChunk = []
            temp = []
        
    
    

    return marginChunks
def smoothNoiseChunks(t,y):
    y = y.copy()
    for chunk in getNoiseChunks(t,y,5):
        smoothed = getSmooth(t[chunk[0]:chunk[1]],y[chunk[0]:chunk[1]])
        print(getSpan(t,y),len(smoothed),chunk[1]-chunk[0])
        if(chunk[1]-chunk[0]<getSpan(t,y)*2):continue
        y[chunk[0]:chunk[1]] = smoothed
    return y
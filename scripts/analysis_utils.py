import enum
import numpy as np
import statistics
import statsmodels.api as sm
import scipy

def dt(time, data):
    res = []
    if(len(time)!=len(data)):
        raise Exception("incorrect sizes")
    for i, v in enumerate(data[1:]):
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
    return span

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
    if(len(y)<2*span):
        if(len(y)):return len(y)*[y[0]]
        else:return y
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


def getNoiseChunks(t,y,margin = 5): # returns [[a,b],[c,d],[e,f]...]
    chunks = []
    temp = []
    for i,v in enumerate(y[:-1]):
        if(abs(v-y[i+1])<=margin):
            if(temp==[]):temp = [i,i+1]
            else:
                temp[1] = i+1
        else:
            print("temp",temp)
            if(len(temp)>1):chunks.append(temp)
            temp = []
        print(t[i],abs(v-y[i+1]),abs(v-y[i+1])<=margin,[t[temp[0]],t[temp[1]]] if len(temp)>1 else "")
    if(len(temp)>1):chunks.append(temp)
    return chunks
def smoothNoiseChunks(t,y):
    y = y.copy()
    for chunk in getNoiseChunks(t,y):
        smoothed = getSmooth(t[chunk[0]:chunk[1]],y[chunk[0]:chunk[1]])
        y[chunk[0]:chunk[1]] = smoothed
    return y
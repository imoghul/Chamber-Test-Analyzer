import enum
import numpy as np
import statistics
def dt(time,data):
    res = []
    for i,v in enumerate(data):
        if i == 0:
            continue
        res.append((v-data[i-1])/(float(time[i])-float(time[i-1])))
    return res

def smooth(arr,span):
    cumsum_vec = np.cumsum(arr)
    moving_average = (cumsum_vec[2 * span:] - cumsum_vec[:-2 * span]) / (2 * span)

    # The "my_average" part again. Slightly different to before, because the
    # moving average from cumsum is shorter than the input and needs to be padded
    front, back = [np.average(arr[:span])], []
    for i in range(1, span):
        front.append(np.average(arr[:i + span]))
        back.insert(0, np.average(arr[-i - span:]))
    back.insert(0, np.average(arr[-2 * span:]))
    return np.concatenate((front, moving_average, back))

def getSpan(t,y):
    span = len(getPeaks(t,y))//50
    if(span<5):span = 5
    return span

def getSmooth(t,y,iterations = None,span = None):
    if(iterations == None):
        iterations = round(5/statistics.stdev(y))#len(getPeaks(t,y))//100
        if(iterations<5):iterations = 5
        if(iterations>5000):iterations = 5000
        print("iterations: "+str(iterations))
    if(span==None):span = getSpan(t,y)
    print("span: "+str(span))
    smoov = smooth(y,span)
    for i in range(iterations-1):
        smoov = smooth(smoov,span)
    return smoov


def getPeaks(t,data):
    res = []
    diff = dt(t,data)
    for i,v in enumerate(diff):
        if(v==0 or (i!=0 and v*diff[i-1]<0)):  res.append(i)

    # clean up bouncing
    bounces = []
    for i,v in enumerate(res):
        if(i!=0 and v == res[i-1]+1):
            bounces.append(v)
    for i in bounces:
        res.remove(i)
    return res
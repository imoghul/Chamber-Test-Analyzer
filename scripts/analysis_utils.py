import numpy as np
import scipy.fftpack
def dt(time,data):
    res = []
    for i,v in enumerate(data):
        if i == 0:
            res.append(0)
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

# def getCutoff(y,iterations,bpoints):

def getSpan(y):
    return 5

def getSmooth(y,iterations = 30,span = None):
    if(span==None):span = getSpan(y)
    smoov = smooth(y,span)
    for i in range(iterations-1):
        smoov = smooth(smoov,span)
    return smoov
import numpy as np
def dt(time,data):
    res = []
    for i,v in enumerate(data):
        if i == 0:
            res.append(0)
            continue
        res.append((v-data[i-1])/(float(time[i])-float(time[i-1])))
    return res

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth
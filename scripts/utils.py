# from numpy import mean
import copy
import csv
from fileinput import filename
from tqdm import tqdm
import math


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10:: 4])


def empty():
    pass


def mean(x):
    sum = 0
    for i in x:
        sum += i
    return sum / len(x)


def average(x):
    if len(x) == 0:
        return 0
    return mean(x)


def dtToMin(y, mon, d, h, m, s):
    return 525600 * y + 43800 * mon + 1440 * d + 60 * h + m + s / 60


def closestTo(arr, val):
    v = min(arr, key=lambda x: abs(x - val))
    return (v, arr.index(v))


def readTime(dt):  # sample dt: 3:09:12.039 PM 11/24/2021
    dt = dt.split(" ")
    d = dt[2]
    d_arr = d.split("/")
    t = dt[0]
    year = int(d_arr[2])
    month = int(d_arr[0])
    day = int(d_arr[1])
    h = int(t.split(":")[0])
    m = int(t.split(":")[1])
    s = float(t.split(":")[2])
    if (dt[1] == "PM") & h != 12:
        h += 12
    if (dt[1] == "AM") & h == 12:
        h = 0
    return (year, month, day, h, m, s)


def process_bar(process, current, total, message="", bar_length=25, bar_pos=40 * " "):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * "-" + ">"
    padding = int(bar_length - len(arrow)) * " "
    ending = "\n" if current == total else "\r"

    padTable = ""
    while (len(f"{process}:" + padTable)) < len(bar_pos):
        padTable += " "
    print(
        f"{process}:{padTable}[{arrow}{padding}] {int(fraction*100)}%  :  {current}/{total} ; {message}",
        end=ending,
    )


def moveToBeginning(l, elem):
    if elem not in l:
        return
    l.insert(0, l.pop(l.index(elem)))


def anyIn(val, l):  # checks if any of the elements of l are in val
    return True in [(i in val) for i in l]


def allIn(val, l):
    return all([(i in val) for i in l])


def allInSome(targets, finds):
    return True in [allIn(i, finds) for i in targets]


def runThreads(threads, max, message):
    originalMax = max
    upperMax = 15000
    processing = []
    dead = []
    length = len(threads)
    counter = 0
    with tqdm(total=length) as pbar:
        pbar.set_description(message)
        while counter < length:
            allAlive = True
            while len(processing) < max and len(threads):
                t = threads.pop(0)
                t.start()
                processing.append(t)

            for i in processing:
                if not i.is_alive():
                    counter += 1
                    pbar.update(1)
                    dead.append(processing.pop(processing.index(i)))
                    allAlive = False

            # if allAlive:
            #     # if(max < upperMax):
            #         max += 10
            # elif max > originalMax:
            #     max -= 1

    for t in dead + processing:
        t.join()


class Time():
    def __init__(self, hour, minute, second, pos=True):
        self.hour = hour
        self.minute = minute
        self.second = second
        self.pos = pos
    def __init__(self,s):
        data = s.split(" ")
        self.pos = data[0]=="+"
        time = data[1].split(":")
        self.hour = int(time[0])
        self.minute = int(time[1])
        self.second = int(time[2])



    def __add__(self, other):
        return self.secToObj(other.toSec() + self.toSec())

    def __sub__(self, other):
        self.__add__(other.__neg__())

    def __neg__(self):
        return Time(self.hour, self.minute, self.second, not self.pos)

    def __str__(self):
        return f'{"+" if self.pos else "-"} {"0" if self.hour<10 else ""}{self.hour}:{"0" if self.minute<10 else ""}{self.minute}:{"0" if self.second<10 else ""}{self.second}'

    def __ge__(self, other):
        return self.toSec() >= other.toSec()

    def __abs__(self):
        return Time(self.hour, self.minute, self.second)

    def toSec(self):
        return (self.second + self.minute * 60 +
                self.hour * 3600) * (1 if self.pos else -1)

    def secToObj(self, secs):
        pos = secs >= 0
        secs = abs(secs)
        h = math.floor(secs / 3600)
        m = math.floor((secs - h * 3600) / 60)
        s = (secs - h * 3600 - m * 60)
        return Time(abs(h), abs(m), abs(s), pos=pos)

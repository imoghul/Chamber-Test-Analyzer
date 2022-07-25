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
# import matplotlib.pyplot as plt
# import numpy as np

outFileName = "summary.csv"
globType = "**/*.csv"

outdir = None
logger = logging.getLogger(__name__)


data = {}
headers = []
threads = []
dirNum = 0


def calc(fileName, dud):
    global data, logger
    try:
        pass
        with open(fileName, newline="") as file:
            if(fileName not in data):
                data[fileName] = {}
            header = None
            skip = True
            rowNum = 0
            for row in csv.reader(file, delimiter="\n", quotechar=","):
                for r in row:
                    v = r.split(",")
                    rowNum += 1
                    if(data[fileName] == {} and not skip):
                        header = v
                        for i in header:
                            data[fileName][i] = []
                        continue
                    if(skip):
                        skip = False
                        continue
                    if(len(v) == len(header)):
                        for index, val in enumerate(v):
                            try:
                                if(header[index] == "Test Time"):
                                    val = Time("+ "+val)
                            except:
                                pass
                            try:
                                val = float(val)
                            except:
                                pass
                            data[fileName][header[index]].append(val)
                    else:
                        logger.error(
                            Exception("headers and data values don't match on row %d" % rowNum))

    except csv.Error as e:
        pass
    except Exception as e:
        logger.error(Exception(
            fileName
            + " couldn't be read with the following error:\n\n\t"
            + str(e)
            + "\n\n"
        ))
        # raise e


def writeHeaderToFile(writer):
    pass


def writeDataToFile(writer, dir, fileNames):
    global dirNum, threads
    dirNum += 1

    bar = tqdm(fileNames)
    bar.set_description(
        "Initializing for the %s directory" % ordinal(dirNum))

    for fileName in bar:
        # threads.append(threading.Thread(target=calc, args=(fileName, 0)))
        if(calc(fileName, 0) == 0):
            if "P Temp chamber" in data[fileName] and -999 not in data[fileName]["P Temp chamber"]:
                print(data[fileName]["P Temp chamber"])
                return


def writeSummaryToFile(writer):
    global data, threads, headers

    # execute threads
    runThreads(threads, 10, "Retrieving Data")
    # print(data[list(data.keys())[0]])
    bar = tqdm(data)
    for fn in bar:
        interest = data[fn]
        # if("P Temp chamber" not in interest):
        #     continue
        # if(-999 in interest["P Temp chamber"]): continue

        t = [str(i) for i in interest["Test Time"]]
        at1 = interest["Ambients"]
        watts = interest["Watt"]
        phps = interest["PHPs"]

        # plt.plot(t,at1,"r")
        # plt.plot(t,watts,"g")
        # plt.show()
        writer.writerow(["Time:"]+t)
        writer.writerow(["Ambients"]+at1)
        writer.writerow(["Watts:"]+watts)
        writer.writerow(["PHPs:"]+phps)
        writer.writerow(["P Temp chamber "]+interest["P Temp chamber"])
        # print(data[fn])
        print(fn)
        break


def transfer(odir, log):
    global outdir, logger, outFileName
    logger = log
    outdir = odir


def getOutFileName():
    return outFileName

from asyncore import write
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
data = {}
outdir = ""
dataFile = None
logger = logging.getLogger(__name__)

headers = []
threads = []
dirNum = 0


def calc(fileName, dud):
    global data,logger
    try:
        pass
        with open(fileName, newline="") as file:
            # data = get_json()
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
                                    val = str(Time("+ "+val))
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


def writeHeaderToFile(writer):
    pass


def writeDataToFile(writer, dir, fileNames):
    global dirNum, threads
    dirNum += 1

    bar = tqdm(fileNames)
    bar.set_description(
        "Initializing for the %s directory" % ordinal(dirNum))
    c = 0
    for fileName in bar:
        # threads.append(threading.Thread(target=calc, args=(fileName, 0)))
        calc(fileName,0)
        c+=1
        if "P Temp chamber" in data[fileName] and -999 not in data[fileName]["P Temp chamber"]:
            c+=1
        if c>=10:
            return


def writeSummaryToFile(writer):
    global data, threads, headers
    json.dump(data, dataFile, indent=4)
    # execute threads
    # runThreads(threads, 10, "Retrieving Data")
    # print(data[list(data.keys())[0]])
    bar = tqdm(data)
    for fn in bar:
        interest = data[fn]
        if("P Temp chamber" not in interest):
            continue
        if(-999 in interest["P Temp chamber"]): continue

        t = [str(i) for i in interest["Test Time"]]
        at1 = interest["Ambients"]
        watts = interest["Watt"]
        phps = interest["PHPs"]

        # plt.plot(t,at1,"r")
        # plt.plot(t,watts,"g")
        # plt.show()
        writer.writerow(["FileName",fn])
        writer.writerow(["Time:"]+t)
        writer.writerow(["Ambients"]+at1)
        writer.writerow(["Watts:"]+watts)
        writer.writerow(["PHPs:"]+phps)
        if("P Temp chamber " in interest):writer.writerow(["P Temp chamber "]+interest["P Temp chamber"])
        writer.writerow([""])
        print(data[fn])
        print(fn)
        # if(i>100):break'
    dataFile.close()


def transfer(odir, log):
    global dataFile, outdir, logger, outFileName
    logger = log
    outdir = odir
    dataFile = open(outdir+"data.json","w")
    json.dump({}, dataFile, indent=4)
    dataFile.close()

    dataFile = open(outdir+"data.json","w")


def getOutFileName():
    return outFileName



# function to add to JSON
def write_json(key,new_data, filename=outdir+'data.json'):

    with open(filename,'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data[key].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)
 
    # python object to be appended

def get_json(filename = outdir+'data.json'):
    with open(filename,'r') as file:
        return json.load(file)
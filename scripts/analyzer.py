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
# data = {}
outdir = ""
logger = logging.getLogger(__name__)

headers = []
threads = []
dirNum = 0


def calc(fileName, dud):
    global logger
    try:
        pass
        with open(fileName, newline="") as file:
            data = {}
            header = None
            skip = True
            rowNum = 0
            for row in tqdm(list(csv.reader(file, delimiter="\n", quotechar=",")),leave=False,desc="Row Number"):
                for r in row:
                    v = r.split(",")
                    rowNum += 1
                    if(data == {} and not skip):
                        header = v
                        for i in header:
                            data[i] = []
                        continue
                    if(skip):
                        skip = False
                        continue
                    if(len(v) == len(header)):
                        for index, val in enumerate(v):
                            try:
                                if(header[index] == "Test Time"):
                                    val = Time("+ "+val).toSec()
                            except:
                                pass
                            try:
                                val = float(val)
                            except:
                                pass
                            data[header[index]].append(val)
                    else:
                        logger.error(
                            Exception("headers and data values don't match on row %d" % rowNum))
            # write_json(fileName,data,outdir+"data.json")
            return data
    except csv.Error as e:
        pass
    except Exception as e:
        raise e
        # logger.error(Exception(
        #     fileName
        #     + " couldn't be read with the following error:\n\n\t"
        #     + str(e)
        #     + "\n\n"
        # ))


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
        data = calc(fileName,0)
        if "P Temp chamber" in data and -999 not in data["P Temp chamber"]:
            write_json(fileName,data,outdir+"data.json")
            c+=1
            print(c)
        if c>=10:
            return


def writeSummaryToFile(writer):
    global threads, headers
    data = get_json(outdir+"data.json")
    # print(data[list(
    # data.keys())[0]])
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

        writer.writerow(["FileName",fn])
        writer.writerow(["Time:"]+t)
        writer.writerow(["Ambients"]+at1)
        writer.writerow(["Watts:"]+watts)
        writer.writerow(["PHPs:"]+phps)
        if("P Temp chamber" in interest):writer.writerow(["P Temp chamber"]+interest["P Temp chamber"])
        writer.writerow([""])


def transfer(odir, log):
    global outdir, logger, outFileName
    logger = log
    outdir = odir
    with open(outdir+"data.json","w") as dataFile:
        json.dump({}, dataFile, indent=4)


def getOutFileName():
    return outFileName



# function to add to JSON
def write_json(key,new_data, filename=outdir+'data.json'):
    try:
        with open(filename,'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details
            
            # if(key not in file_data):file_data[key] = new_data
            # else:file_data[key].append(new_data)
            file_data[key] = new_data
            
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent = 4)
 
    except PermissionError:
        write_json(key,new_data,filename)

def get_json(filename = outdir+'data.json'):
    with open(filename,'r') as file:
        return json.load(file)
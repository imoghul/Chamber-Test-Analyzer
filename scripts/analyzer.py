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

outputJson = 'data.json'


def calc(fileName, dud):
    global logger
    try:
        pass
        with open(fileName, newline="") as file:
            data = {}
            header = None
            skip = True
            rowNum = 0
            for row in tqdm(list(csv.reader(file, delimiter="\n", quotechar=",")), leave=False, desc="Row Number"):
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
            # write_json(fileName,data,outdir+outputJson)
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
        "Retrieving from the %s directory" % ordinal(dirNum))
    c = 0
    for fileName in bar:
        data = calc(fileName, 0)
        # "P Temp chamber" in data and -999 not in data["P Temp chamber"] and "P pidPTerm" in data and len(data["P pidPTerm"]) != data["P pidPTerm"].count(-999) and "P pidISum" in data and len(data["P pidISum"]) != data["P pidISum"].count(-999):
        if True:
            write_json(fileName, data, outdir+outputJson)
            c += 1
        # if c >= 100:
        #     return


def writeSummaryToFile(writer):
    global threads, headers
    data = get_json(outdir+outputJson)
    # print(data[list(
    # data.keys())[0]])
    bar = tqdm(data)
    for fn in bar:
        interest = data[fn]

        writer.writerow(["FileName", fn])
        writer.writerow(["Time:"]+[str(i) for i in interest["Test Time"]])
        writer.writerow(["Ambients"]+interest["Ambients"])
        writer.writerow(["Watts:"]+interest["Watt"])
        writer.writerow(["PHPs:"]+interest["PHPs"])
        if("P Temp chamber" in interest):
            writer.writerow(["P Temp chamber"]+interest["P Temp chamber"])
        if("P pidPTerm" in interest):
            writer.writerow(["P pidPTerm"]+interest["P pidPTerm"])
        if("P pidISum" in interest):
            writer.writerow(["P pidISum"]+interest["P pidISum"])
        writer.writerow([""])


def transfer(odir, log):
    global outdir, logger, outFileName
    logger = log
    outdir = odir
    with open(outdir+outputJson, "w") as dataFile:
        json.dump({}, dataFile, indent=4)


def getOutFileName():
    return outFileName


# function to add to JSON
def write_json(key, new_data, filename=outdir+outputJson):
    try:
        with open(filename, 'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details

            # if(key not in file_data):file_data[key] = new_data
            # else:file_data[key].append(new_data)
            file_data[key] = new_data

            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent=4)

    except PermissionError:
        write_json(key, new_data, filename)


def get_json(filename=outdir+outputJson):
    with open(filename, 'r') as file:
        return json.load(file)

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
                    if(data[fileName] == {}):
                        header = v
                        for i in header:
                            data[fileName][i] = []
                        continue
                    if(header != None and skip):
                        skip = False
                        continue
                    if(len(v) == len(header)):
                        for index, val in enumerate(v):
                            if(header[index] == "TESTTIME"):
                                val = str(Time("+ "+val))
                            elif(val.isnumeric()):
                                val = float(val)
                            data[fileName][header[index]].append(val)
                    else:
                        logger.error(
                            Exception("headers and data values don't match on row %d" % rowNum))

    except csv.Error as e:
        pass
    except Exception as e:
        # logger.error(Exception(
        #     fileName
        #     + " couldn't be read with the following error:\n\n\t"
        #     + str(e)
        #     + "\n\n"
        # ))
        raise e


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
        calc(fileName, 0)


def writeSummaryToFile(writer):
    global data, threads, headers

    # execute threads
    runThreads(threads, 2000, "Retrieving Data")
    print(data[list(data.keys())[0]])


def transfer(odir, log):
    global certdir, preferencesFile, detectionList, retrieveData, genCert, outdir, logger, outFileName
    logger = log
    outdir = odir


def getOutFileName():
    return outFileName

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
from slugify import slugify
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

outputJson = 'fileNames.json'

detectedFiles = []

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
                                print(val)
                            try:
                                val = float(val)
                            except:
                                pass
                            data[header[index]].append(val)
                    else:
                        logger.error(
                            Exception("headers and data values don't match on row %d" % rowNum))
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
    get_json(outdir+outputJson)


def writeDataToFile(writer, dir, fileNames):
    global dirNum, threads, detectedFiles
    dirNum += 1

    bar = tqdm(fileNames)
    bar.set_description(
        "Retrieving from the %s directory" % ordinal(dirNum))
    c = 0


    
    for fileName in bar:
        
        # def run(fileName,outdir,c):
            if cleanFileName(fileName) in detectedFiles:continue#return 

            data = calc(fileName, 0)
            if "Watt" in data:#True:
                try:write_json(fileName, data, outdir)
                except:pass
                c += 1
        # threads.append(threading.Thread(target=run,args=(fileName,outdir,c)))
    


def writeSummaryToFile(writer):
    global threads, headers
    # runThreads(threads,1,"Running Threads")


def transfer(odir, log):
    global outdir, logger, outFileName
    logger = log
    outdir = odir
    get_json(outdir+outputJson)


def getOutFileName():
    return outFileName


# function to add to JSON
def write_json(fn,new_data,outdir=outdir):
    global detectedFiles
    key = cleanFileName(fn)
    # print(outdir+"data/"+key+".json")
    try:
        with open(outdir+"data/"+key+".json", 'w') as file:
            json.dump(new_data,file,indent=4)
    except FileNotFoundError:
        
        f = open(outdir+"data/"+key+".json", "x")
        f.close()
        with open(outdir+"data/"+key+".json", 'w') as file:
            json.dump(new_data,file,indent=4)
        # write_json(fn, new_data, outdir)
    except FileExistsError:
        detectedFiles.append(key)

    try:
        with open(outdir+outputJson, 'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details
            detectedFiles = list(file_data.keys())
            # if(key not in file_data):file_data[key] = new_data
            # else:file_data[key].append(new_data)
            file_data['File Names'].append(key)

            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent=4)
    except PermissionError:
        write_json(fn, new_data, outdir)


def get_json(filename=outdir+outputJson):
    global detectedFiles
    with open(filename, 'r') as file:
        d = json.load(file)
        detectedFiles = d['File Names']
        return d


def cleanFileName(fn):
    key = ""+fn.replace(".json","")
    return slugify(key)+".json"
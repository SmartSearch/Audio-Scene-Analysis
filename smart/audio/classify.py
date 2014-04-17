#!/usr/bin/env python3
# encoding: utf-8

# SMART FP7 - Search engine for MultimediA enviRonment generated contenT
# Webpage: http://smartfp7.eu
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. 
# 
# The Original Code is Copyright (C) 2013 IBM Corp.
# All Rights Reserved
# 
# Contributor(s):
#  Zvi Kons <zvi@il.ibm.com>

'''
smart.audio.classify - audio classification CLI.
'''

import sys

from smart.audio import AudioClassifier, Configuration
import argparse, math
import datetime
import os.path
import json
import urllib.request
import logging


def logsig(x):
    '''
    Log sigmoid function
    :param x: input
    :returns: output
    '''
    return 1/(1+math.exp(-x))

def pred2json(componentName, pred, d0):
    '''
    Converts classification scores into JSON format
    :param componentName: name of EdgeNode component
    :param pred: prediction values
    :param d0: sample start time and date
    :returns: scores in JSON format (string) 
    '''
    # calculate offset for middle of the frame from the sample start time
    pos=(pred["t1"]+pred["t2"])/2.0
    dt=datetime.timedelta(seconds=pos)
    d1=d0+dt
    d1s=d1.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    # build JSON data in EdgeNode format
    audio={"@ID":componentName, "position" : pos}
    for lbl in pred:
        if (lbl != "t1" ) and (lbl != "t2"):
            # score if mapped to the (0,1) range
            audio.update({lbl+"_score" :  logsig(pred[lbl])})
    data={"time": d1s, "audio": audio}
    jsondict={"timestamp":int(pos*1000), "data": data}
    return json.dumps(jsondict, indent=2)

def postJson(url, jsonData):
    '''
    Post JSON data to EdgeNode server
    :param url: server URL
    :param jsonData: JSON string
    '''
    data = jsonData.encode('utf-8')
    request = urllib.request.Request(url)
    request.add_header("Content-Type","application/json")
    try:
        with urllib.request.urlopen(request, data) as rin:
            res=json.loads(rin.read().decode("utf-8"))
            if rin.getcode() != 201:
                logging.error("ERROR: Server rejected JSON data\n[{}]\n".format(res))
                return None
        return res
    except Exception as e:
        logging.error("ERROR: Failed to post JSON data\n{}\n".format(e))
        return None

def main(argv): 
    '''Command line classification.'''

    parser = argparse.ArgumentParser(description="Classification for an audio file")
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="increase verbosity level", default=0)
    parser.add_argument("-m", "--model_dir", dest="modelDir", default="./models", help="input directory for models data [%(default)s]")
    parser.add_argument("-c", "--csv_ouput", dest="csvOutput", action="store_true", help="CSV table output [default]")
    parser.add_argument("-j", "--json_ouput", dest="jsonOutput", action="store_true", help="JSON format output")
    parser.add_argument("-e", "--edge_node", dest="edgeNodeUrl", help="URL for edge node server. JSON output will be posted to this URL")
    parser.add_argument("-n", "--component_name", dest="componentName", help="Name of the component within the edge server (required if -j or -e are used)")
    
    parser.add_argument("audio_file", help="audio file for classification")
    args = parser.parse_args()
    if args.verbose==1:
        logging.basicConfig(level=logging.INFO)
    if args.verbose>1:
        logging.basicConfig(level=logging.DEBUG)
    cfg=Configuration
    if (not args.csvOutput) and (not args.jsonOutput) and (not args.edgeNodeUrl):
        args.csvOutput=True 
    if (args.jsonOutput or args.edgeNodeUrl) and not args.componentName:
        logging.critical("Missing component name parameter\n")
        return 1
    # classification class
    cls=AudioClassifier.AudioClassifier(cfg)
    # load GMMs
    cls.loadModels(args.modelDir)

    # print CSV header
    if args.csvOutput:
        print("t1,t2", end="")
        for lbl in cls.labels:
            print(",{}".format(lbl), end="")
        print()
    
    # Sample start time from the file creation time
    if args.jsonOutput or args.edgeNodeUrl:
        sampleTime=os.path.getmtime(args.audio_file)
        sampleDateTime=datetime.datetime.fromtimestamp(sampleTime)

    # iterate over segments
    for p in cls.predFile(args.audio_file):
        if args.csvOutput:
            print("{0[t1]},{0[t2]}".format(p), end="")
            for lbl in cls.labels:
                print(",{}".format(logsig(p[lbl])), end="")
            print()
        if args.jsonOutput or args.edgeNodeUrl:
            jsonData=pred2json(args.componentName, p, sampleDateTime)
            if args.jsonOutput:
                print(jsonData)
            if args.edgeNodeUrl:
                if not postJson(args.edgeNodeUrl, jsonData):
                    return 1
    return 0
        
if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
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
smart.audio.train -- Training module for audio classification
'''

import sys

from smart.audio import AudioClassifier, Configuration
import argparse
import logging


def main(argv): 
    '''Command line training.'''

    parser = argparse.ArgumentParser(description="Train audio classifier from training set")
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="increase verbosity level", default=0)
    parser.add_argument("-m", "--model_dir", dest="modelDir", default="./models", help="output directory for models data [%(default)s]")
    parser.add_argument("list_file", help="file containing list of training samples and labels")
    args = parser.parse_args()
    if args.verbose==1:
        logging.basicConfig(level=logging.INFO)
    if args.verbose>1:
        logging.basicConfig(level=logging.DEBUG)
    cfg=Configuration

    # create classifier
    trn=AudioClassifier.AudioClassifier(cfg)
    # load the file list
    fd=trn.loadFilesData(args.list_file)
    # train GMMs
    trn.createAllGmms(args.modelDir, fd)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
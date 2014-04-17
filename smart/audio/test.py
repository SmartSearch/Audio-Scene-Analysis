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
 


"""
smart.audio.test -Test and calculate EER for audio data set CLI.
"""
import sys

from smart.audio import AudioClassifier, Configuration, utils
import argparse
import logging


def main(argv): 
    '''Command line training.'''

    parser = argparse.ArgumentParser(description="Test audio classifier using a testing set")
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="increase verbosity level", default=0)
    parser.add_argument("-m", "--model_dir", dest="modelDir", default="./models", help="input directory for models data [%(default)s]")
    parser.add_argument("list_file", help="file containing list of testing samples and labels")
    args = parser.parse_args()
    if args.verbose==1:
        logging.basicConfig(level=logging.INFO)
    if args.verbose>1:
        logging.basicConfig(level=logging.DEBUG)
    cfg=Configuration
    cls=AudioClassifier.AudioClassifier(cfg)
    cls.loadModels(args.modelDir)
    fd=cls.loadFilesData(args.list_file)

    # create long source and target vectors from all audio files and labels
    scr={}
    trg={}
    for label in cls.labels:
        scr[label]=[]
        trg[label]=[]
    for f in fd:
        (scr1,trg1)=cls.testFile(f)
        for label in cls.labels:
            scr[label].extend(scr1[label])
            trg[label].extend(trg1[label])
    # print EER for each label
    for label in cls.labels:
        print("{}: {:.2f}%".format(label, 100*utils.eer(scr[label], trg[label])))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
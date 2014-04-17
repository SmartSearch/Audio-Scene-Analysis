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
smart.audio.Configuration - Audio classifier configuration file.
'''

# Location of SPTK and Sox executables
# Should be configured to local setting
sptk="/usr/local/sptk/bin"
sox="/usr/bin/sox"

# Working sample rate in Hz
samplerate=22050
# Window length in samples
winLen=1024
# Distance between each frame in samples
frmLen=512
# Length of MFCC vector
nMfcc=16
# Length of the feature vector = (MFCC + dMFCC + ddMFCC)
ftrLen = nMfcc *3
# Number of Gaussians in each GMM
nGauss = 16

# Length of segment used for classification (in seconds)
segLen=5

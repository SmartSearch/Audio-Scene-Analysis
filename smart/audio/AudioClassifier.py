#!/usr/bin/env python3

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

 
import tempfile, os.path
import struct
import logging

"""
smart.audio.AudioClassifier - audio classification class.
"""

class TrainException(Exception):
    '''Exception in training process'''
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg=msg
        
    def __repr__(self):
        return "<TrainException:: {0}>".format(self.msg)

    def __str__(self):
        return "TrainException= {0}".format(self.msg)

class AudioClassifier:
    '''GMM model for audio classification'''

    def __init__(self, cfg):
        self.cfg=cfg
        self.tempDirObj=tempfile.TemporaryDirectory()
        self.tempDir=self.tempDirObj.name
        self.sptkDir=self.cfg.sptk

    def do(self,cmd):
        '''Execute a command'''
        logging.debug("DO: "+ cmd)
        rc=os.system(cmd)
        if rc!=0:
            raise TrainException("rc={0}".format(rc))

    def file2mfcc(self, inFileName, mfccName, timeRange=None):
        '''Convert audio file to MFCC with delta and delta^2.
        Then append the output to the mfccName'''
        #convert file to short format
        logging.debug("file2mfcc: {} >> {}".format(inFileName, mfccName))
        if timeRange:
            trim="trim ={} ={}".format(timeRange[0], timeRange[1])
        else:
            trim=""
        data=os.path.join(self.tempDir, "data")
        cmd="{0.sox} {1} -t raw -e signed-integer -b 16 -c 1 -r {0.samplerate} {2}.s {3}".format(self.cfg, inFileName, data, trim)
        self.do(cmd)
        #convert from short to float
        x2x=os.path.join(self.sptkDir, "x2x")
        cmd="{0} +sf {1}.s > {1}.f".format(x2x, data)
        self.do(cmd)
        # cut into frames
        frame=os.path.join(self.sptkDir, "frame")
        cmd="{0} -l {1.winLen} -p {1.frmLen} {2}.f > {2}.frm".format(frame, self.cfg, data)
        self.do(cmd)
        # convert frames to MFCC
        mfcc=os.path.join(self.sptkDir, "mfcc")
        cmd="{0} -l {1.winLen} -m {1.nMfcc} {2}.frm > {2}.mfcc".format(mfcc, self.cfg, data)
        self.do(cmd)
        # Calculate dynamic features and append to output file
        delta=os.path.join(self.sptkDir, "delta")
        cmd="{0} -l {1.nMfcc}  -d -0.5 0 0.5 -d 1 -2 1 {2}.mfcc >> {3}".format(delta, self.cfg, data, mfccName)
        self.do(cmd)

    def createUbm(self, ubmFile, filesData):
        '''
        Calculate UBM model from all the data available
        :param ubmFile: output file containing UBM model
        '''
        # Calculate MFCC for all files
        mfccFile=os.path.join(self.tempDir, "ubm.dmfcc")
        logging.info("createUbm: creating "+ mfccFile)
        if os.path.exists(mfccFile):
            os.remove(mfccFile)
        for f in filesData:
            self.file2mfcc(f[0], mfccFile)
        # Create GMM model from all data
        logging.info("createUbm: building GMM model")
        gmm=os.path.join(self.sptkDir, "gmm")
        cmd="{0} -l {1.ftrLen} -m {1.nGauss} {2} > {3}".format(gmm, self.cfg, mfccFile, ubmFile)
        self.do(cmd)

    def createGmm(self, gmmFile, label, filesData):
        '''
        Calculate GMM model from all the data of a given label
        :param gmmFile: output file containing GMM model
        :param label: label name for GMM model
        '''
        # Calculate MFCC for all files
        mfccFile=os.path.join(self.tempDir, label+".dmfcc")
        logging.info("createGmm: creating "+ mfccFile)
        if os.path.exists(mfccFile):
            os.remove(mfccFile)
        for f in filesData:
            fileName=f[0];
            for lblInfo in f[1:]:
                if label==lblInfo[0]:
                    self.file2mfcc(fileName, mfccFile, lblInfo[1:])
        # Create GMM model from all data
        logging.info("createGmm: building GMM model for "+label)
        gmm=os.path.join(self.sptkDir, "gmm")
        cmd="{0} -l {1.ftrLen} -m {1.nGauss} {2} > {3}".format(gmm, self.cfg, mfccFile, gmmFile)
        self.do(cmd)

    def createAllGmms(self, modelDir, filesData):
        '''
        Create the GMM models for the UBM and all other audio classes
        :param modelDir: output directory
        :param filesData: list of audio files and labels
        '''
        self.modelDir=modelDir
        # get a list of all available labels
        labels=set()
        for fd in filesData:
            for lblData in fd[1:]:
                labels.add(lblData[0])
        self.labels=list(labels)
        if not os.path.exists(self.modelDir):
            os.mkdir(self.modelDir)
        # build UBM
        gmmFile=os.path.join(self.modelDir, "ubm.gmm")
        self.createUbm(gmmFile, filesData)
        # build GMM for each label
        for lbl in self.labels:
            gmmFile=os.path.join(self.modelDir, lbl+".gmm")
            self.createGmm(gmmFile, lbl, filesData)
        # save list of labels
        with open(os.path.join(self.modelDir, "labels.txt"), "wt") as flbl:
            for lbl in self.labels:
                flbl.write(lbl+"\n")
    
    def predict(self, audioFile, t1, t2):
        '''
        Calculate the GMM score for each audio class
        :param audioFile: input file
        :param t1: start of time range (sec)        
        :param t2: end of time ragnge (sec)
        :returns: dictionary with score for each label
        '''
        # extract features for this time range
        mfccFile=os.path.join(self.tempDir, "data.dmfcc")
        logging.info("createGmm: creating "+ mfccFile)
        if os.path.exists(mfccFile):
            os.remove(mfccFile)
        self.file2mfcc(audioFile, mfccFile, [t1, t2])
        labels=list(self.labels)
        labels.append("ubm")
        # calc log probability for each class including UBM
        pred0={}
        for label in labels:
            gmmFile=os.path.join(self.modelDir, label+".gmm")
            gmmp=os.path.join(self.sptkDir, "gmmp")
            predFile=os.path.join(self.tempDir, "pred.f")
            cmd="{0} -a -l {1.ftrLen} -m {1.nGauss} {2} {3} > {4}".format(gmmp, self.cfg, gmmFile, mfccFile, predFile)
            self.do(cmd)
            with open(predFile, 'rb') as fp:
                res=struct.unpack('f', fp.read(4))
            pred0[label]=res[0]
        # return the score relative to the UBM
        pred={}
        for label in self.labels:
            pred[label]=pred0[label]-pred0["ubm"]
        return pred
    
    def predFile(self, audioFile):
        '''
        Iterator returning the prediction for all segments in the file
        :param audioFile: input file
        :returns: dict with scores for each label including the time range
        '''
        # find audio duration (in seconds)
        durFile=os.path.join(self.tempDir, "dur.txt")
        cmd="{}i -D {} > {}".format(self.cfg.sox, audioFile, durFile)
        self.do(cmd)
        with open(durFile,"rt") as fin:
            dur=float(fin.readline())
        # iterate over all segments
        t1=0
        while t1<dur:
            t2=t1+self.cfg.segLen
            p=self.predict(audioFile, t1, min(t2,dur))
            p["t1"]=t1
            p["t2"]=t2
            t1=t2   
            yield p

    def testFile(self, audioFileData):
        '''
        Calculate the scores and the expected values for each segment in the file.
        Expected values are calculated from the label information
        :param audioFileData: list containing audio file and labels
        :returns: tuple with dict with list for each label
        '''
        # initialize empty dicts
        scr={}
        trg={}
        for label in self.labels:
            scr[label]=[]
            trg[label]=[]
        # iterate over all segments
        for p in self.predFile(audioFileData[0]):
            # convert score into lists
            trg1={}
            for label in self.labels:
                scr[label].append(p[label])
                trg1[label]=0
            # find all the label in this time range
            t1=p["t1"]
            t2=p["t2"]
            for lblInfo in audioFileData[1:]:
                l1=lblInfo[1]
                l2=lblInfo[2]
                if (l1<=t2) and (l2>=t1):
                    # find length of label included in this range
                    d=(min(t2,l2)-max(t1,l1))/(t2-t1)
                    trg1[lblInfo[0]]=min(trg1[lblInfo[0]]+d,1.0)
            for label in self.labels:
                trg[label].append(trg1[label])
        return (scr, trg)
        
    def loadFilesData(self, listFile):
        '''
        Read the files list from a file. The file format should be:
        <audio file> <labels file>
        ...
        The label file format should be
        <t1> <t2> <label>
        ...
        :param listFile: file containing list of audio and labal files
        '''
        filesData=[]

        logging.info("loadFilesList: loading "+ listFile)

        with open(listFile, "rt") as fin:
            for ln in fin:
                # line format: <audio file> <label file>
                files=ln.split()
                if len(files)!=2:
                    continue
                fileData=[files[0]]
                # read labels files
                with open(files[1], "rt") as flabels:
                    for lnLabels in flabels:
                        # line format: t1 t2 label
                        tk=lnLabels.split()
                        if len(tk)!=3:
                            continue    
                        fileData.append((tk[2], float(tk[0]), float(tk[1])))
                filesData.append(fileData)
        return filesData
    
    def loadModels(self, modelDir):
        '''
        Load labels names from the models directory
        :param modelDir: input folder
        '''
        self.modelDir=modelDir
        self.labels=[]
        with open(os.path.join(self.modelDir, "labels.txt"), "rt") as flbl:
            for ln in flbl:
                self.labels.extend(ln.split())
        
            

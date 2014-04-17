'''
smart.audio.utils - Utilities functions.
'''

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



def eer(scr, trg):
    '''
    Calculate equal error rate (EER)
    :param scr: scores vector
    :param trg: target vector
    :returns: EER
    '''
    (fa,md)=roc(scr, trg)
    mind=10
    # find best point where fa~=md
    for fm in zip(fa,md):
        d=abs(fm[0]-fm[1])
        if d<mind:
            e=sum(fm)/2
            mind=d
    return e

def  roc(scr, trg):   
    '''
    Calculate ROC: false alarm vs. miss detection curve
    :param scr: scores vector
    :param trg: target vector
    :returns: two vectors for false alarms and miss detection curve
    '''
    # convert target to Booleans
    t1=[x>0.5 for x in trg]
    # number of true
    nt=sum(t1)
    # number of false
    nf=len(t1)-nt
    if nt==0 or nf==0:
        return ([0, 1], [1, 0])
    #possible thresholds
    ths=[min(scr)-1] # add point lower than min
    ths.extend(set(scr)) # all unit scores
    ths.append(max(scr)+1) # add point larger than max
    ths.sort()
    
    # check FA / MD for all possible thresholds
    fa=[]
    md=[]
    for th in ths:
        fa1=0.0
        md1=0.0
        for st in zip(scr, t1):
            # count how many positives have scores below threshold (MD)
            if st[0]<th and st[1]:
                md1+=1.0
            # count how many negatives have scores above threshold (FA)
            if st[0]>=th and not st[1]:
                fa1+=1.0
        fa.append(fa1/nf)
        md.append(md1/nt)
    return (fa, md)

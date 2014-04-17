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
smart.audio.description - Create XML for feed configuration.
"""

import argparse
import logging
from smart.audio import Configuration, AudioClassifier
import re
import xml.sax.saxutils
import sys

# XML template. Macros are replace with %MACRO%
xmlSource="""<?xml version="1.0" encoding="UTF-8"?>
<Feed xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="SMART_Datafeed_Schema_v0.3.xsd">
    <Id>dusk.ait.gr:%FEEDNAME%</Id>
    <Type>Virtual</Type>
    <Title>Audio feed</Title>
    <Description>Audio analysis using SMART.audio.classify.py</Description>
    <DescriptionTags>
        <TextTags>audio</TextTags>
        <URITags>smartfp7:audio</URITags>
    </DescriptionTags>
    <ContactInfo>
        <ContactEmail>%EMAIL%</ContactEmail>
    </ContactInfo>
    <Components>
        <Virtual>
            <Name>%COMP%</Name>
            <Description>%DESC%</Description>
            <DescriptionTags>
                <TextTags>%TAGS%</TextTags>
            </DescriptionTags>
            <Type>audio</Type>
        </Virtual>
    </Components>
    <Outputs>
        <Output>
            <Name>position</Name>
            <ProducedBy>%COMP%</ProducedBy>
            <Description>Time within the sample</Description>
            <Type>double</Type>
            <Unit>seconds</Unit>
            <HasConfidence>false</HasConfidence>
        </Output>
    %OUTPUTS%
    </Outputs>
</Feed>
"""

# Template for audio class results
clsSource="""
        <Output>
            <Name>%CLASS%_score</Name>
            <ProducedBy>%COMP%</ProducedBy>
            <Description>Score for %CLASS% audio</Description>
            <Type>double</Type>
            <HasConfidence>false</HasConfidence>
        </Output>
"""

macros={}
macroPattern=re.compile(r'%([A-Z]+)%')

def macroVal(m):
    '''
    Replace macro key with its value
    :param m: regexp match result
    :returns: Macro value
    '''
    logging.debug("{} -> {}".format(m.group(1),macros[m.group(1)]))
    return macros[m.group(1)]

def macroSub(s):
    '''
    Substitue all macros in a string with their values.
    :param s: input string
    :returns: new string
    '''
    return macroPattern.sub(macroVal, s)

def main(argv): 
    '''Create feed description XML file.'''

    parser = argparse.ArgumentParser(description="Create feed description XML file.")
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="increase verbosity level", default=0)
    parser.add_argument("-m", "--model_dir", dest="modelDir", default="./models", help="input directory for models data [%(default)s]")
    parser.add_argument("-f", "--feed_name", dest="feedName", help="Name of the edge server feed", required=True)
    parser.add_argument("-c", "--component_name", dest="componentName", help="Name of the edge server component", required=True)
    parser.add_argument("-e", "--email", help="Creator email", required=True)
    parser.add_argument("-d", "--description", help="Description of the feed [default: \"\"]", default="")
    parser.add_argument("-t", "--tags", help="Description tags of the feed [default: \"\"]", default="")
    
    parser.add_argument("output_file", help="output XML file name")
    args = parser.parse_args()
    if args.verbose==1:
        logging.basicConfig(level=logging.INFO)
    if args.verbose>1:
        logging.basicConfig(level=logging.DEBUG)

    if len(args.tags)<1:
        args.tags="SMART.audio.classify.py"
    else:
        args.tags+=",SMART.audio.classify.py"
    # setup macro values
    macros.update({"COMP": args.componentName, "EMAIL": args.email, "DESC":xml.sax.saxutils.escape(args.description), "TAGS":args.tags, "FEEDNAME": args.feedName})
    cfg=Configuration

    # a classifier is needed in order to get the labels list
    cls=AudioClassifier.AudioClassifier(cfg)
    cls.loadModels(args.modelDir)
    
    # build section for each audio class
    outputs=""
    for lbl in cls.labels:
        macros["CLASS"]=lbl
        outputs=outputs+ macroSub(clsSource)
    macros["OUTPUTS"]=outputs
    # substitue the rest of the macros
    xmlText=macroSub(xmlSource)
    # write results
    with open(args.output_file, "wt") as fout:
        fout.write(xmlText)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

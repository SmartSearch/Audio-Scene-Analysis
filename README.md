SMART Audio classifier
=======================

## Introduction

This package contains sample tools for audio classification. The following functionality is provided:
- Training an audio classification model from a set of audio samples.
- Testing the classification rates of the model using a set of audio samples.
- Classifying an audio file and sending the results to an SMART EdgeNode server.
- Creating a feed description file that can be used to register the feed on a SMART EdgeNode server.

## Requirements

The following packages are required to be installed for this classification tool:
- Python3: http://python.org/ (tested with version 3.2.3)
- Speech Signal Processing Toolkit (SPTK): http://sp-tk.sourceforge.net/ (tested with version 3.6)
- SoX - Sound eXchange: http://sox.sourceforge.net/ (tested with version 14.4.0)

## Configuration

All the tools use the common configuration file: smart/audio/Configuration.py. Before running any tools it is best to review this configuration file. The user should verify the "sptk" variable points to the location of the SPTK binaries folder and that the "sox" variable points to the sox binary.

## Audio data

The classification tools support any audio format which is supported by the sox utility. During operation the audio files will be converted by "sox" to 16 bit, single channel, raw PCM file with sample rate specified by the configuration file.

For training and testing the tools require a set of annotated audio files. For each audio file the user should create a labels files. The label files are plain text files which the following format:

```
<t1> <t2> <audio class>
...
```

where t1 and t2 are the start and end time of the range in seconds and 'audio class' is one word label of this range. The same classes will be used for classification. The time ranges can overlap so any given point of time can belong to zero, one or more classes.

An example for a label file could be:

```
0.0          70.77634604   traffic
92.93723717  146.67739816  traffic
104.15618831 119.39180096  people
130.88776323 145.1538369   people
141.69119766 203.74169282  music
175.07103992 202.21813156  traffic
206.51180421 237.26004065  traffic
```

Label files can be created with the help of tools such as Audacity (http://audacity.sourceforge.net/) and Praat(http://www.fon.hum.uva.nl/praat/).

An audio set is described by a text file containing the paths to pairs of audio and labels file. An example for audio set file could be:

```
audio1.wav audio1.lbl
audio2.wav audio2.lbl
...
```

## Training audio classification models

The train.py is used for training the classification models. For example:

```Shell
$ export PYTHONPATH="$PYTHONPATH:SmartCode"
$ python3 smart/audio/train.py -m Data/models Data/training_files.txt
```

This will train the classification modules using the files listed in the training_files.txt and write the results to the Data/models folder.

Use the '-h' switch for description of all available options. This also works for all the other commands listed below.

## Testing classification rates

The testing.py script is used for testing the classification models. This allows to compare the labels produced by the models to labels produced manually. It is best to test the models with files that were not included in the training set. For example:

```Shell
$ python3 smart/audio/test.py -m Data/models Data/testing_files.txt
```

This will test the classification modules in the Data/models folder using the files listed in the testing_files.txt. The output is the equal error rate (EER) for each class.

## Generating a feed description file

Feed description files are used to register a feed in an EdgeNode (see http://opensoftware.smartfp7.eu/projects/smart/wiki/EdgeNodePostCommands#CreateFeed). A utility is included for generating this file from the audio classes information. This should be used after the models data is ready.

For example:

```Shell
$ python3 smart/audio/description.py -m Data/models -f audio_feed_example -c microphone1 -e my_email@address.org -d "Audio classification from outdoor microphone" -t "audio,street,traffic,people" feed.xml
```

This will create the feed.xml file. It is recommended to edit this file and verify its content before posting it to the server.
 
## Posting data to the edge server

The classify utility can process an audio file and post the results to the EdgeNode (see: http://opensoftware.smartfp7.eu/projects/smart/wiki/EdgeNodePostCommands#Append).

For example:

```Shell
$ python3 smart/audio/classify.py -m Data/models -e http://dusk.ait.gr/couchdb/audio_feed_example -n microphone1 audio.wav
```

# Pre-trained models

The _models_ directory contains pre-trained models files. The models were trained using more than 10 hours of audio data collected in the SMART project. The models supports the following audio classes:

- Applause
- Crowd
- Music
- Siren
- Speaker
- Traffic

# License

SMART FP7 - Search engine for MultimediA enviRonment generated contenT
Webpage: http://smartfp7.eu

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/. 

The Original Code is Copyright (C) 2013 IBM Corp.
All Rights Reserved

Contributor(s):
 Zvi Kons <zvi@il.ibm.com>


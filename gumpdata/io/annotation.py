"""Access movie annotations
"""

import os
import csv
from os.path import join as opj
import numpy as np

def get_scene_boundaries(basedir):
    """Returns the boundaries between scenes in movie time

    Parameters
    ----------
    basedir : path
      Base path of the dataset.

    Returns
    -------
    list(float)
      Timestamps are given in seconds.
    """
    fname = opj(basedir, 'stimulus', 'annotations', 'scenes.csv')
    cr = csv.reader(open(fname))
    ts = [float(line[0]) for line in cr]
    return ts

def get_german_audiodescription_transcript(basedir):
    """Returns the transcript with star and end timestamps

    Parameters
    ----------
    basedir : path
      Base path of the dataset.

    Returns
    -------
    array(float, float), list(str)
      The first return value is a 2-column array with start and end timestamp
      of each narration sequence. The second return value is a list with the
      corresponding transcripts in UTF8 encoding.

    """
    fname = opj(basedir, 'stimulus', 'annotations',
                'german_audio_description.csv')
    cr = csv.reader(open(fname))
    transcripts = []
    ts = []
    for line in cr:
        ts.append([float(i) for i in line[:2]])
        transcripts.append(line[2])
    return np.array(ts), transcripts


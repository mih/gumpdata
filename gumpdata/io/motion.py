"""Access motion correction estimates
"""

import os
from os.path import join as opj
import numpy as np

def get_run_motion_estimates(basedir, subj, task, run):
    """Returns the motion correction estimates for a particular run

    Parameters
    ==========
    basedir : path
      Base path of the dataset.
    subj : str
      Subject identifier (without 'sub' prefix).
    task : int
      Task ID (see task_key.txt)
    run : int
      Run ID.

    Returns
    =======
    array
      Array of floats -- one row per fMRI volume, 6 columns (first three:
      translation X, Y, Z in mm, last three: rotation in deg)
    """
    fname = opj(basedir, 'sub%s' % subj, 'BOLD', 'task%.3i_run%.3i' % (task, run),
                'bold_dico_moco.txt')
    data = np.loadtxt(fname)
    return data

def get_motion_estimates(basedir, subj, task, runs=(1,2,3,4,5,6,7,8),
                       truncate=4):
    """Returns the merged motion correction estimates for multiple runs.

    The temporal overlap between movie segments/runs is removed by truncating
    the end and front of adjacent runs by a configurable number of samples.

    Parameters
    ==========
    basedir : path
      Base path of the dataset.
    subj : str
      Subject identifier (without 'sub' prefix).
    task : int
      Task ID (see task_key.txt)
    runs : sequence
      Sequence ID for runs to consider. By default all 8 runs are used.
    truncate : int
      Number of samples/volumes to truncate at the edges of adjacent runs.

    Returns
    =======
    array
      Array of floats -- one row per fMRI volume, 6 columns (first three:
      translation X, Y, Z in mm, last three: rotation in deg)
    """
    data = []
    for i, r in enumerate(runs):
        rdata = get_run_motion_estimates(basedir, subj, task, r)
        if truncate and i > 0:
            # remove desired number samples at the front (except for first run)
            rdata = rdata[truncate:]
        if truncate and i < len(runs) - 1:
            # remove desired number samples at the end (except for last run)
            rdata = rdata[:-truncate]
        data.append(rdata)
    return np.vstack(data)

"""Access physiological recordings
"""

import os
from os.path import join as _opj
import numpy as np

__all__ = ['get_run_physio_data', 'get_run_physio_data']

def get_run_physio_data(basedir, subj, task, run, sensors=None):
    """Returns the physiological recording for a particular run

    Parameters
    ----------
    basedir : path
      Base path of the dataset.
    subj : str
      Subject identifier (without 'sub' prefix).
    task : int
      Task ID (see task_key.txt)
    run : int
      Run ID.
    sensors : None or tuple({'trigger', 'respiratory', 'cardiac', 'oxygen'})
      Selection and order of values to return.

    Returns
    -------
    array
      Array of floats -- one row per sample (100Hz), if ``sensors`` is None,
      4 columns are returned (trigger track, respiratory trace, cardiac trace,
      oxygen saturation). If ``sensors`` is specified the order of columns
      matches the order of the ``sensors`` sequence.
    """
    fname = _opj(basedir, 'sub%s' % subj, 'physio', 'task%.3i_run%.3i' % (task, run),
                'physio.txt.gz')
    sensor_map = {
        'trigger': 0,
        'respiratory': 1,
        'cardiac': 2,
        'oxygen': 3
    }
    if not sensors is None:
        sensors = [sensor_map[s] for s in sensors]
    data = np.loadtxt(fname, usecols=sensors)
    return data

def get_physio_data(basedir, subj, task, runs=(1,2,3,4,5,6,7,8),
                    truncate=4, sensors=None):
    """Returns the physiological recording for a particular run

    The temporal overlap between movie segments/runs is removed by truncating
    the end and front of adjacent runs by a configurable number of trigger
    intervals.

    Parameters
    ----------
    basedir : path
      Base path of the dataset.
    subj : str
      Subject identifier (without 'sub' prefix).
    task : int
      Task ID (see task_key.txt)
    runs : sequence
      Sequence ID for runs to consider. By default all 8 runs are used.
    truncate : int
      Number of trigger intervals to truncate at the edges of adjacent runs.
      Only 3, 4 and 5 are meaningful.
    sensors : None or tuple({'trigger', 'respiratory', 'cardiac', 'oxygen'})
      Selection and order of values to return.

    Returns
    -------
    array
      Array of floats -- one row per sample (100Hz), if ``sensors`` is None,
      4 columns are returned (trigger track, respiratory trace, cardiac trace,
      oxygen saturation). If ``sensors`` is specified the order of columns
      matches the order of the ``sensors`` sequence.
    """
    added_trigger = False
    if not sensors is None:
        if not 'trigger' in sensors:
            sensors = tuple(sensors) + ('trigger',)
            added_trigger = True
            trigger_mask = np.array([s != 'trigger' for s in sensors])
        trigger_column = sensors.index('trigger')
    else:
        trigger_column = 0
    data = []
    for i, r in enumerate(runs):
        rdata = get_run_physio_data(basedir, subj, task, r, sensors=sensors)
        triggers = rdata.T[trigger_column].nonzero()[0]
        if i > 0:
            # remove desired number samples at the front (except for first run)
            rdata = rdata[triggers[truncate]:]
        if i < len(runs) - 1:
            # remove desired number samples at the end (except for last run)
            rdata = rdata[:triggers[-truncate]]
        if added_trigger:
            data.append(rdata[:, trigger_mask])
        else:
            data.append(rdata)
    return np.vstack(data)

def check_timing(trigger_train, target_dist=200):
    triggerpos = trigger_train.nonzero()[0]
    td = np.diff(triggerpos) - target_dist
    return np.cumsum(td)

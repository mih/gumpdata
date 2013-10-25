import os
import numpy as np
import nose.tools as nt
import gumpdata

gd = gumpdata.GumpData()
subjs = gumpdata.subjs_by_task[1]
nvols = gumpdata.n_fmri_volumes_by_task[1]
runs = range(1,len(nvols) + 1)

def test_run_shape():
    """Tests for correct shape/size of all physio data"""
    for s in subjs:
        if s == 'phantom':
            # no physio data for phantom
            continue
        for r in runs:
            data = gd.get_run_physio_data(s, 1, r)
            triggers = data.T[0].nonzero()[0]
            ntriggers = len(triggers)
            # check n triggers
            nt.assert_equal(ntriggers, nvols[r-1])
            nt.assert_equal(data.shape[1], 4)
            # cumulative timing drift (target distance should be 200 samples
            # (2s@100Hz)
            cd = np.sum(np.diff(triggers) - 200)
            # less or equal to 30ms max drift per run (3@100Hz)
            nt.assert_true(cd <= 3)

def test_run_merge_truncation():
    """Test for correct truncation of run boundaries during merge"""
    nt.assert_equal(len(gd.get_physio_data(2, 1, sensors=('trigger',)).T.nonzero()[0]),
                    3543)
    nt.assert_equal(len(gd.get_physio_data(2, 1).T[0].nonzero()[0]),
                    3543)

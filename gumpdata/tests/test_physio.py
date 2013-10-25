import os
import numpy as np
import nose.tools as nt
import gumpdata

gd = gumpdata.GumpData()
subjs = gumpdata.subjs_by_task[1]
nvols = gumpdata.n_fmri_volumes_by_task[1]
runs = range(1,len(nvols) + 1)

def check_timing(trigger_train, target_dist=200):
    triggerpos = trigger_train.nonzero()[0]
    td = np.diff(triggerpos) - target_dist
    return np.cumsum(td)

def test_run_shape():
    """Tests for correct shape/size of all MOCO data"""
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

def _test_run_merge_truncation():
    """Test for correct truncation of run boundaries during merge"""
    nt.assert_equal(moco.get_moco_estimates(os.curdir, '002', 1).shape,
                    (3543,6))
    # this will cause a warning, but should work nevertheless
    from warnings import warn
    warn("ignore warning below -- only for testing purposes")
    nt.assert_equal(moco.get_moco_estimates(os.curdir, '002', 1,
                                            truncate_samples=10).shape,
                    (3459,6))

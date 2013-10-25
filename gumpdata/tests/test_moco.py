
import os
import nose.tools as nt
from gumpdata import GumpData
import gumpdata

gd = GumpData()

subjs = gumpdata.subjs_by_task[1]
runs = range(1,len(gumpdata.n_fmri_volumes_by_task[1]) + 1)
nvols = gumpdata.n_fmri_volumes_by_task[1]

def test_run_shape():
    """Tests for correct shape/size of all MOCO data"""
    for s in subjs:
        for r in runs:
            if s == '010':
                # no moco data for subj 010
                nt.assert_raises(IOError,
                                 gd.get_run_motion_estimates,
                                 s, 1, r)
                continue
            data = gd.get_run_motion_estimates(s, 1, r)
            if s == '004' and r == 8:
                nt.assert_equal(data.shape, (263, 6))
            else:
                nt.assert_equal(data.shape, (nvols[r-1], 6))

def test_run_merge_truncation():
    """Test for correct truncation of run boundaries during merge"""
    nt.assert_equal(gd.get_motion_estimates(2, 1).shape,
                    (3543,6))
    # this will cause a warning, but should work nevertheless
    from warnings import warn
    warn("ignore warning below -- only for testing purposes")
    nt.assert_equal(gd.get_motion_estimates(2, 1, truncate=10).shape,
                    (3459,6))

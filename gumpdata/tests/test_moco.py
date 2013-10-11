
import os
import nose.tools as nt
import gumpdata.io.motion as moco

subjs = ['%.3i' % i for i in range(1, 21)] + ['phantom']
runs = range(1,9)
nvols = (451, 441, 438, 488, 462, 439, 542, 338)

def test_run_shape():
    """Tests for correct shape/size of all MOCO data"""
    for s in subjs:
        for r in runs:
            if s == '010':
                # no moco data for subj 010
                nt.assert_raises(IOError,
                                 moco.get_run_motion_estimates,
                                 os.curdir, s, 1, r)
                continue
            data = moco.get_run_motion_estimates(os.curdir, s, 1, r)
            if s == '004' and r == 8:
                nt.assert_equal(data.shape, (263, 6))
            else:
                nt.assert_equal(data.shape, (nvols[r-1], 6))

def test_run_merge_truncation():
    """Test for correct truncation of run boundaries during merge"""
    nt.assert_equal(moco.get_motion_estimates(os.curdir, '002', 1).shape,
                    (3543,6))
    # this will cause a warning, but should work nevertheless
    from warnings import warn
    warn("ignore warning below -- only for testing purposes")
    nt.assert_equal(moco.get_motion_estimates(os.curdir, '002', 1,
                                            truncate=10).shape,
                    (3459,6))

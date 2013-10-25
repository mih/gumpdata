import os
import numpy as np
import nose.tools as nt
import gumpdata

gd = gumpdata.GumpData()
subjs = gumpdata.subjs_by_task[1]
nvols = gumpdata.n_fmri_volumes_by_task[1]
runs = range(1,len(nvols) + 1)


def test_fmri():
    """Tests for correct shape/size of all fmri data"""
    for flavor in ('',
                   'dico',
                   'dico7Tad2grpbold7Tad',
                   'dico7Tad2grpbold7Tad_nl'):
        for r in runs:
            r_shape = []
            for s in subjs:
                if flavor.startswith('dico'):
                    if s == '010' or (s == 'phantom' and flavor.startswith('dico7T')):
                        nt.assert_raises(IOError,
                                         gd.get_run_fmri,
                                         s, 1, r, flavor)
                        continue
                img = gd.get_run_fmri(s, 1, r, flavor)
                if s == '004' and r == 8:
                    # known dtaa problem
                    continue
                r_shape.append(img.get_shape())
                nt.assert_equal(nvols[r-1], img.get_shape()[3])
                if not nvols[r-1] == img.get_shape()[3]:
                    print s, r, flavor, nvols[r-1], img.get_shape()[3]
            nt.assert_equal(1, len(np.unique(r_shape)), msg="shape equal r%i" % r)

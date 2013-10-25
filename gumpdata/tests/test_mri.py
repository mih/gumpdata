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

def test_dti():
    """Tests for correct shape/size of all dti data"""
    shapes = []
    for s in [s for s in subjs if not s =='phantom']:
        img, bvals, bvecs = gd.get_dti(s)
        nt.assert_true(img.get_shape()[3] == len(bvals) == len(bvecs))
        nt.assert_equal(bvecs.shape, (33,3))
        nt.assert_equal(img.get_shape()[:3], (144,144,70))
        shapes.append(img.get_shape())
    nt.assert_equal(1, len(np.unique(shapes)), msg="cross-subj shape equal")

def test_swi():
    """Tests for correct shape/size of all swi data"""
    shapes = []
    for s in [s for s in subjs if not s =='phantom']:
        mag, pha = gd.get_swi(s)
        nt.assert_equal(mag.get_shape(), pha.get_shape())
        shapes.append(mag.get_shape())
    nt.assert_equal(1, len(np.unique(shapes)), msg="cross-subj shape equal")

def test_fieldmap():
    """Tests for correct shape/size of all fieldmap data"""
    shapes = []
    for s in [s for s in subjs if not s =='phantom']:
        mag, pha = gd.get_fieldmap(s)
        nt.assert_equal(mag.get_shape(), pha.get_shape())
        shapes.append(mag.get_shape())
    nt.assert_equal(1, len(np.unique(shapes)), msg="cross-subj shape equal")

def test_angio():
    """Tests for correct shape/size of all angio data"""
    shapes = []
    for s in [s for s in subjs if not s =='phantom']:
        img = gd.get_angio(s)
        if not s in ['002', '006']:
            shapes.append(img.get_shape())
    nt.assert_equal(1, len(np.unique(shapes)), msg="cross-subj shape equal")

def test_t1t2():
    """Tests for correct shape/size of all T1 and T2 data"""
    shapes = []
    for s in [s for s in subjs if not s =='phantom']:
        t1 = gd.get_t1(s)
        t2 = gd.get_t2(s)
        nt.assert_equal(t1.get_shape(), t2.get_shape())
        shapes.append(t1.get_shape())
    nt.assert_equal(1, len(np.unique(shapes)), msg="cross-subj shape equal")

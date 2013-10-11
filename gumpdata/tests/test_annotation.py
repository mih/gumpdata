import os
import numpy as np
import nose.tools as nt
import gumpdata.io.annotation as an

def test_scenes():
    scenes = an.get_scene_boundaries(os.curdir)
    nt.assert_true(len(scenes), 198)
    nt.assert_equal(np.array(scenes).dtype, float)
    # timestamps all incremental
    nt.assert_true((np.diff(scenes) > 0).all())

def test_german_ad():
    ts, tr = an.get_german_audiodescription_transcript(os.curdir)
    nt.assert_equal(np.array(ts).dtype, float)
    # one for each
    nt.assert_equal(len(ts), len(tr))
    # timestamps incremental
    nt.assert_true((np.diff(ts, axis=0) > 0).all())
    nt.assert_true((np.diff(ts, axis=1) > 0).all())


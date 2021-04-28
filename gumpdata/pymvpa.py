from .io import GumpData
from mvpa2.suite import fmri_dataset, vstack, h5save
import numpy as np

def mk_movie_dataset(gd, subj, mask, task=1, flavor='', filter=None,
        writeto=None, add_fa=None):
    cur_max_time = 0
    segments = []
    for seg in range(1,9):
        print 'Seg', seg
        ds = fmri_dataset(
                gd.get_run_fmri(subj, task, seg, flavor=flavor),
                mask=mask, add_fa=add_fa)
        if task == 1:
            # sanitize TR
            ds.sa.time_coords = np.arange(len(ds)) * 2.0
        mc = gd.get_run_motion_estimates(subj, task, seg)
        for i, par in enumerate(('mc_xtrans', 'mc_ytrans', 'mc_ztrans',
                                 'mc_xrot', 'mc_yrot', 'mc_zrot')):
            ds.sa[par] = mc.T[i]
        ds.sa['movie_segment'] = [seg] * len(ds)
        TR = np.diff(ds.sa.time_coords).mean()
        if not filter is None:
            print 'filter'
            ds = filter(ds)
        # truncate segment time series to remove overlap
        if seg > 1:
            ds = ds[4:]
        if seg < 8:
            ds = ds[:-4]
        ds.sa['movie_time'] = np.arange(len(ds)) * TR + cur_max_time
        cur_max_time = ds.sa.movie_time[-1] + TR
        if writeto is None:
            segments.append(ds)
        else:
            ds.samples = ds.samples.astype('float32')
            h5save(writeto % (subj, task, seg), ds, compression=9)
    return segments

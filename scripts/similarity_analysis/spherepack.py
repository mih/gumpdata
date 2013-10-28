def packing(dataset, radius=4, nifti=False, randoffset=False):
	"""return a hexagonal close sphere packing grid for a PyMVPA fMRI dataset
    
    Keyword arguments:
    radius-- radius in voxels of the spheres to pack (default 4)
    nifti-- write out a seed voxel mask as a nifti
    randomoffset-- random jitter of the seed voxel grid

    """
    
	from pylab import find, random
	from numpy import ones, zeros, arange, sqrt, remainder
	from mvpa2.suite import fmri_dataset, Dataset
	import os

	if randoffset:
		ro = random(3)
	else:
		ro = zeros(3)
	
	minco = dataset.fa.voxel_indices.min(0)
	maxco = dataset.fa.voxel_indices.max(0)
	rect = ones(dataset.a.voxel_dim)
	
	fac = sqrt(6)*2*radius/3
	for iz,z in enumerate(arange(minco[2], maxco[2], fac)):
		for iy,y in enumerate(arange(minco[1], maxco[1], fac)):
			for x in arange(minco[0], maxco[0], 2*radius):
				hx = x + remainder(iy, 2)*radius + ro[0]*radius
				hy = y + remainder(iz, 2)*fac + ro[1]*radius
				hz = z + ro[2]*radius
				if hz <= maxco[2]:
					rect [hx, hy, hz] += 1

	maskedrect = dataset.mapper.forward1(rect)
	roiIndex = find((maskedrect == 2))
	print  'number of seed voxel: '+str(len(roiIndex))
	
	maskedrectds = Dataset([maskedrect])
	maskedrectds.a = dataset.a.copy()
	maskedrectds.fa = dataset.fa.copy()
    
	if nifti:
		from nibabel import Nifti1Image
		Nifti1Image(maskedrectds.O.squeeze(),
					dataset.a.imghdr.get_best_affine()
					).to_filename(os.path.join('sparse'+str(int(radius))+'.nii.gz'))

	return roiIndex, maskedrectds
	
def fx(sl, dataset, roi_ids, results):
    """this requires the searchlight conditional attribute 'roi_feature_ids'
    to be enabled"""

    import numpy as np
    from mvpa2.datasets import Dataset

    resmap = None
    probmap = None
    for resblock in results:
        for res in resblock:
            if resmap is None:
                # prepare the result container
                resmap = np.zeros((len(res), dataset.nfeatures), dtype=res.samples.dtype)
                observ_counter = np.zeros(dataset.nfeatures, dtype=int)
            #project the result onto all features -- love broadcasting!
            resmap[:, res.a.roi_feature_ids] += res.samples
            # increment observation counter for all relevant features
            observ_counter[res.a.roi_feature_ids] += 1
    # when all results have been added up average them according to the number
    # of observations
    observ_mask = observ_counter > 0
    resmap[:, observ_mask] /= observ_counter[observ_mask]
    # transpose to make broadcasting work -- creates a view, so in-place
    # modification still does the job
    result_ds = Dataset(resmap,
                        fa={'observations': observ_counter})
    if 'mapper' in dataset.a:
        import copy
        result_ds.a['mapper'] = copy.copy(dataset.a.mapper)
    return result_ds

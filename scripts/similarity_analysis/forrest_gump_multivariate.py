'''Computes a multivariate consistency map between two subjects (subj1 and subj2)
	Keyword arguments:
	-subj1-- subject code as in the openfmri.org-folder
	-subj2-- subject code as in the openfmri.org-folder
	-nproc-- number of processor for parallelization of the searchlight
	-align-- linear or nonlinear
	e.g. python forrest_gump_multivariate.py -subj1 sub001 -subj2 sub002 -nproc 4 -align linear
	output-- nifti-image maps/sl_*subj1*_*subj2*_s4_sparse2_*align*_multivariate.nii.gz
'''

import matplotlib as mpl
mpl.use('Agg')
import mvpa2.suite as mvpa
import numpy as np
import scipy.spatial.distance as sd
import nibabel as nb
import os, sys, glob
import Bio.Cluster
import myaggregate
import spherepack

#Input arguments
def GetArg():
    thisarg = sys.argv[0]
    del sys.argv[0]
    return thisarg

while len(sys.argv) > 0:
	carg = GetArg()
	if carg == '-subj1':
		subj1 =  GetArg()
	if carg == '-subj2':
		subj2 =  GetArg()
	if carg == '-nproc':
		nproc =  GetArg()
	if carg == '-align':
		align = GetArg()
        
mvpa.debug.active += ["SLC"]

#Set working and data directory
path = os.path.join('/home','data','exppsy','baumgartner','forrestgump')
datapath = os.path.join('/home','data','exppsy','forrest_gump','openfmri.org')

##Parameter
sp = 4				#searchlight sphere radius
sparse = 2			#packing sphere radius
zsc = 1				#Voxelwise zscoring
samples_size = 12	#Length of segments in sec
TR = 2				#Repetition time

#Define mask and create reference mask dataset
if align=='nonlinear':
	maskfile = os.path.join(datapath,'templates', 'grpbold7Tad','qa', 'dico7Tad2grpbold7Tad_nl','brain_mask_intersection.nii.gz')
elif align=='linear':
	maskfile = os.path.join(datapath,'templates', 'grpbold7Tad','qa', 'dico7Tad2grpbold7Tad7Tad','brain_mask_intersection.nii.gz')
ds = mvpa.fmri_dataset(maskfile, mask=maskfile)

#Load dataset of two subjects
dsfile = '_z'+str(zsc)+'_'+str(samples_size)+'_'+align
evds1 = mvpa.h5load(os.path.join('dataset',subj1+dsfile+'.hdf5'))
evds2 = mvpa.h5load(os.path.join('dataset',subj2+dsfile+'.hdf5'))
evds = mvpa.vstack([evds1,evds2])
del evds1, evds2

#Determine sphere center voxel 
roiIndex, maskedrectds =  spherepack.packing(ds, radius=sparse, nifti=True,randoffset=True)
evds.fa['1stidx'].value[:] = False
evds.fa['1stidx'].value[roiIndex] = True

#Prepare representational similarity analysis measure
class RSA(mvpa.Measure):
    is_trained = True
    def __init__(self,subj1,subj2, **kwargs):
		mvpa.Measure.__init__(self, **kwargs)
		self._subj1 = subj1
		self._subj2 = subj2
	def _call(self, evds):
		dsm1 = sd.pdist(evds[evds.sa.subj==self._subj1].samples, metric='correlation')
		dsm2 = sd.pdist(evds[evds.sa.subj==self._subj2].samples, metric='correlation')
	res = 1-Bio.Cluster.distancematrix(np.vstack((dsm1,dsm2)),dist='s')[1][0]
	return mvpa.Dataset(np.array(res)[np.newaxis])

#Call representational similarity analysis measure
rsa = RSA(subj1,subj2)

#Prepare Searchlight
sl = mvpa.Searchlight(rsa,
			mvpa.IndexQueryEngine(
					voxel_indices=mvpa.Sphere(sp),
					event_offsetidx=lambda x: range(samples_size / TR)),
			roi_ids='1stidx',
			postproc=mvpa.mean_sample(),
			results_fx=spherepack.fx,
			nproc=int(nproc),
			enable_ca=['roi_feature_ids'])

#Iterate the Representational similarity analysis measure over all searchlight spheres
slmap = sl(evds)

#Name the output
filename = 'sl_'+subj1+'_'+subj2+'_s'+str(sp)+'_sparse'+str(sparse)+dsfile

#Mapping of the searchlight results into group template space
nimg = mvpa.map2nifti(ds, slmap.samples[:,:ds.nfeatures], imghdr=ds.a.imghdr)

#Save result as nifti in maps directory 
try:
    os.mkdir(os.path.join(path,'maps'))
except:
    print 'maps directory already exists'
    
nb.Nifti1Image(nimg.get_data(),
			nimg.get_header().get_best_affine()
			).to_filename(os.path.join(path,'maps',filename + '_multivariate.nii.gz'))

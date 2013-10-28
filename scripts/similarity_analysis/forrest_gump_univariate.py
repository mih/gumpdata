'''Computes a univariate inter-subject correlation map between two subjects
	Keyword arguments:
	-subj1-- subject code 
	-subj2-- subject code
	-nproc-- number of processor for parallelization of the searchlight
	-align-- linear or nonlinear
	e.g. python forrest_gump_univariate.py -subj1 sub001 -subj2 sub002 -nproc 4 -align linear
	output-- nifti-image maps/sl_*subj1*_*subj2*_s4_sparse2_*align*_univariate.nii.gz
'''

import matplotlib as mpl
mpl.use('Agg')
import mvpa2.suite as mvpa
import numpy as np
import scipy.spatial.distance as sd
import nibabel as nb
import os, sys, glob

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
zsc = 1				#Voxelwise zscoring
samples_size = 12	#Length of segments in sec

if align=='nonlinear':
	maskfile = os.path.join(datapath,'templates', 'grpbold7Tad','qa', 'dico7Tad2grpbold7Tad_nl','brain_mask_intersection.nii.gz')
elif align=='linear':
	maskfile = os.path.join(datapath,'templates', 'grpbold7Tad','qa', 'dico7Tad2grpbold7Tad7Tad','brain_mask_intersection.nii.gz')

ds = mvpa.fmri_dataset(maskfile, mask=maskfile)
dsfile = '_z'+str(zsc)+'_'+str(samples_size)+'_'+align

#Load dataset of two subjects and reorganise for univariate analysis
evds1 = mvpa.h5load(os.path.join('dataset',subj1+dsfile+'.hdf5'))
evds1 = evds1.mapper.reverse(evds1)
evds2 = mvpa.h5load(os.path.join('dataset',subj2+dsfile+'.hdf5'))
evds2 = evds1.mapper.reverse(evds2)
evds = mvpa.vstack([evds1,evds2])
del evds1, evds2

# Prepare inter-subject correlation measure
class Corr(mvpa.Measure):
	is_trained = True
	def __init__(self,subj1,subj2, **kwargs):
		mvpa.Measure.__init__(self, **kwargs)
		self._subj1 = subj1
		self._subj2 = subj2
	def _call(self, evds):
		res = 1-sd.pdist(np.hstack((evds[evds.sa.subj==self._subj1].samples,evds[evds.sa.subj==self._subj2].samples)).T,'correlation')
		return mvpa.Dataset(np.array(res)[np.newaxis])

# Call inter-subject correlation measure
cor = Corr(subj1,subj2)

# Prepare single voxel Searchlight
sl = mvpa.Searchlight(cor,
			mvpa.IndexQueryEngine(
					voxel_indices=mvpa.Sphere(0)),
			nproc=int(nproc))

#Iterate the inter-subject correlation measure over all voxels
slmap = sl(evds)

# Name the output
filename = 'sl_'+subj1+'_'+subj2+dsfile

# Mapping of the searchlight results into group template space
nimg = mvpa.map2nifti(ds, slmap.samples[:,:ds.nfeatures], imghdr=ds.a.imghdr)

#Save result as nifti in maps directory
try:
    os.mkdir(os.path.join(path,'maps'))
except:
    print 'maps directory already exists'

# Save result as nifti in maps directory 
nb.Nifti1Image(nimg.get_data(),
			nimg.get_header().get_best_affine()
			).to_filename(os.path.join(path,'maps',filename + '_univariate.nii.gz'))
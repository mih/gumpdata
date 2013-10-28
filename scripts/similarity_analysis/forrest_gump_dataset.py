'''Prepare PyMVPA dataset of the multivariate consistency (forrest_gump_multivariate.py) or inter-subject correlation (forrest_gump_univariate.py) analyses
	Keyword arguments:
	-subj-- subject code as in the openfmri.org-folder
	e.g. python forrest_gump_dataset.py -subj sub001
	output-- dataset/*subj*_z1_12_*align'.hdf5'
'''

import matplotlib as mpl
mpl.use('Agg')
import mvpa2.suite as mvpa
import numpy as np
import nibabel as nb
import os,sys,glob
from scipy import signal


def GetArg():
	thisarg = sys.argv[0]
	del sys.argv[0]
	return thisarg

while len(sys.argv) > 0:
	carg = GetArg()
	if carg == '-subj':
		subj =  GetArg()
	if carg == '-align':
		align = GetArg()

mvpa.debug.active += ["SLC"]

#Set working and data directory
path = os.path.join('/home','data','exppsy','baumgartner','forrestgump')
datapath = os.path.join('/home','data','exppsy','forrest_gump','openfmri.org')

## Parameter
zsc = 1				#Voxelwise zscoring
samples_size = 12	#Length of segments in sec
TR = 2				#Repetition time
lf = 150.			#lowpass in sec
hf = 9.				#highpass in sec

if align=='nonlinear':
	boldfile = 'bold_dico_dico7Tad2grpbold7Tad_nl.nii.gz'
	maskfile = os.path.join(datapath,'templates', 'grpbold7Tad','qa', 'dico7Tad2grpbold7Tad_nl','brain_mask_intersection.nii.gz')
elif align=='linear':
	boldfile = 'bold_dico_dico7Tad2grpbold7Tad.nii.gz'
	maskfile = os.path.join(datapath,'templates', 'grpbold7Tad','qa', 'dico7Tad2grpbold7Tad','brain_mask_intersection.nii.gz')

boldlist = np.sort(glob.glob(os.path.join(datapath,subj,'BOLD','task001*')))

print subj

#Concatenate segments and remove presentation overlap at the end and begin of each segment
Ds = []
for i,run in enumerate(boldlist):
	print run
	ds = mvpa.fmri_dataset(os.path.join(datapath,run,boldfile), mask=maskfile)	
	mc = mvpa.McFlirtParams(os.path.join(run, 'bold_dico_moco.txt'))
	for param in mc:
		ds.sa['mc_' + param] = mc[param]
	if i==0:
		ds = ds[:-4]
	elif i<7:
		ds = ds[4:-4]
	else:
		ds = ds[4:]
	ds.sa['chunks'] = np.ones(ds.nsamples)*i
	print ds.shape
	Ds.append(ds)
	
ds = mvpa.vstack(Ds)
ds.samples = ds.samples.astype('float32')

#Detrending and MC removal
mvpa.poly_detrend(ds,
		  opt_regs=['mc_'+param  for param in mc],
		  chunks_attr='chunks'
		  )
		  
#Voxelwise Zscore
if zsc:
	mvpa.zscore(ds)

#bandpass filter
nf = 0.5/TR
ws = [(1/lf)/nf, (1/hf)/nf]
b, a = signal.butter(5, ws, btype='band')
S = [signal.filtfilt(b, a, x) for x in ds.samples.T]
ds.samples = np.array(S).T
ds.samples = ds.samples.astype('float32')

#Create Event-related Dataset
onsets = np.arange(0,ds.nsamples - samples_size/TR, samples_size/TR)
events = []
for on in onsets:
	Ev = dict()
	Ev['onset'] = on
	Ev['duration'] = samples_size / TR
	Ev['target'] = on*TR
	Ev['subj'] = subj
	events.append(Ev)

evds = mvpa.eventrelated_dataset(ds, events=events)
evds.fa['1stidx'] = evds.fa.event_offsetidx==0

#Save pymvpa-dataset as hdf5 in dataset directory 
try:
    os.mkdir(os.path.join(path,'dataset'))
except:
    print 'results directory already exists'

dsfile = subj+'_z'+str(zsc)+'_'+str(samples_size)+'_'+align
mvpa.h5save(os.path.join(path,'dataset',dsfile+'.hdf5'), evds, compression='gzip')
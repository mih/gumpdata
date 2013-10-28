'''Group statistics of the multivariate consistency map (forrest_gump_multivariate.py) or inter-subject correlation map (forrest_gump_univariate.py)
	Keyword arguments:
	-typ-- multivariate or univariate
	-align-- linear or nonlinear
	e.g. python forrest_gump_groupresults.py -typ multivariate -align linear
	output-- nifti-image results/coactivation_*align*_*typ*.nii.gz
			 nifti-image results/mean_coactivation_*align*_*typ*.nii.gz
			 nifti-image results/mean_coactivation_*align*_*typ*_mni.nii.gz
			 nifti-image results/mean_coactivation_*align*_*typ*_pvalues.nii.gz
			 nifti-image results/mean_coactivation_*align*_*typ*_pvalues_mni.nii.gz
			 nifti-image results/coactivation_*align*_*typ*.nii.gz
'''

import numpy as np
import nibabel as nb
import pylab as pl
import os, glob, sys

def GetArg():
	thisarg = sys.argv[0]
	del sys.argv[0]
	return thisarg

while len(sys.argv) > 0:
	carg = GetArg()
	if carg == '-typ':
		typ =  GetArg()
	if carg == '-align':
		align = GetArg()

#Set working and data directory
path = os.path.join('/home','data','exppsy','baumgartner','forrestgump')
datapath = os.path.join('/home','data','exppsy','forrest_gump','openfmri.org')

resultfile = 'coactivation_'+align+'_'+typ

if align=='nonlinear':
	maskfile = os.path.join(datapath,'templates', 'grpbold7Tad','qa', 'dico7Tad2grpbold7Tad_nl','brain_mask_intersection.nii.gz')
elif align=='linear':
	maskfile = os.path.join(datapath,'templates', 'grpbold7Tad','qa', 'dico7Tad2grpbold7Tad7Tad','brain_mask_intersection.nii.gz')

#Read in all inter-subject maps
maps = glob.glob(os.path.join(path,'maps','sl_sub0*_sub0*'+'_'+align+'_'+typ+'.nii.gz'))
maps.sort()
K = []
for m in maps:
    K.append(nb.load(m).get_data())
    print m, K[-1].shape

print 'number of maps: '+str(len(maps))
K = np.array(K)
#Compute the mean inter-subject map
mK = np.mean(K,0)

#Convert mean correlations in percent rank of the pooled correlation values
k = np.sort(np.reshape(K[K!=0],-1))
mk = mK[mK!=0]
L = np.vstack((np.hstack((k,mk)),np.hstack((-np.ones(len(k)),range(len(mk))))))
sL = L[:,np.argsort(L[0])]
U = np.vstack((sL[1,sL[1]>-1],pl.find(sL[1]>-1)-np.arange(len(mk))))
prank = U[1,np.argsort(U[0])]/float(len(k))
pK = mK.copy()
pK[mK!=0] = prank

#Load mask
M = nb.load(maskfile)

#Plot correlation value distribution and save figure in in result directory
try:
    os.mkdir(os.path.join(path,'results'))
except:
    print 'results directory already exists'

Thres = [0,.25,.5,.75, .9, .95, .99, .995]
rthres = []
for t in Thres:
	rthres.append(k[len(k)*t])
rthres.append(k[-1])

mk = mK[mK!=0]
mk.sort()
mkthres = []
for t in Thres:
	mkthres.append(mk[len(mk)*t])
mkthres.append(mk[-1])

fig = pl.figure(figsize=(12,12),facecolor='w')
ax1 = pl.subplot2grid((6, 1), (0, 0), rowspan=2)
kh = np.histogram(k,500, density=True)
mKh = np.histogram(mK[mK!=0],500, density=True)
pl.plot(kh[1][:-1],np.cumsum(kh[0]*np.diff(kh[1])))
pl.plot(mKh[1][:-1],np.cumsum(mKh[0]*np.diff(mKh[1])))

for i,t in enumerate(rthres):
	pl.plot([t,t],[0,Thres[i]],'k:',lw=1)
	pl.plot([rthres[0],t],[Thres[i],Thres[i]],'k:',lw=1)
	if Thres[i]>.95:
		pl.text(t,.955,str(sum(pK>Thres[i])), color='k',rotation=90)
	
ax1.spines['bottom'].set_visible(False)
ax1.xaxis.tick_top()
pl.axis([rthres[0],k.max(),0.95,1.005])

ax2 = pl.subplot2grid((6, 1), (2, 0), rowspan=4)
pl.plot(kh[1][:-1],np.cumsum(kh[0]*np.diff(kh[1])))
pl.plot(mKh[1][:-1],np.cumsum(mKh[0]*np.diff(mKh[1])))

for i,t in enumerate(rthres):
	pl.plot([t,t],[0,Thres[i]],'k:',lw=1)
	pl.plot([rthres[0],t],[Thres[i],Thres[i]],'k:',lw=1)

ax2.spines['top'].set_visible(False)
ax2.xaxis.tick_bottom()
pl.xlabel('Correlation')
pl.ylabel('Empirical culumlative distribution')
pl.axis([rthres[0],k.max(),0,1.1])
pl.legend(loc=4)
pl.savefig(os.path.join(path,'results','cumhist_'+resultfile+'.pdf'))
pl.show()

#Save mean correlation maps as nifti in result directory
nb.Nifti1Image(mK,
	M.get_header().get_base_affine()
	).to_filename(os.path.join(path,'results','mean_'+resultfile+'.nii.gz'))
#Transform mean correlation map into MNI
os.system('fsl5.0-flirt -in '+os.path.join(path,'results','mean_'+resultfile)+' -applyxfm -init '+os.path.join(path,'templates','tmpl2mni_12dof.mat')+' -out '+os.path.join(path,'results','mean_'+resultfile+'_mni')+' -paddingsize 0.0 -interp trilinear -ref /usr/share/data/fsl-mni152-templates/MNI152_T1_1mm_brain')

#Save percent rank map as nifti in result directory
nb.Nifti1Image(pK,
	M.get_header().get_base_affine()
	).to_filename(os.path.join(path,'results','mean_'+resultfile+'_pvalue.nii.gz'))
#Transform percent rank map into MNI
os.system('fsl5.0-flirt -in '+os.path.join(path,'results','mean_'+resultfile+'_pvalue')+' -applyxfm -init '+os.path.join(path,'templates','tmpl2mni_12dof.mat')+' -out '+os.path.join(path,'results','mean_'+resultfile+'_pvalue_mni')+' -paddingsize 0.0 -interp trilinear -ref /usr/share/data/fsl-mni152-templates/MNI152_T1_1mm_brain')


#Save all inter-subject correlation maps as nifti in result directory
K = np.rollaxis(K,0,4)
nb.Nifti1Image(K, M.get_header().get_best_affine()).to_filename(os.path.join(path,'results',resultfile+'.nii.gz'))
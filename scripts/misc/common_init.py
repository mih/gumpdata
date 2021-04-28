from os.path import join as _opj
from mvpa2.datasets.sources import OpenFMRIDataset

datapath = "/home/data/psyinf/forrest_gump/anondata"
logpath = _opj(os.path.dirname(datapath), 'condor_logs')

# dataset handler
of = OpenFMRIDataset(datapath)

# preamble for a condor submit file
condor_submit_preamble = """
universe = vanilla
output = %(logpath)s/$(CLUSTER).$(PROCESS).out
error = %(logpath)s/$(CLUSTER).$(PROCESS).err
log = %(logpath)s/$(CLUSTER).$(PROCESS).log
initialdir = %(datapath)s
getenv = True
should_transfer_files = NO
transfer_executable = False
""" % dict(datapath=datapath, logpath=logpath)

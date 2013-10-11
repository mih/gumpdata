# list of all task IDs in the dataset
tasks = [1]
# list of subjects for all tasks
subjs_by_task = {
  1: ['%.3i' % i for i in range(1, 21)] + ['phantom']
}
# number of fMRI volume per run per task
n_fmri_volumes_by_task = {
  1: (451, 441, 438, 488, 462, 439, 542, 338)
}


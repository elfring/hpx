<!-- Copyright (c) 2014 John Biddiscombe                                          -->
<!--                                                                              -->
<!-- Distributed under the Boost Software License, Version 1.0. (See accompanying -->
<!-- file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)        -->

Not Finished yet.


The network storage benchmark comes with several files

##################################################
# What the files are for
##################################################
network_storage.cpp 
------------------------------
This is the code for the test.

network_storage.bat.in 
------------------------------
This is a windows batch file template which will be filled in using cmake substitution
and then copied to your build/scripts directory.
The generated script can be invoked to run the benchmark in serial or parallel. 
It spawns each task on the same node so although you may run 4 copies, 
they are competing for resources. 
The windows version is good for testing and debugging on a single node.
adding or removing /B for the launch command in the script
controls whether each task is launched in a new console window or not
example usage (2 tasks)
scripts/network_storage.bat 2

slurm-test-HPX-storage.sh.in
------------------------------
This is a bash script template which will be filled in using cmake substitution
and then copied to your build/scripts directory.
When executed, the script will loop over a number of parameter combinations
and for each generate a directory with a name generated from the params, like
  hpx-N0002-T02048-t04-ibverbs
and inside it there will be a "submit-job.bash" script which contains a single
slurm job submission. you can manually submit just one job using "sbatch submit-job.bash", 
or in the root of the scripts folder there will be generated another script 
which is called "run_jobs.bash". When this script is run, it will loop over
all the jobs that were created by the first script and submit all jobs, you
can then sit back and wait until they complete.
Each job will write its results into "slurm.out" in the 

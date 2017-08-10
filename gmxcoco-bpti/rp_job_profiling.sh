#!/bin/bash

# if set to 1 RP will spit out a time profile of job
# not sure where though. It will make a CSV file though
# ask vivek where it will be. might be on cluster in last
# unit or something


# note that running this bash script does not seem to set the enviroment variable 
# however copy and past this line below into terminal and it will set it 
# properly and simulation will give profiling info

export RADICAL_ENMD_PROFILING=1; echo "RADICAL_ENMD_PROFILING="$RADICAL_ENMD_PROFILING



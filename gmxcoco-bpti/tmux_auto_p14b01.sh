#!/bin/bash 


#p12b02_left_d3_itrs48_k12_100_k34_100

for i in p14b01*; 
do 
	sess="$i" 
	dir="$i"
	window=${sess}:0
	tmux new-session -d -s  $sess  
	tmux send -t $sess.0 "cd $dir/" Enter
	tmux send -t $sess.0 "source ~/Documents/jha/extasy-tools/bin/activate"  Enter
	tmux send -t $sess.0 "export RADICAL_ENMD_PROFILING=1" Enter
	tmux send -t $sess.0 "python nwexgmx_v002.py --RPconfig supermic.rcfg --Kconfig gmxcoco.wcfg" Enter 
done 
#tmux send -t $sess.0 "echo $\RADICAL_ENMD_PROFILING" Enter
#tmux send -t $sess.0 





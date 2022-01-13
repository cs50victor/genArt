#!/bin/bash
set  im_size=256
#If you choose cuda, make sure you select GPU under [Runtime]-[Change runtime type]
set device=cuda
#Set where you want NBB results to be saved
set pts_path="example/NBBresults"
#Set paths and other parameters for cleaning points
set  activation_path="example/NBBresults/correspondence_activation.txt"
set  output_path="example/CleanedPts"
set  NBB=1
set max_num_points=80
set  b=10
# 
set output_dir="example/DSTresults"
set max_iter=250
set checkpoint_iter=50
set content_weight=8
set warp_weight=0.5
set reg_weight=50
set optim=sgd
set lr=0.2
set verbose=0
set save_intermediate=0
set save_extra=0

echo "Done with setting env variables"
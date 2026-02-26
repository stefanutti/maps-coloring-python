 #!/bin/bash

for iLoop in `seq 1 10000`;
do
   echo "-----------------"
   echo "-----------------"
   echo "-----------------"
   echo $iLoop
   echo "-----------------"
   echo "-----------------"
   echo "-----------------"
   if [ -f "error.txt" ]
   then
      rm error.txt
   fi

   vertices=`awk -v min=10 -v max=100 'BEGIN {srand(); print int(min + rand() * (max - min + 1))}'`
   sage ../ct/4ct.py -r $vertices

   if [ -f "error.txt" ]
   then
      mv debug.previous_run.planar debug.random.previous_run.planar.$iLoop
      mv debug.previous_run.edgelist debug.random.previous_run.edgelist.$iLoop
      mv debug.really_bad_case.edgelist debug.random.really_bad_case.edgelist.$iLoop
      mv debug.really_bad_case.dot debug.random.really_bad_case.dot.$iLoop
   fi
done  

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

   vertices=`awk -v min=200 -v max=400 'BEGIN {srand(); print int(min + rand() * (max - min + 1))}'`
   sage 4ct.py -r $vertices

   if [ -f "error.txt" ]
   then
      mv debug.input_planar_g_faces.serialized debug.random.input_planar_g_faces.serialized.$iLoop
      mv debug.input_planar_g_faces.embedding_list debug.random.input_planar_g_faces.embedding_list.$iLoop
      mv debug.really_bad_case.edgelist debug.random.really_bad_case.edgelist.$iLoop
      mv debug.really_bad_case.dot debug.random.really_bad_case.dot.$iLoop
   fi
done  

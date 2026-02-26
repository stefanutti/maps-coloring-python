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
      exit -1
   fi

   sage ../ct/4ct.py -p debug.random.input_planar_g_faces.serialized.100

   if [ -f "error.txt" ]
   then
      mv debug.input_planar_g_faces.serialized debug.one.input_planar_g_faces.serialized.$iLoop
      mv debug.input_planar_g_faces.embedding_list debug.one.input_planar_g_faces.embedding_list.$iLoop
      mv debug.really_bad_case.edgelist debug.one.really_bad_case.edgelist.$iLoop
      mv debug.really_bad_case.dot debug.one.really_bad_case.dot.$iLoop
   fi
done  

#!/bin/bash
${CXX} -lm -Wall -O -g ./main_unittest.cxx ../src/bmi_soil_freeze_thaw.cxx ../src/soil_freeze_thaw.cxx -o run_sft
./run_sft configs/unittest.txt
rm -f run_sft
rm -rf run_sft.dSYM

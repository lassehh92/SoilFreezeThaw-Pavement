#!/bin/bash

# Create 'logs' directory if it doesn't exist
if [ ! -d "logs" ]; then
    mkdir logs
fi

# Set log file name based on current date and time
log_filename="logs/$(date +'%Y-%m-%d_%H-%M-%S').log"

# Redirect stdout and stderr to the log file
exec > >(tee -a "$log_filename") 2>&1

option=$1

if [ ! $# == 1 ]; then
    echo "Usage: $0 OPTION={STANDALONE,PFRAMEWORK}"
    echo "One of these options must be specified to run SFT model"
    exit
fi

if [ $option == "STANDALONE" ] || [ $option == "PFRAMEWORK" ]; then
    echo "SFT model running with option $option"
else
    echo "Invalid option! $option"
    exit
fi

args=" "
exe_name=" "
if [ $option == "STANDALONE" ]; then
    args='./configs/laramie_config_standalone.txt'
    exe_name='sft_standalone'
elif [ $option == "PFRAMEWORK" ]; then
    #args="./configs/dansani_config_sft.txt ./configs/dansani_config_smp.txt"
    #args="./configs/dansani_config_sft_dz_1cm.txt ./configs/dansani_config_smp_dz_1cm.txt"
    #args="./configs/dansani_config_sft_dz_3cm.txt ./configs/dansani_config_smp_dz_3cm.txt"
    args="./configs/dansani_config_sft_dz_3cm_spinup.txt ./configs/dansani_config_smp_dz_3cm.txt"
    #args="./configs/dansani_config_sft_dz_3cm_transient.txt ./configs/dansani_config_smp_dz_3cm.txt"
    exe_name='sft_pframework'
fi

echo "config file: $args"
./build/${exe_name} $args

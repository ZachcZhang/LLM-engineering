#!/bin/env bash

# load settings
module load anaconda3
conda init
source ~/.bash_profile # activate conda command 
conda activate deepspeed
module load cuda/12.0 
module load pdsh-2.29
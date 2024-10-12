#!/bin/bash
#SBATCH --job-name=test_zc1
#SBATCH --nodes=2               # 请求3个节点
#SBATCH --ntasks-per-node=8     #每个节点上8个任务
#SBATCH --cpus-per-task=8       #每个任务使用8个cpu核
#SBATCH --gres=gpu:8            # 每个节点8个GPU
#SBATCH --time=02:00:00         # 最大运行时间2小时
#SBATCH --partition=czhangcn_rent # 替换为你的分区名
#SBATCH --nodelist=gpu1-14,gpu1-18 #指定节点运行
#SBATCH --output=%j.out
#SBATCH --error=%j.error

module load anaconda3
conda init
source ~/.bash_profile
conda activate deepspeed
module load cuda/11.7

echo "SLURM_JOBID: " $SLURM_JOBID
echo "SLURM_ARRAY_TASK_ID: " $SLURM_ARRAY_TASK_ID
echo "SLURM_ARRAY_JOB_ID: " $SLURM_ARRAY_JOB_ID
echo "SLURM_LOCALID: " $SLURM_LOCALID
echo "SLURM_JOB_NODELIST:" $SLURM_JOB_NODELIST
echo "SLURM_PROCID: " $SLURM_PROCID
echo "SLURM_LOCALID:" $SLURM_LOCALID
echo "SLURM_NTASKS: " $SLURM_NTASKS
echo "SLURM_STEP_NODELIST: " $SLURM_STEP_NODELIST

#srun ./run_ds.sh 
export NUM_NODES=2
export NUM_GPUS=16

# Size of expert parallel world (should be less than total world size)
master_addr=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_ADDR=$master_addr
export MASTER_PORT="30001"
code_path="~/LLM-engineering/Deepspeed/cifar10/" # please change to your own code path
export HOSTFILE=$code_path"hostfile"

deepspeed  --num_nodes $NUM_NODES \
    --num_gpus $NUM_GPUS \
	--hostfile $HOSTFILE \
    --master_addr $MASTER_ADDR \
	--master_port $MASTER_PORT \
    --launcher SLURM \
    ${code_path}"cifar10_deepspeed-temp.py" \
    --deepspeed \
    --log-interval 100
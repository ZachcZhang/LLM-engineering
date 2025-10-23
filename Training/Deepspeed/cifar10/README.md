## 使用说明
本例子参考项目:[DeepSpeedExamples](https://github.com/microsoft/DeepSpeedExamples)  training/cifar的例子，做了修改以支持**多机多卡**，帮助更好的学习使用deepspeed。
- 请安装DeepSpeed等相关依赖.
- 修改run-muti-node.sh脚本的#SBATCH --nodelist 、 hostfile文件为你的GPU机器。
- 修改代码为您的路径，执行方式: sbatch run-muti-node.sh
# 机器人语音合成功能模块
# 使用教程
### 下载预训练模型
所有的
```
python ASVspoof15&19_LA_Data_Preparation.py 
```
It generates audio of fixed length from the given dataset.
### Training
```
python train.py
```
We use focal loss to train the model, which solves the problem of difficult classification samples to some extent. The training records are saved in log files, and the model files are saved every epoch of training.
### Testing
```
python test.py
```
It generates the model's output softmax accuracy, and EER.

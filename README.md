DataCollect
====
the Meter data collecting program<br>
适用于威胜DDZY102-Z单相费控智能电能表<br> 
USB2.0 FT232RL to RS422/RS485 <br> 

当前版本特性
- 多电表
- 可运行时添加电表
- 自动扫描设备 
- 仅有耗电量 
- 余电量预设100

#### 安装模块
```
pip install serial
pip install MySQL-python==1.2.5
pip install argparse
pip install logging
```

#### 查看日志
日志在 ~/access-point/logs/powerconsume.log
```shell
tail -f ~/access-point/logs/powerconsume.log
```
#### 启动
-h参数查看帮助信息
```shell
root@accesspoint-ThinkPad-X240:~# python powerconsume.py -h
usage: powerconsume.py [-h] [-m METER] [-a ADD]

Multi meter acquisition program

optional arguments:
  -h, --help            show this help message and exit
  -m, --meter           Initial start up list
  -a, --add             Add new meters into collect program
```

初始化启动 通过-m 参数指定==待启动==电表id 
```python
python powerconsume.py -m 电表id1,电表id2,电表id3
```

启动过程中如需添加电表可通过 -a 参数指定==待添加==电表id
```python
python powerconsume.py -a 电表id4 -a 电表id5
```
若不加任何参数，则按默认电表组 ["1605343448000232","1605343453000135"] 启动采集程序
# EC600MCNLE POC Demo 使用说明

## 概述

此 demo 在搭载`EC600MCNLE`模组的开发板上开发，麦克风和按键用的是开发板上的，屏幕采用分辨率为`240×240`的`ST7789`，外接一个喇叭到开发板作为音频输出。

- `code`：所有的代码文件
- `firmware`：模组固件包

固件和脚本烧录方法：[QPYcom 固件脚本下载 - QuecPython (quectel.com)](https://python.quectel.com/doc/Application_guide/zh/dev-tools/QPYcom/qpycom-dw.html)

## 1. 外设

### 1.1 LCD

- 型号：ST778
- 分辨率：240×240

> LCD初始化详情参考移远wiki：[LCD显示屏](https://python.quectel.com/doc/API_reference/zh/peripherals/machine.LCD.html)

### 1.2 按键

基于开发板上对应的KEY1、KEY2

| KEY  |         引脚          |                           功能说明                           |
| :--: | :-------------------: | :----------------------------------------------------------: |
| KEY1 | 引脚号60  ---  GPIO13 |                           长按说话                           |
| KEY2 | 引脚号59  ---  GPIO12 | 单击：列表滚动<br />双击：选择当前列表<br />长按：返回上一级目录<br /> |

> 按键中断详情参考：[ExtInt - 外部中断](https://python.quectel.com/doc/API_reference/zh/peripherals/machine.ExtInt.html)

### 1.3 音频

|           接口           |                 引脚                 |      说明      |
| :----------------------: | :----------------------------------: | :------------: |
|          麦克风          | MIC_N：引脚号23<br />MIC_P：引脚号24 |    说话录音    |
| 听筒<br />（需外接听筒） | SPK_N：引脚号21<br />SPK_P：引脚号22 | 播放收到的音频 |

## 2. 程序分析

### 2.1 目录结构

```plaintext
.
├── README.MD
├── code
│   ├── common.py
│   ├── dev
│   │   ├── key.py
│   │   └── lcd.py
│   ├── img
│   │   ├── battery_1.png
│   │   ├── battery_2.png
│   │   ├── ......
│   │   └── signal_5.png
│   ├── poc_main.py
│   ├── services.py
│   └── ui
│       ├── styles.py
│       └── ui.py
└── firmware
    └── EC600MCNLER06A01M08_POC_XBND_OCPU_QPY_BETA0813.zip
```

### 2.2 简要流程图

![image-20240814140616290](https://typora-breeze.oss-cn-wuhan-lr.aliyuncs.com/img-md/image-20240814140616290.png) 



### 2.3 简述初始化流程

LCD 和 lvgl 的初始化在`ui.py`中进行，属于全局变量。

其他初始化流程如下：

`App`是一个`poc_main.py`的一个类，对其设置按键、UI、屏幕栏、消息框以及服务之后启动即可。

`App`充当一个程序启动的管理器，包含程序的基础组成部分。

`App`的`UI`负责所有屏幕管理，以及部分事件消息的中转等

`App`的服务负责提供基础服务，如网络服务，媒体服务、以及最重要的`Poc`服务等

![image-20240814141030603](https://typora-breeze.oss-cn-wuhan-lr.aliyuncs.com/img-md/image-20240814141030603.png) 

### 2.4 界面

1. `WelcomeScreen`：检测`sim`卡状态、绑定平台
2. `MenuBar`：每个界面（`WelcomeScreen`除外）的菜单栏显示，包括信号、时间、电量
3. `MainScreen`：主界面功能展示，包括多个列表
4. `DevScreen`：设备信息，包括`ICCID`、`IMEI`、固件版本
5. `GroupScreen`：所在群组显示界面
6. `MemberScreen`：所添加的成员列表显示界面

### 2.5 服务

1. `DevInfoService`：提供设备信息服务
2. `MediaService`：提供音频服务
3. `NetService`：提供网络服务
4. `PocService`：提供`Poc`对讲服务

## 3. 演示操作

### 3.1 程序启动

在`QPYcom`运行`poc_main.py`脚本，程序开始运行，进入到`WelcomeScreen`界面，同时获取`sim`卡状态和当前账号，并通过`tts`语音播报当前登录用户及其加入的群组信息。

![image-20240814094634924](https://typora-breeze.oss-cn-wuhan-lr.aliyuncs.com/img-md/image-20240814094634924.png) 

**注意**：未插入`sim`卡时不会进入到`MainScreen`，插入`sim`卡重启设备后即可正常运行

![image-20240814114345769](https://typora-breeze.oss-cn-wuhan-lr.aliyuncs.com/img-md/image-20240814114345769.png) 

### 3.2  主界面

主界面包含多个选项列表（用户可自行添加、修改），每个选项对应一个新的界面，双击`key2`键，可以进入到所选中的界面当中，长按`key2`键则返回上一级界面

![image-20240814094658732](https://typora-breeze.oss-cn-wuhan-lr.aliyuncs.com/img-md/image-20240814094658732.png) 


### 3.3 对讲

1. 长按`key1`键，可以与同一群组内的成员进行对讲，菜单栏显示麦克风图标
2. 说话结束后，松开`key1`键，结束对讲功能
3. 在主动呼叫或被对方呼叫时，都会有消息弹窗提示
4. 对方讲话时，菜单栏显示听筒图标

![ec951d1df2f268a698b0e3d3119b16e](https://typora-breeze.oss-cn-wuhan-lr.aliyuncs.com/img-md/ec951d1df2f268a698b0e3d3119b16e.jpg)

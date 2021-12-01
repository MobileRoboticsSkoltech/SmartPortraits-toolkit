# Converter to TUM and EuRoC formats

## Usage

To convert data to EuRoC format you need to call **convertData.sh** script and set parameter with either the path to the dataset directory ("dataset" in our case) with **-a** (all) flag or the path to a particlar person (197, for example) omitting the flag. After calling the script output data will be present inside **smartphone_video_frames** directroty of every sequence.


```
dataset
└── 000
│    └── date1
│    │     └── _azure_depth_camera_info
│    │     └── _azure_depth_image_raw
│    │     └── _mcu_imu
│    │     └── _sequences_ts
│    │     └── smartphone_video_frames
│    │     └── CameraTrajectory.txt
│       ...
│    └── date5
│    │     └── ...
 ...
│    │
└── 100
│    └── date1
│    ...
│    └── date5
```

## Examples

```./convertData.sh -a /home/user/dataset``` - converts the whole dataset
```./convertData.sh /home/user/dataset/150``` - converts only the person contained in the directory 150

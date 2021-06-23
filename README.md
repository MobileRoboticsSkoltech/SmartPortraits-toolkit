# Toolkit for Avatar dataset

This repository provides a toolkit for Avatar dataset — dataset of human torso videos recorded on smartphone with estimated camera trajectory. Also, depth data from the depth sensor is recorded along with every video with sub-millisecond synchronization between frames.

Main hardware used:

* Samsung S10e
* Azure Kinect DK

## Dataset description

### Location

Dataset is located [HERE: add link]()

### Structure and format

The data is organized as following. Folder numbers in root directory (`000`, ..., `100`) present order number of recorded person. Every person folder contains 5 pose records named by date with 5 different static poses: 3 in staying position, 2 in sitting position. Every pose record contains data collected from smartphone, depth sensor and IMU in the following format.

```
Avatar Dataset
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

*_azure_depth_image_raw* — contains `.npy` file with depth data 640x480.

*smartphone_video_frames* — contains data recorded on smartphone: video, IMU data, timestamps of flash blinking.

*CameraTrajectory.txt* — camera trajectory in quaternion format.

### Intrinsics and extrinsics

Calibration parameters of the setup are kept in the dictionary format in `setup_parameters.json` and could be accessed in the next way:

```python
import json
param = read('setup_parameters.json')

# RGB data from smartphone (intrinsics)
param['rgb']['dist_mtx'] -- 3x3 matrix
param['rgb']['dist_coef'] -- 8x1 array
param['rgb']['undist_mtx'] -- 3x3 matrix

# Depth data from Azure Kinect (intrinsics)
param['depth']['dist_mtx'] -- 3x3 matrix
param['depth']['dist_coef'] -- 8x1 array
param['depth']['undist_mtx'] -- 3x3 matrix

# Extrinsic transformation between RGB camera and depth camera
param['T'] -- 4x4 transformation matrix
```

## Dataset download and extraction

### Download

TODO -- zhores CLI API for effective data downloading

### Dataset extraction on local machine

Performs final extraction of the dataset sequence, splits video to frames with aligned timestamps.

#### System requirements

    - Python
    - FFmpeg

Run ```./local_extract.sh <PATH_TO_SEQUENCE_DIRECTORY> <optional> --split```. Use ```--split``` option to split the sequence to subsequences.


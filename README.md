# Toolkit for Avatar dataset

This repository provides a toolkit for Avatar dataset — dataset of human torso videos recorded on smartphone with estimated camera trajectory. Also, depth data from the depth sensor is recorded along with every video with sub-millisecond synchronization between frames.

Main hardware used:

* Samsung S10e
* Azure Kinect DK

## Dataset description

### Location

Dataset is located [HERE: add link]()

### Structure and format

The dataset contains 200 people recorded in different poses and different locations.
Folder numbers in the root directory (000, ..., 200) present the order number of the recorded person. Every person folder contains 5 records named by date with 5 different static poses: 3 in staying position, 2 in sitting position. Every record contains synchronized data from the smartphone (Samsung S10e), depth sensor (Azure Kinect DK), and external IMU sensor. The recordings were performed with periodical flash blinking (1 Hz).

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

*_azure_depth_camera_info* -- intrinsic parameters of a depth camera in ROS format

*_azure_depth_image_raw* -- 1-channel float array 640x576 (distance is presented in meters), name represents a moment of capturing (nanoseconds)

*_mcu_imu* -- data from external IMU (3-axis gyroscope, 3-axis accelerometer), every line contains 7 values <timestamp (nanoseconds), gyro-x, gyro-y, gyro-z, accel-x, accel-y, accel-z>

*smartphone_video_frames* -- video recorded on the smartphone (<date>.mp4), exact timestamps of frames in the video (<date>_aligned_timestamps.csv, nanoseconds), timestamps of moments with flash turned on (<date>_aligned_flash.csv, nanoseconds), data from built-in smartphone gyroscope (<date>_aligned_gyro.csv, <gyro-x, gyro-y, gyro-z, nanoseconds>).

*CameraTrajectory.txt* -- trajectory obtained from ORB SLAM, every line contains a timestamp (seconds) and pose quaternion.

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

### Sequence conversion to TUM format with masks
Perfoms conversion of a video to tom format with masks and corrected masks.
#### System requirements

    - Python
    - FFmpeg
    - [U-2-Net](https://github.com/xuebinqin/U-2-Net)

Run ```python3 make_TUM.py <PATH_TO_SEQUENCE_DIRECTORY> <PATH_TO_U-2-Net>```. 
# avatar-dataset-toolkit

# TODO list
* [ ]  `local_extract` script with minimal settings for external user
* [ ] poincloudify example -- how to get point cloud from depth image
* [ ] conversion to TUM format
* [ ] depth projection on rgb visualization
* [ ] explanation on dataset format and extrinsics/intrinsics

## Local dataset extraction

Performs final extraction of the dataset sequence, splits video to frames with aligned timestamps.

### System requirements

    - Python
    - FFmpeg

Run ```./local_extract.sh <PATH_TO_SEQUENCE_DIRECTORY> <optional> --split```. Use ```--split``` option to split the sequence to subsequences.

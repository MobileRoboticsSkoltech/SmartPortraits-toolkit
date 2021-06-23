# Toolkit for Avatar dataset

# TODO list
* [ ] poincloudify example -- how to get point cloud from depth image
* [ ] conversion to TUM format
* [ ] depth projection on rgb visualization
* [ ] explanation on dataset format and extrinsics/intrinsics

## Data download

* [ ] TODO -- zhores CLI API for effective data downloading

## Dataset extraction on local machine

Performs final extraction of the dataset sequence, splits video to frames with aligned timestamps.

### System requirements

    - Python
    - FFmpeg

Run ```./local_extract.sh <PATH_TO_SEQUENCE_DIRECTORY> <optional> --split```. Use ```--split``` option to split the sequence to subsequences.

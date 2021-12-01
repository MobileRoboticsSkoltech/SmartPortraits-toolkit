import numpy as np
import pandas as pd
import cv2
import argparse

import rosbag
import rospy
from sensor_msgs.msg import Imu
from cv_bridge import CvBridge, CvBridgeError

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_path', help='Directory with ASL data')
    parser.add_argument('--output_path', help='Directory to put the bag into')

    args = parser.parse_args()

    dataPath = args.input_path.rstrip("/")
    bagPath = args.output_path

    print(dataPath)

    # ---------- #

    bag = rosbag.Bag(bagPath, 'w')

    try:
        dataIMU = pd.read_csv(dataPath + "/imu0/data.csv", sep=",")

        for indexIMU, rowIMU in dataIMU.iterrows():
            imu = Imu()
            imu.header.stamp = rospy.Time.from_sec(float(rowIMU[0])/1.0e+9)
            imu.header.frame_id = "imu"
            imu.header.seq = indexIMU

            imu.angular_velocity.x = rowIMU[1]
            imu.angular_velocity.y = rowIMU[2]
            imu.angular_velocity.z = rowIMU[3]

            imu.linear_acceleration.x = 0 if np.isnan(rowIMU[4]) else rowIMU[4]
            imu.linear_acceleration.y = 0 if np.isnan(rowIMU[5]) else rowIMU[5]
            imu.linear_acceleration.z = 0 if np.isnan(rowIMU[6]) else rowIMU[6]

            imu.orientation.w = 1

            bag.write('/imu0', imu)

        dataImage = pd.read_csv(dataPath + "/cam0/data.csv", sep=",")

        for indexImage, rowImage in dataImage.iterrows():
            Image = cv2.imread(dataPath + "/cam0/data/" + rowImage[1], cv2.IMREAD_UNCHANGED)
            msg = CvBridge().cv2_to_imgmsg(Image, "bgr8")

            msg.header.stamp = rospy.Time.from_sec(float(rowImage[0]) / 1.0e+9)
            msg.header.frame_id = "cam0"
            msg.header.seq = indexImage

            bag.write('/cam0/image_raw', msg)

    finally:
        bag.close()

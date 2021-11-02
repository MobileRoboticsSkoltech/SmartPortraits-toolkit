import pandas as pd
from collections import deque
import sys


def addExtension(tVal):
    return str(tVal) + ".png"


if __name__ == '__main__':
    dataDir = sys.argv[1]
    timestampPath = sys.argv[2]
    gyroPath = sys.argv[3]

    # ----------#

    timestampLabels = ["#timestamp [ns]", "filename"]
    timestamps = pd.read_csv(timestampPath, header=None, dtype=str)
    outputFilename = dataDir + "/timestamps.csv"

    data = {
        timestampLabels[0]: timestamps[0], timestampLabels[1]: timestamps[0] + ".png"
    }

    dataframe = pd.DataFrame(data=data)
    dataframe.to_csv(outputFilename, sep=',', encoding='utf-8', index=False, line_terminator='\r\n')

    # ----------#

    imuLabels = [
        "#timestamp [ns]",
        "w_RS_S_x [rad s^-1]",
        "w_RS_S_y [rad s^-1]",
        "w_RS_S_z [rad s^-1]",
        "a_RS_S_x [m s^-2]",
        "a_RS_S_y [m s^-2]",
        "a_RS_S_z [m s^-2]"
    ]

    gyro = pd.read_csv(gyroPath, header=None)
    outputFilename = dataDir + "/gyro_accel.csv"

    if len(sys.argv) == 5:
        accelPath = sys.argv[4]
        accel = pd.read_csv(accelPath, header=None)

        data = pd.merge_asof(gyro, accel, on=3, direction='nearest')
        data = data.reindex(columns=[3, '0_x', '1_x', '2_x', '0_y', '1_y', '2_y'])
        data.columns = [imuLabels[0], imuLabels[1], imuLabels[2], imuLabels[3], imuLabels[4], imuLabels[5], imuLabels[6]]
    else:
        data = {
            imuLabels[0]: gyro[3],
            imuLabels[1]: gyro[0],
            imuLabels[2]: gyro[1],
            imuLabels[3]: gyro[2],
            imuLabels[4]: "",
            imuLabels[5]: "",
            imuLabels[6]: ""
        }

    dataframe = pd.DataFrame(data=data)
    dataframe.to_csv(outputFilename, sep=',', encoding='utf-8', index=False, line_terminator='\r\n')



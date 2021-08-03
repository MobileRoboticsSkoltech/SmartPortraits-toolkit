# Copyright 2020 Mobile Robotics Lab. at Skoltech
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
from shutil import copyfile
from decimal import Decimal
from src.sm_utils import ALLOWED_EXTENSIONS

FILE_TYPE = 'file'
CSV_TYPE_T_FIRST = 'csv_t_first'
CSV_TYPE_T_LAST = 'csv_t_last'
time_to_ns = 1


def make_dir_if_needed(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def main():
    parser = argparse.ArgumentParser(
        description="Split extracted data"
    )
    parser.add_argument(
        "--target_dir",
        required=True
    )
    parser.add_argument(
        "--data_dir",
        required=True
    )
    parser.add_argument(
        '--type',
        choices=[FILE_TYPE, CSV_TYPE_T_FIRST, CSV_TYPE_T_LAST],
        help='<Required> Message type for extraction',
        required=True
    )
    parser.add_argument('--timestamps', nargs='+',
                        help='<Optional> List of sequence timestamps')
    parser.add_argument('--csv', required=False,
                        help='<Optional> CSV for splitting')
    parser.add_argument('--time_unit', required=False,
                        type=int,
                        help='<Optional> If timestamp is not in nanoseconds,\
                            specifies amount to multiply by')
    parser.add_argument('--space', required=False,
                        type=int,
                        help='<Optional> Space separator')
    args = parser.parse_args()

    # TODO: switch to class in this file to get rid of this
    global time_to_ns
    if args.time_unit is not None:
        time_to_ns = args.time_unit
    sep = ','
    if args.space is not None:
        sep = ' '

    if args.type == FILE_TYPE:
        split(args.target_dir, args.data_dir, list(
            map(lambda x: int(x), args.timestamps)))
    elif args.type == CSV_TYPE_T_LAST:
        split_csv_t_last(args.target_dir, args.data_dir, args.csv, list(
            map(lambda x: int(x), args.timestamps)), sep=sep)
    elif args.type == CSV_TYPE_T_FIRST:
        split_csv_t_first(args.target_dir, args.data_dir, args.csv, list(
            map(lambda x: int(x), args.timestamps)), sep=sep)


def split(target_dir, data_dir, timestamps):
    print("Splitting sequences...")

    filename_timestamps = list(map(
        lambda x: (x, int(os.path.splitext(x)[0])),
        filter(
            lambda x: os.path.splitext(x)[1] in ALLOWED_EXTENSIONS,
            os.listdir(target_dir)
        )
    ))
    filename_timestamps.sort(key=lambda tup: tup[1])
    sequences = []
    prev = 0
    for timestamp in timestamps:
        sequences.append(
            list(filter(lambda x: x[1] < timestamp and x[1] >= prev,
                        filename_timestamps)))
        prev = timestamp
    sequences.append(
        list(filter(lambda x: x[1] >= timestamp, filename_timestamps)))
    for i, seq in enumerate(sequences):
        print("Copying sequence %d..." % i)
        new_dir = os.path.join(data_dir, "seq_%d" %
                               i, os.path.split(target_dir)[-1])
        make_dir_if_needed(new_dir)
        for filename, _ in seq:
            copyfile(os.path.join(target_dir, filename),
                     os.path.join(new_dir, filename))


def split_csv_t_first(target_dir, data_dir, csv_filename, timestamps, sep=','):
    with open(os.path.join(target_dir, csv_filename), 'r') as csv_file:
        lines = csv_file.readlines()
        print(csv_filename)
        if (len(lines[0].split(sep, 1)) > 1):
            csv_data = list(
                map(lambda line:
                    (sep + line.split(sep, 1)[1],
                        Decimal(line.split(sep, 1)[0])*time_to_ns),
                    lines))
        else:
            csv_data = list(
                map(lambda line:
                    ('', Decimal(line.split(sep, 1)[0])*time_to_ns),
                    lines))
        sequences = []
        prev = 0

        for timestamp in timestamps:
            sequences.append(
                list(filter(lambda x: x[1] < timestamp and x[1] >= prev,
                            csv_data)))
            prev = timestamp
        sequences.append(
            list(filter(lambda x: x[1] >= timestamp, csv_data)))
        for i, seq in enumerate(sequences):
            print("Copying sequence %d..." % i)
            if target_dir != data_dir:
                new_dir = os.path.join(data_dir, "seq_%d" %
                                       i, os.path.split(target_dir)[-1])
            else:
                new_dir = os.path.join(data_dir, "seq_%d" % i)
            make_dir_if_needed(new_dir)
            # create file with subsequence
            ind = 0
            with open(
                os.path.join(new_dir, csv_filename), 'w+'
            ) as subsec_file:
                for data in seq:
                    subsec_file.write('%d%s' % (data[1], data[0]))
                    ind += 1


def split_csv_t_last(target_dir, data_dir, csv_filename, timestamps, sep=','):
    with open(os.path.join(target_dir, csv_filename), 'r') as csv_file:
        lines = csv_file.readlines()
        print(csv_filename)
        if (len(lines[0].rsplit(sep, 1)) > 1):
            csv_data = list(
                map(lambda line:
                    (line.rsplit(sep, 1)[0] + sep,
                        Decimal(line.rsplit(sep, 1)[1])*time_to_ns),
                    lines))
        else:
            csv_data = list(
                map(lambda line:
                    ('', Decimal(line.rsplit(sep, 1)[0])*time_to_ns),
                    lines))
        sequences = []
        prev = 0

        for timestamp in timestamps:
            sequences.append(
                list(filter(lambda x: x[1] < timestamp and x[1] >= prev,
                            csv_data)))
            prev = timestamp
        sequences.append(
            list(filter(lambda x: x[1] >= timestamp, csv_data)))
        for i, seq in enumerate(sequences):
            print("Copying sequence %d..." % i)            
            if target_dir != data_dir:
                new_dir = os.path.join(data_dir, "seq_%d" %
                                       i, os.path.split(target_dir)[-1])
            else:
                new_dir = os.path.join(data_dir, "seq_%d" % i)
            make_dir_if_needed(new_dir)
            # create file with subsequence
            ind = 0
            with open(
                os.path.join(new_dir, csv_filename), 'w+'
            ) as subsec_file:
                for data in seq:
                    subsec_file.write('%s%d\n' % (data[0], data[1]))
                    ind += 1


if __name__ == '__main__':
    main()

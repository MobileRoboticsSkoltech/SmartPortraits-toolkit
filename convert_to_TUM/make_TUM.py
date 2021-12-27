import os
import subprocess
from shutil import rmtree
import argparse

from cut_masks import cut_all_masks


def clean_dir(dir_path):
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)

        if not os.path.isdir(file_path):
            os.remove(file_path)

        else:
            rmtree(file_path)


if __name__ == "__main__":
    curr_dir = os.path.dirname(__file__)
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=str, help="Path to secuence folder")
    parser.add_argument("u2net", type=str, help="Path to U-2-Net folder")
    args = parser.parse_args()
    target, path_to_u2net = args.target, args.u2net
    final_folder = os.path.normpath(target) + '_TUM'
    mask_folder = os.path.join(final_folder, 'mask')
    mask_res = os.path.join(final_folder, 'mask_res')

    if not os.path.exists(final_folder):
        os.mkdir(final_folder)
    else:
        clean_dir(final_folder)

    subprocess.run(
        [os.path.join(".", "local_extract", "local_extract.sh"), target])
    subprocess.run(["python3", os.path.join(
        curr_dir, "convert_to_tum.py"), target, final_folder])

    if not os.path.exists(mask_folder):
        os.mkdir(mask_folder)
    else:
        clean_dir(mask_folder)

    subprocess.run(["python3", os.path.join(path_to_u2net, "u2net_human_seg_test.py"),
                   path_to_u2net, os.path.join(final_folder, "rgb/"), os.path.join(final_folder, "mask/")])

    if not os.path.exists(mask_res):
        os.mkdir(mask_res)
    else:
        clean_dir(mask_res)
    cut_all_masks(final_folder, os.path.join(target, "_azure_depth_image_raw"))

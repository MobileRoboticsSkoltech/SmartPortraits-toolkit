import sys
import os
import subprocess
from shutil import rmtree

def clean_dir(dir_path):
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        
        if not os.path.isdir(file_path):
            os.remove(file_path)
            
        else:
            rmtree(file_path)
            

if __name__ == "__main__":
    curr_dir = os.path.dirname(__file__)
    target = sys.argv[1]
    path_to_u2net = sys.argv[2]
    final_folder = target +'_TUM'
    mask_folder = os.path.join(final_folder, 'mask')
    mask_res = os.path.join(final_folder, 'mask_res')
    
    if not os.path.exists(final_folder):
        os.mkdir(final_folder)
    else:
        clean_dir(final_folder)

    subprocess.run(['./local_extract/local_extract.sh', target])
    subprocess.run(["python3", os.path.join(curr_dir, "convert_to_tum.py"), target, final_folder])

    if not os.path.exists(mask_folder):
        os.mkdir(mask_folder)
    else:
        clean_dir(mask_folder)

    subprocess.run(["python3", path_to_u2net + "u2net_human_seg_test.py", path_to_u2net, final_folder + "/rgb/", final_folder + "/mask/"])

    if not os.path.exists(mask_res):
        os.mkdir(mask_res)
    else:
        clean_dir(mask_res)

    subprocess.run(["python3", os.path.join(curr_dir, "cut_masks.py"), final_folder, os.path.join(target, "_azure_depth_image_raw")])

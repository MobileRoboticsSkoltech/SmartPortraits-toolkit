import numpy as np
import cv2
from sklearn.cluster import DBSCAN
import open3d as o3d
import pickle
import imageio
import sys
import os
import tqdm
import json
from convert_to_tum import pointcloudify_depth, project_pcd_to_depth, smooth_depth


def convert_from_depth(depth_arr, rgb_cnf, shp, config_file):
    curr_dir = os.path.dirname(__file__)

    with open(os.path.join(curr_dir, config_file["depth_conf"]), 'rb') as config:
        config_dict = pickle.load(config)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pointcloudify_depth(depth_arr, config_dict['depth']['dist_mtx'],
                                                                config_dict['depth']['dist_coef']))
    T = np.load(os.path.join(curr_dir, config_file["transform_intristics"]))
    pcd.transform(T)
    aligned_depth = project_pcd_to_depth(
        pcd, rgb_cnf['undist_intrinsics'], shp, config_file)
    return aligned_depth


def convert_pcd(depth, rgb_cnf):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pointcloudify_depth(
        depth, rgb_cnf['undist_intrinsics'], [], undistort=False))  # H * W X 3
    return pcd


def filter_pcd(pcd):
    cld = np.asarray(pcd.points)
    return [(p) for num, p in enumerate(cld) if p[0] > 0 or p[1] > 0 or p[2] > 0]


def count_labels(filtered, labels):
    uniq = {}
    depth_p = {}
    for pos, a in enumerate(labels):
        if not (a in uniq):
            uniq[a] = 0
            depth_p[a] = filtered[pos][2]
        else:
            uniq[a] += 1
    return (uniq, depth_p)


def filter_small_clusters(uniq, depth_p):
    filtered_depth_p = {}

    for key, dist in depth_p.items():
        if abs(dist) > 0.0001 and uniq[key] > 1000:
            filtered_depth_p[key] = dist
    return filtered_depth_p


def choose_mask_points(labels, filtered, mink):
    ready = []
    for n, x in enumerate(labels):
        if x == mink:
            ready.append(filtered[n])
    return ready


def back_to_png(ready, rgb_cnf, shp, config):
    r = o3d.geometry.PointCloud()
    r.points = o3d.utility.Vector3dVector(ready)
    aligned_depth = project_pcd_to_depth(
        r, rgb_cnf['undist_intrinsics'], shp, config)
    return aligned_depth


def cut_all_masks(path_rgb, path_raw_depth):
    curr_dir = os.path.dirname(__file__)
    with open(os.path.join(curr_dir, 'config.json')) as conf_f:
        config = json.load(conf_f)
    with open(os.path.join(path_rgb, "association.txt")) as asoc:
        lines = asoc.readlines()
        for line in tqdm.tqdm(lines):
            rgb_cnf = np.load(os.path.join(
                curr_dir, config["rgb_intristics"]), allow_pickle=True).item()
            s = line.strip().split(" ")
            rgb_name = s[0] + ".png"
            depth_name = s[2] + ".npy"
            mask = imageio.imread(os.path.join(path_rgb, "mask", rgb_name))
            depth_array = np.load(os.path.join(
                path_raw_depth, depth_name), allow_pickle=True)
            gray_mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
            depth_sparce = convert_from_depth(
                depth_array, rgb_cnf, mask.shape[:2], config)
            filtered = np.asarray(convert_pcd(
                depth_sparce * (gray_mask > 0), rgb_cnf).points)

            filtered = filtered[~np.all(filtered == 0, axis=1)]

            clustering = DBSCAN(eps=0.5, n_jobs=-1)
            labels = clustering.fit_predict(filtered)

            uniq, depth_p = count_labels(filtered, labels)

            filtered_depth_p = filter_small_clusters(uniq, depth_p)

            mink = min(filtered_depth_p, key=depth_p.get)

            ready = choose_mask_points(labels, filtered, mink)

            aligned_depth = back_to_png(ready, rgb_cnf, mask.shape[:2], config)
            aligned_depth = smooth_depth(aligned_depth)

            aligned_depth = (aligned_depth > 0) * 255

            imageio.imwrite(os.path.join(path_rgb, "mask_res",
                            rgb_name), (aligned_depth).astype(np.uint16))


if __name__ == "__main__":
    path_rgb = sys.argv[1]
    path_raw_depth = sys.argv[2]
    cut_all_masks(path_rgb, path_raw_depth)

import copy
import cv2 as cv
import imageio

import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'


from multiprocessing import Pool
import numpy as np
import os
import open3d as o3d
import pickle
import scipy
from scipy.signal import convolve2d
import shutil
import sys
from tqdm import tqdm


DEPTH_SCALE_FACTOR = 5000
SETUP_CONFIG = 'bandeja_standard.pickle'


# Point cloud from depth (by Konstantin)
def pointcloudify_depth(depth, intrinsics, dist_coeff, undistort=True):
    shape = depth.shape[::-1]
    
    if undistort:
        undist_intrinsics, _ = cv.getOptimalNewCameraMatrix(intrinsics, dist_coeff, shape, 1, shape)
        inv_undist_intrinsics = np.linalg.inv(undist_intrinsics)

    else:
        inv_undist_intrinsics = np.linalg.inv(intrinsics)

    if undistort:
        # undist_depthi = cv.undistort(depthi, intrinsics, dist_coeff, None, undist_intrinsics)
        map_x, map_y = cv.initUndistortRectifyMap(intrinsics, dist_coeff, None
                                                  , undist_intrinsics, shape, cv.CV_32FC1)
        undist_depth = cv.remap(depth, map_x, map_y, cv.INTER_NEAREST)

    # Generate x,y grid for H x W image
    grid_x, grid_y = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]))
    grid = np.concatenate([np.expand_dims(grid_x, -1),
                           np.expand_dims(grid_y, -1)], axis=-1)

    grid = np.concatenate([grid, np.ones((shape[1], shape[0], 1))], axis=-1)

    # To normalized image coordinates
    local_grid = inv_undist_intrinsics @ grid.reshape(-1, 3).transpose()  # 3 x H * W

    # Raise by undistorted depth value from image plane to local camera space
    if undistort:
        local_grid = local_grid.transpose() * np.expand_dims(undist_depth.reshape(-1), axis=-1)

    else:
        local_grid = local_grid.transpose() * np.expand_dims(depth.reshape(-1), axis=-1)
        
    return local_grid.astype(np.float32)


def project_pcd_to_depth(pcd, undist_intrinsics, img_size): 
    I = np.zeros(img_size, np.float32)
    h, w = img_size
    points = np.asarray(pcd.points)
    d = points[:, 2] #np.linalg.norm(points, axis=1)
    normalized_points = points / np.expand_dims(points[:, 2], axis=1)
    proj_pcd = np.round(undist_intrinsics @ normalized_points.T).astype(np.int64)[:2].T
    proj_mask = (proj_pcd[:, 0] >= 0) & (proj_pcd[:, 0] < w) & (proj_pcd[:, 1] >= 0) & (proj_pcd[:, 1] < h)
    proj_pcd = proj_pcd[proj_mask, :]
    d = d[proj_mask]
    pcd_image = np.zeros((1080, 1920))
    pcd_image[proj_pcd[:, 1], proj_pcd[:, 0]] = d
    return pcd_image


def smooth_depth(depth):
    MAX_DEPTH_VAL = 1e5
    KERNEL_SIZE = 11
    depth[depth == 0] = MAX_DEPTH_VAL
    smoothed_depth = scipy.ndimage.minimum_filter(depth, KERNEL_SIZE)
    smoothed_depth[smoothed_depth == MAX_DEPTH_VAL] = 0
    return smoothed_depth


def align_rgb_depth(rgb, depth, roi, config_file=SETUP_CONFIG):
    curr_dir = os.path.dirname(__file__)
    with open(os.path.join(curr_dir, config_file), 'rb') as config:
        config_dict = pickle.load(config)

    # Undistort rgb image

    rgb_cnf = np.load(os.path.join(curr_dir, 's10_standard_intrinsics(1).npy'), allow_pickle=True).item()
    
    undist_rgb = cv.undistort(rgb, rgb_cnf['intrinsics'], rgb_cnf['dist_coeff'],
                              None, rgb_cnf['undist_intrinsics'])

    # Create point cloud from depth
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pointcloudify_depth(depth, config_dict['depth']['dist_mtx'],
                                                config_dict['depth']['dist_coef']))
    T = np.load(os.path.join(curr_dir, 'azure2s10_standard_extrinsics(1).npy'))

    # Align point cloud with depth reference frame
    pcd.transform(T)
    
    # Project aligned point cloud to rgb
    aligned_depth = project_pcd_to_depth(pcd, rgb_cnf['undist_intrinsics'], rgb.shape[:2])
    
    smoothed_aligned_depth = smooth_depth(aligned_depth)
    x, y, w, h = roi

    depth_res = smoothed_aligned_depth[y:y+h, x:x+w]
    rgb_res = undist_rgb[y:y+h, x:x+w]
    return rgb_res, depth_res


def process_pair(rgbd_pair):
    rgb_image = cv.imread(os.path.join(smartphone_folder, str(rgbd_pair[0]) + '.png'))
    depth_array = np.load(os.path.join(azure_depth_folder, str(rgbd_pair[1]) + '.npy'), allow_pickle=True)

    rgb_image_aligned, depth_array_aligned = align_rgb_depth(rgb_image, depth_array, (0, 0, 1920, 1080))

    # Save rgb as 8-bit png
    cv.imwrite(os.path.join(final_folder, 'rgb', str(rgbd_pair[0]) + '.png'), rgb_image_aligned)

    # Save depth as 16-bit unsigned int with scale factor
    depth_array_aligned = (depth_array_aligned * DEPTH_SCALE_FACTOR).astype(np.uint16)
    imageio.imwrite(os.path.join(final_folder, 'depth', str(rgbd_pair[1]) + '.png'), depth_array_aligned)


if __name__ == "__main__":
    dataset_path = sys.argv[1]
    # dirs = os.listdir(dataset_path)
    # dirs.sort()
    final_folder_path = sys.argv[2]
    # already_processed = os.listdir('final/')
    # for data_dir in dirs:
        # if data_dir in already_processed:
            # continue
#        if data_dir not in ['2021-07-08-14-49-30']:
#            continue
        # Folder where the data in TUM format will be put
    final_folder = final_folder_path + '/'

    azure_depth_folder = dataset_path + '/_azure_depth_image_raw/'
    smartphone_folder = dataset_path  + '/smartphone_video_frames/'

    depth_ts = np.array([int(file.split('.')[0]) for file in os.listdir(azure_depth_folder) 
                        if file.endswith('.npy')])
    depth_ts.sort()

    rgb_ts = np.array([int(file.split('.')[0]) for file in sorted(os.listdir(smartphone_folder)) 
                    if file.endswith('.png')])
    rgb_ts.sort()
    
    print('Depth timestamps from {1} to {2} (cnt {0})'.format(len(depth_ts), depth_ts[0], depth_ts[-1]))
    print('RGB timestamps from {1} to {2} (cnt {0})'.format(len(rgb_ts), rgb_ts[0], rgb_ts[-1]))

    # Build correspondences between depth and rgb by nearest neighbour algorithm
    rgbd_pairs = []
    for depth_t in depth_ts:
        closest_rgb_t = min(rgb_ts, key=lambda x: abs(depth_t - x))
        rgbd_pairs.append((closest_rgb_t, depth_t))
    # Prepare folder infrastructure
    if os.path.exists(final_folder):
        shutil.rmtree(final_folder)
    os.mkdir(final_folder)
    os.mkdir(os.path.join(final_folder, 'depth'))
    os.mkdir(os.path.join(final_folder, 'rgb'))
    


    # Copy pairs of rgb and depth to final dir
    # for pair in tqdm(rgbd_pairs):
    #     process_pair(pair)

    pool = Pool(processes=10)
    # pool._taskqueue._maxsize = 10
    for _ in tqdm(pool.imap_unordered(process_pair, rgbd_pairs), total=len(rgbd_pairs)):
        pass
    
    pool.close()
    pool.join()

    # with Pool(60) as pool: 
    #     pool.map(process_pair, rgbd_pairs)

    # Produce file with associations between rgb and depth files
    with open(os.path.join(final_folder, 'association.txt'), 'w') as association_file:
        for rgbd_pair in rgbd_pairs:
            association_file.write('{0} {1} {2} {3}\n'
                                .format(rgbd_pair[0] , os.path.join('rgb', str(rgbd_pair[0] ) + '.png'),
                                        rgbd_pair[1] , os.path.join('depth', str(rgbd_pair[1] ) + '.png')))

from tif_to_lonlat import *
import pandas as pd
from pyproj import Geod
import cv2
import numpy as np
from server_api.database_mysql import *


def nonzero_pixel_ratio(image_path):
    # 读取图像 (BGR format)
    img = cv2.imread(image_path)

    if img is None:
        raise FileNotFoundError(f"无法加载图像: {image_path}")

    # 判断每个像素是否在所有三个通道上都为 0
    # 即：只有当 R==0 且 G==0 且 B==0 时，才视为“零像素”
    zero_pixels = (img == 0).all(axis=2)  # shape: (H, W)，True 表示是全零像素

    total_pixels = img.shape[0] * img.shape[1]
    nonzero_count = total_pixels - np.count_nonzero(zero_pixels)

    ratio = nonzero_count / total_pixels
    return ratio



data_base_info=dict()
data_base_info["ip"]= "220.168.154.63"
data_base_info["port"]= "3306"
data_base_info["database"]= "pvops_admin"
data_base_info["user"]= "pvops"
data_base_info["passwd"]= "GLKJ@pvops0419"

def data_to_database(data_base_info, data, area_id):

    db = MySQLDatabase(host=data_base_info["ip"],
                  database = data_base_info["database"],
                  user= data_base_info["user"],
                  password=data_base_info["passwd"],
                  port=data_base_info["port"])



    db.update("patrol_area",{"area_proportion":data},'area_id='+str(area_id))

    # keys = ["panel_name", "panel_tl", "panel_tr", "panel_bl", "panel_br", "center_point",
    # "panel_id", "station_id", "model_id", "is_deleted", "create_by", "update_by", "tenant_id",
    # "pcoor_area", "bracket_area", "total"]




def calculate_distance_pyproj(lat1, lon1, lat2, lon2):
    """
    使用 pyproj.Geod 计算两个经纬度点之间的距离

    参数:
    lat1, lon1: 第一个点的纬度和经度（十进制度）
    lat2, lon2: 第二个点的纬度和经度（十进制度）

    返回:
    距离（米）
    """
    # 创建 Geod 实例，默认使用 WGS84 椭球体
    g = Geod(ellps='WGS84')

    # 计算两点间的距离和方位角
    azimuth1, azimuth2, distance = g.inv(lon1, lat1, lon2, lat2)

    return distance

def read_csv(area_csv, hunan_area_297_new, hunan_area_298_new):

    df = pd.read_csv(area_csv)

    tif_path_297 = r"D:\hunan_tif\297\result.tif"
    tif_path_298 = r"D:\hunan_tif\298\result.tif"

    dataset_297, transform_297 = img2gps_init(tif_path_297)
    dataset_298, transform_298 = img2gps_init(tif_path_298)

    for row in df.itertuples():
        min_x = int(row.min_x)
        max_x = int(row.max_x)
        min_y = int(row.min_y)
        max_y = int(row.max_y)
        model_id = int(row.model_id)
        area_id = int(row.area_id)

        if int(model_id) == 297:
            x1_lat, x1_lon = img2gps(min_x, min_y, dataset=dataset_297, transform=transform_297)
            x2_lat, x2_lon = img2gps(max_x, min_y, dataset=dataset_297, transform=transform_297)
            x3_lat, x3_lon = img2gps(max_x, max_y, dataset=dataset_297, transform=transform_297)

            img_path = hunan_area_297_new + str(area_id) + ".jpg"

        else:
            x1_lat, x1_lon = img2gps(min_x, min_y, dataset=dataset_298, transform=transform_298)
            x2_lat, x2_lon = img2gps(max_x, min_y, dataset=dataset_298, transform=transform_298)
            x3_lat, x3_lon = img2gps(max_x, max_y, dataset=dataset_298, transform=transform_298)

            img_path = hunan_area_298_new + str(area_id) + ".jpg"



        w = calculate_distance_pyproj(x1_lon, x1_lat, x2_lon, x2_lat)
        h = calculate_distance_pyproj(x2_lon, x2_lat, x3_lon, x3_lat)

        ratio = nonzero_pixel_ratio(img_path)



        # print("area: ", w*h)
        # print("ratio: ", ratio)

        data_to_database(data_base_info,w*h*ratio, area_id)

        print("valid area: ", w*h*ratio, "/m2")

if __name__ == '__main__':
    read_csv("new_area.csv", r"D:\hunan_area_297_new/", r"D:\hunan_area_298_new/")
import pandas as pd
from tif_to_lonlat import *


def read_csv(csv_path):
    df = pd.read_csv(csv_path)

    tif_path_297 = r"D:\hunan_tif\297\result.tif"
    tif_path_298 = r"D:\hunan_tif\298\result.tif"

    dataset_297, transform_297 = img2gps_init(tif_path_297)
    dataset_298, transform_298 = img2gps_init(tif_path_298)

    # 新增列
    df['img_area'] = None
    df['min_x'] = 0.0
    df['max_x'] = 0.0
    df['min_y'] = 0.0
    df['max_y'] = 0.0

    for index, row in df.iterrows():
        area_id = row['area_id']
        model_id = row['model_id']
        area_range = row['area_range']

        area_data = area_range.split('|')

        img_area = []
        x_total = []
        y_total = []

        for points in area_data:
            lon, lat = points.split(',')
            lon = float(lon)
            lat = float(lat)

            if int(model_id) == 297:
                x, y = gps2img(lat, lon, dataset=dataset_297, transform=transform_297)
            else:
                x, y = gps2img(lat, lon, dataset=dataset_298, transform=transform_298)

            img_area.append((x, y))
            x_total.append(x)
            y_total.append(y)

        min_x = min(x_total)
        max_x = max(x_total)
        min_y = min(y_total)
        max_y = max(y_total)

        # 填充新列
        df.at[index, 'img_area'] = img_area
        df.at[index, 'min_x'] = min_x
        df.at[index, 'max_x'] = max_x
        df.at[index, 'min_y'] = min_y
        df.at[index, 'max_y'] = max_y

    df['img_area'] = df['img_area'].astype(str)
    df.to_csv('new_area.csv', index=False)

    # 返回更新后的 DataFrame
    return df









if __name__ == '__main__':

    read_csv("patrol_area.csv")


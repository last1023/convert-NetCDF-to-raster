import os
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
import numpy as np
from netCDF4 import Dataset
from osgeo import gdal, osr


def convert(file_path, output_file_path):
    global num

    parent_path = os.path.dirname(output_file_path)
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)

    NC_DS = Dataset(file_path, encoding='gbk')
    l = list(NC_DS.variables.items())

    Lat = NC_DS.variables['LAT'][:]
    Lon = NC_DS.variables['LON'][:]

    variable = NC_DS.variables[str(l[-1][0])][:, :]

    SPEI = np.asarray(variable)

    LonMin, LatMax, LonMax, LatMin = [Lon.min(), Lat.max(), Lon.max(), Lat.min()]

    N_Lat = len(Lat)
    N_Lon = len(Lon)
    Lon_Res = (LonMax - LonMin) / (N_Lon - 1)
    Lat_Res = (LatMax - LatMin) / (N_Lat - 1)

    spei_ds = gdal.GetDriverByName('Gtiff').Create(output_file_path, N_Lon, N_Lat, 1,
                                                   gdal.GDT_Float32)

    geotransform = (LonMin, Lon_Res, 0, LatMin, 0, Lat_Res)
    spei_ds.SetGeoTransform(geotransform)


    srs = osr.SpatialReference()  # 获取地理坐标系统信息，用于选取需要的地理坐标系统
    srs.ImportFromEPSG(4326)  # 定义输出的坐标系为"WGS 84"，AUTHORITY["EPSG","4326"]
    spei_ds.SetProjection(srs.ExportToWkt())  # 给新建图层赋予投影信息


    spei_ds.GetRasterBand(1).WriteArray(SPEI)
    spei_ds.FlushCache()  #


def show_files(path, all_files, suffix='.nc'):
    # 首先遍历当前目录所有文件及文件夹
    file_list = os.listdir(path)
    # 准备循环判断每个元素是否是文件夹还是文件，是文件的话，把名称传入list，是文件夹的话，递归
    for file in file_list:
        # 利用os.path.join()方法取得路径全名，并存入cur_path变量，否则每次只能遍历一层目录
        cur_path = os.path.join(path, file)
        # 判断是否是文件夹
        if os.path.isdir(cur_path):
            show_files(cur_path, all_files, suffix)
        elif cur_path.endswith(suffix):
            all_files.append(cur_path)
    return all_files


def main():
    suffix = '.nc'
    root = tk.Tk()
    root.withdraw()  # 主窗口隐藏
    messagebox.showinfo(message='请选择目录', title='转换目标目录及其子目录下所有nc文件')
    target_path = askdirectory()
    contents = show_files(target_path, [], suffix)
    for input_file in contents:
        output_file = input_file.replace(os.path.basename(target_path), 'converted').replace('.nc', '.tif')
        convert(input_file, output_file)
        print(f'输出文件{output_file}')

    if len(contents) == 0:
        messagebox.showwarning(message=f'未找到后缀为{suffix}的文件')
    else:
        messagebox.askokcancel(message=f'{len(contents)}个文件处理成功！')


if __name__ == '__main__':
    main()

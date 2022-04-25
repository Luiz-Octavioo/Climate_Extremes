# -------------------------------------------------------------------------------#
# -----------------------------Climate Extremes----------------------------------#
# Create by: Luiz Octavio                                                        #
# LAB: Grupo de Pesquisa em Interação Biosfera-Atmosfera                         #
# Universidade Federal do Estado de Mato Grosso                                  #
# Mestre e Doutorando no Programa de Pós Graduação em Fisica Ambiental           #
# Cuiabá, Mato Grosso                                                            #
#                                                                               #
#                                                                               #
#                                                                               #
# Version: 0.1                                                                   #
# Contato:luizpgfa@gmail.com | luizoctavio@fisica.ufmt.br                        #
# -------------------------------------------------------------------------------#
import xarray as xr
import pandas as pd
import numpy as np
import pymannkendall as mk
import salem


# Fix encode time
def fix_encoding_time(ds, start, end, freq):
    # Consertando o calendario do arquivo
    #_, reference_date = ds.time.attrs['units'].split('since')
    ds['time'] = pd.date_range(
        start=start, end=end, freq=str(freq))

    return ds

# Print variables of xarray dataset


def print_varnames(ds):
    varnames = list(ds.keys())
    print('Variables of Dataset:')
    for varname in varnames:
        print(varname)
    return ''

# Mask Dataset


def mask_dataset(ds, shapefile_path, col_shapefile=False, query=False):
    # Read shapefile and query data
    shape = salem.read_shapefile(shapefile_path)
    shape.crs = 'EPSG:4326'  # WGS84
    if col_shapefile and query:
        shape = shape.loc[shape[str(col_shapefile)] == str(query)]
        # mask dataset
        roi = ds.salem.subset(shape=shape, margin=2)
        roi = roi.salem.roi(shape=shape)

    else:
        roi = ds.salem.subset(shape=shape, margin=2)
        roi = roi.salem.roi(shape=shape)

    return roi

# Get varname


def getvar(ds):
    ds_var = list(ds)[0]
    return ds_var

# Get lat name


def get_lat_name(ds):
    for lat_name in ['lat', 'latitude']:
        if lat_name in list(ds.coords):
            return lat_name

# Get lon name


def get_lon_name(ds):
    for lon_name in ['lon', 'longitude']:
        if lon_name in list(ds.coords):
            return lon_name


# Get 98th percentile and 2th percentile of data
def get_percentil_98th(ds):
    p98 = ds.quantile(
        0.98, dim=[get_lat_name(ds), get_lon_name(ds)])
    return p98


def get_percentil_2th(ds):
    p2 = ds.quantile(
        0.02, dim=[get_lat_name(ds), get_lon_name(ds)])
    return p2

# get weigthed mean


def get_weighted_mean(ds, varname):
    weights = np.cos(np.deg2rad(ds[get_lat_name(ds)]))
    weights.name = 'weights'
    ds_weighted = ds[f'{varname}'].weighted(weights)
    return ds_weighted

# Get stats of variable xarray


def get_stats(ds, varname):
    mean = ds[f'{varname}'].mean(
        dim=[get_lat_name(ds), get_lon_name(ds)]).to_series()
    # rolling_mean = ds[f'{varname}'].rolling(
    #     time=6, center=True).mean('time').to_series()
    weighted_mean = get_weighted_mean(ds, varname)
    weighted_mean_series = weighted_mean.mean(
        dim=[get_lat_name(ds), get_lon_name(ds)]).to_series()
    std = ds[f'{varname}'].std(
        dim=[get_lat_name(ds), get_lon_name(ds)]).to_series()
    min_s = ds[f'{varname}'].min(
        dim=[get_lat_name(ds), get_lon_name(ds)]).to_series()
    max_s = ds[f'{varname}'].max(
        dim=[get_lat_name(ds), get_lon_name(ds)]).to_series()
    p75 = ds[f'{varname}'].quantile(
        0.75, dim=[get_lat_name(ds), get_lon_name(ds)]).to_series()
    p25 = ds[f'{varname}'].quantile(
        0.25, dim=[get_lat_name(ds), get_lon_name(ds)]).to_series()
    p5 = ds[f'{varname}'].quantile(
        0.05, dim=[get_lat_name(ds), get_lon_name(ds)]).to_series()
    p95 = ds[f'{varname}'].quantile(
        0.95, dim=[get_lat_name(ds), get_lon_name(ds)]).to_series()
    time = pd.date_range(start='1979-01-01', end='2020-01-01', freq='1YS')
    df = pd.DataFrame({'Time': time, f'Mean_{getvar(ds)}': mean.values,
                       'Weighted_mean': weighted_mean_series.values,
                       'Std': std.values,
                       'Min': min_s.values, 'Max': max_s.values,
                       'P75': p75.values, 'P25': p25.values,
                       'P5': p5.values, 'P95': p95.values})
    return df


def mann_kendall_test(data):
    # Mann Kendall test
    res = mk.hamed_rao_modification_test(data)
    trend_line = np.arange(len(data)) * res.slope + res.intercept
    return res, trend_line

# merge datasets


def merge_params(stats, sig_stats, name_stats, name_sig):
    return xr.Dataset({name_stats: stats, name_sig: sig_stats})

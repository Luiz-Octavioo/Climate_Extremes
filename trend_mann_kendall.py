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

import numpy as np
import xarray as xr
import pymannkendall as mk
import warnings
from tqdm import tqdm
from utils import *

# filter Warnings
warnings.filterwarnings('ignore')


# Calculate slope of Theil-Sen test pixel by pixel
def calc_slope(ds):
    # Slope for Theil-Sen
    output_slope = []
    for lat in tqdm(np.arange(len(ds[get_lat_name(ds)].values))):
        for lon in np.arange(len(ds[get_lon_name(ds)].values)):
            try:
                slope = mk.hamed_rao_modification_test(ds[:, lat, lon]).slope
            except:
                slope = np.nan  # if nan values exists
            output_slope.append(slope)

    output_slope = np.copy(output_slope).reshape(ds[get_lat_name(ds)].size, ds[get_lon_name(ds)].size)
    return xr.DataArray(output_slope, dims=('lat', 'lon'), coords={
        'lat': ds[get_lat_name(ds)], 'lon': ds[get_lon_name(ds)]})


# Calculate the significance of trend of Mann-Kendall test pixel by pixel
def calc_sig(ds):
    # Significance of trends
    output_sig = []
    for lat in tqdm(np.arange(len(ds[get_lat_name(ds)].values))):
        for lon in np.arange(len(ds[get_lon_name(ds)].values)):
            try:
                pval = mk.hamed_rao_modification_test(ds[:, lat, lon]).p
            except:
                pval = np.nan  # if nan values exists
            output_sig.append(pval)
    output_sig = np.copy(output_sig).reshape(ds[get_lat_name(ds)].size, ds[get_lon_name(ds)].size)
    return xr.DataArray(output_sig, dims=('lat', 'lon'),
                        coords={'lat': ds[get_lat_name(ds)], 'lon': ds[get_lon_name(ds)]})


# Merge variables trends and significance
def merge_params(stats, sig_stats):
    return xr.Dataset({'Trend': stats, 'Sig': sig_stats})

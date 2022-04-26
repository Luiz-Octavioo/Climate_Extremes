# Import Modules

import xarray as xr
from esmtools.stats import corr
from esmtools.grid import convert_lon
import os
import glob
from utils import *
from tqdm import tqdm
# import matplotlib.pyplot as plt

# Ignore warnings
import warnings

warnings.filterwarnings('ignore')

# Open dataset of sea surface temperature (SST)
ersst = xr.open_dataset('sst.mean.nc')
# Slice of data
ersst = ersst.sel(time=slice('1979-01-01', '2020-12-01'))
# Calculate anomalies
asst = ersst.groupby('time.month') - ersst.groupby('time.month').mean(dim='time')

# Set regions nino of interest NOAA
nino_regions = ['NINO1+2', 'NINO3', 'NINO4', 'NINO34', 'TNAI', 'TSAI']
path = '/home/luiz/Jupyter_Notebook/Python_Notebook/Climate_Extremes_DOC/Correlations_NC/'
precip_path = 'Precip_COR'
temp_path = 'Temp_COR'

# Change dir
os.chdir('/home/luiz/climate_change/ETCCDI_Extremes/Anual/Anual-Temp/')

# Create directory to save correlations
for region in nino_regions:
    if not os.path.exists(f'{path}{region}/{temp_path}'):
        # os.mkdir(f'{path}{region}/{precip_path}/')
        os.mkdir(f'{path}{region}/{temp_path}/')

nino_lat_lon = {'NINO1+2': {'lat': [-10, 0], 'lon': [280, 290]}, 'NINO3': {'lat': [-5, 5], 'lon': [210, 270]},
                'NINO4': {'lat': [-5, 5], 'lon': [160, 210]}, 'NINO34': {'lat': [-5, 5], 'lon': [190, 240]},
                'TNAI': {'lat': [5.5, 23.5], 'lon': [302.5, 345]}, 'TSAI': {'lat': [0, -20], 'lon': [-30, 10]}}

# Empty lists to store data
nino_data = []
for key, nino in nino_lat_lon.items():
    print(key + ': ', nino['lat'][0], nino['lat'][1], nino['lon'][0], nino['lon'][1])
    if key == 'TSAI':
        print('Convert longitude to -180 to 180')
        asst = convert_lon(asst, coord='lon')
        asst_areas = asst.sel(lon=slice(nino['lon'][0], nino['lon'][1]),
                              lat=slice(nino['lat'][0], nino['lat'][1])).mean(
            ("lon", "lat"))
    else:
        asst_areas = asst.sel(lon=slice(nino['lon'][0], nino['lon'][1]),
                              lat=slice(nino['lat'][1], nino['lat'][0])).mean(
            ("lon", "lat"))
    # Calculate to annual mean
    asst_areas_annual = asst_areas.resample({'time': 'YS'}).mean()
    # store data
    nino_data.append(asst_areas_annual)

# Define path of shapefile
shp = '/home/luiz/Documentos/Shapefiles/South_America/South_America.shp'
# Create list with Extremes ETCCDI Index
ETCCDI_index = glob.glob('*nc')
# Sort list by other list
# list_index = ['r10mm', 'r20mm', 'r30mm', 'rx1day', 'rx5day', 'prcptot', 'sdii', 'r95p', 'r99p', 'cwd', 'cdd']
list_index = ['txx', 'tnx', 'txn', 'tnn', 'dtr', 'wsdi', 'csdi', 'tx90p', 'tn90p', 'tx10p', 'tn10p', 'fd']
ETCCDI_index = [x for x in ETCCDI_index if x.split('_')[0] in list_index]
ETCCDI_index.sort(key=lambda x: list_index.index(x.split('_')[0]))

# Loop over regions
start_date = '1979-01-01'
end_date = '2020-01-01'
freq = '1YS'

for nino, name_nino in zip(nino_data, nino_regions):
    for index in tqdm(ETCCDI_index):
        ds = xr.open_dataset(index, decode_timedelta=False)
        ds = fix_encoding_time(ds, start=start_date, end=end_date, freq=freq)
        ds = convert_lon(ds, coord=get_lon_name(ds))
        # clip
        ds = mask_dataset(ds, shapefile_path=shp)

        # Remove 'time_bnds'
        if 'time_bnds' in ds:
            ds = ds.drop_vars('time_bnds')
        else:
            pass

        # Get name of index
        index_name = index.split('_')[0]

        # Log
        print(f'{index_name.upper()} - Calculate Correlation between {name_nino} Region')

        # Calculate correlation
        cor, p = corr(nino.sst, ds[getvar(ds)], dim='time', return_p=True)

        # Merge Params
        da = merge_params(cor, p, name_stats='cor', name_sig='sig')

        # Exportar arquivos
        print(f'Saving File {index_name}_COR_{name_nino}.nc')
        da.to_netcdf(f'{path}{name_nino}/{temp_path}/' + f'{index_name}_COR_{name_nino}.nc')

        print('Done!')
    print(f'Done correlations between {name_nino} Region')
print('All correlations done!')

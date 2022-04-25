# -------------------------------------------------------------------------------#
# -----------------------------Climate Extremes----------------------------------#
# Create by: Luiz Octavio                                                        #
# LAB: Grupo de Pesquisa em Interação Biosfera-Atmosfera                         #
# Universidade Federal do Estado de Mato Grosso                                  #
# Mestre e Doutorando no Programa de Pós Graduação em Fisica Ambiental           #
# Cuiabá, Mato Grosso                                                            #
#                                                                                #
#                                                                                #
#                                                                                #
# Version: 0.1                                                                   #
# Contato:luizpgfa@gmail.com | luizoctavio@fisica.ufmt.br                        #
# -------------------------------------------------------------------------------#


# For manipulate spatial datasets
import xarray as xr
import xclim
import salem
from esmtools.grid import convert_lon

# Computation and get data
import glob
import numpy as np

# filter warnings
import warnings

from utils import get_lat_name, get_lon_name

warnings.filterwarnings('ignore')


# Class for process data
class ProcessData:
    """[Class to process files in NETCDF format for performance of 
    Extreme Climatic Indices derived from the expertise of ETCCDI.]

    Parameters: 
        -----------
        nc: [str] -> directory of present files NETCDF

    """

    def __init__(self, nc, var, multidataset=False):
        self.nc = nc
        self.var = var

        if multidataset:
            # List of files for combine
            list_netcdf = glob.glob(self.nc + '*.nc')
            self.nc = xr.open_mfdataset(list_netcdf, chunks={
                'time': 365, 'lat': 150, 'lon': 150})
            # Get lon name
            lon_name = get_lon_name(self.nc)
            self.nc = (lambda x: convert_lon(x, coord=lon_name)
                       if np.max(x[lon_name]) > 180 else x)(self.nc)

        else:
            # Open one dataset
            self.nc = xr.open_dataset(self.nc)
            # get lon name
            lon_name = get_lon_name(self.nc)
            # Convert lon
            self.nc = (lambda x: convert_lon(x, coord=lon_name) if np.max(
                x[lon_name]) > 180 else x)(self.nc)

    def getvar(self):
        self.var = list(self.nc)[0]
        return self.var

    # Get lat name
    def get_lat_name(self):
        for lat_name in ['lat', 'latitude']:
            if lat_name in list(self.nc.dims):
                return lat_name

    # Get lon name
    def get_lon_name(self):
        for lon_name in ['lon', 'longitude']:
            if lon_name in list(self.nc.dims):
                return lon_name

    # Process Precipitation Data
    def process_prcp(self):
        """[
        1-Rename the variable present in the database to 'precip'
        2-Correction of units to be compatible with the program]

        Returns:
            [type]: [Xarray Dataset processed for run functions extremes precipitation]
        """
        # Process
        # Rename variable
        if self.var != 'precip':
            self.var = self.nc.getvar()
            self.nc = self.nc.rename_vars({self.var: 'precip'})
        # Rename coordinates
        if list(self.nc.dims)[1:3] != ['lon', 'lat']:
            self.nc = self.nc.rename(
                {get_lat_name(self.nc): 'lat', get_lon_name(self.nc): 'lon'})
        else:
            pass
        # Correct units
        self.nc[self.var].attrs['units'] = 'mm/day'

        # Fill Nan Values
        ds = self.nc.bfill(dim='time')

        return ds

    # Process Temperature Data
    def process_temp(self):
        """[
        1-Rename the variable present in the database to 'temp'.
        2-Correction of units to be compatible with the program.

        Returns:
            [type]: [Xarray Dataset processed for run functions extremes temperature]
        """
        # Process
        if self.var != ['tmax', 'tmin']:
            self.var = list(self.nc.keys())
            self.var = self.var[0]
            self.nc = self.nc.rename_vars(
                {self.var[0]: 'tmax', self.var[1]: 'tmin'})
        # Rename coordinates
        if list(self.nc.dims)[1:3] != ['lon', 'lat']:
            self.nc = self.nc.rename(
                {get_lat_name(self.nc): 'lat', get_lon_name(self.nc): 'lon'})

        # Correct units
        self.nc[self.var].attrs['units'] = 'degC'

        # Fill Nan Values
        ds = self.nc.bfill(dim='time')

        return ds

    # Function for mask dataset
    @staticmethod
    def mask_dataset(ds, shapefile_path, col_shapefile, query):
        # Read shapefile and query data
        shape = salem.read_shapefile(shapefile_path)
        shape.crs = 'EPSG:4326'  # WGS84
        shape = shape.loc[shape[str(col_shapefile)] == str(query)]
        # mask dataset
        roi = ds.salem.subset(shape=shape, margin=2)
        roi = roi.salem.roi(shape=shape)

        return roi

    # Functions for Performance Precipitation Indices Extremes

    def perform_cdd(self, ds):
        return xclim.indicators.atmos.maximum_consecutive_dry_days(
            pr=ds[self.var], thresh=1, freq='YS', ds=ds)

    def perform_cwd(self, ds):
        return xclim.indicators.atmos.maximum_consecutive_wet_days(
            pr=ds[self.var], thresh=1, freq='YS', ds=ds)

    def perform_r10(self, ds):
        return xclim.indicators.icclim.R10mm(pr=ds[self.var], freq='YS', ds=ds)

    def perform_r20(self, ds):
        return xclim.indicators.icclim.R20mm(pr=ds[self.var], freq='YS', ds=ds)

    def perform_sdii(self, ds):
        return xclim.indicators.icclim.SDII(pr=ds[self.var], freq='YS', ds=ds)

    def perform_rx1day(self, ds):
        return xclim.indicators.atmos.max_1day_precipitation_amount(
            pr=ds[self.var], freq='YS', ds=ds)

    def perform_rx5day(self, ds):
        return xclim.indices.simple.max_n_day_precipitation_amount(
            pr=ds[self.var], window=5, freq='YS')

    def perform_r95p(self, ds):
        # Percentile calc
        p95 = xclim.core.calendar.percentile_doy(ds[self.var], per=95)
        return xclim.indicators.icclim.R95p(pr=ds[self.var], per=p95, freq='YS')

    def perform_r99p(self, ds):
        # Percentile calc
        p99 = xclim.core.calendar.percentile_doy(ds[self.var], per=99)
        return xclim.indicators.icclim.R99p(pr=ds[self.var], per=p99, freq='YS')

    # Functions for Temperature Indices Extremes
    #
    # def perform_txx(self, ds_max):
    #     return xclim.indicators.cf.txx(data=, freq='YS')
    #
    # def perform_txn(self, ds_max):
    #     return xclim.indices.tx_min(ds_max, freq='YS')

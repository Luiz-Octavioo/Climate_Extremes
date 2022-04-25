# Import Modules
import xarray as xr
# from cmocean import cm as cm
import matplotlib.pyplot as plt
import numpy as np
# from metpy.plots import ctables

from datetime import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeat
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import cartopy.mpl.ticker as cticker
from cartopy.io.shapereader import Reader, natural_earth
import matplotlib.ticker as mticker


# Function for plot maps cartopy

def create_maps(ax, lon_min=-90, lon_max=-30, lat_min=-60, lat_max=15, freq_lat=16, freq_lon=16,
                shape=False, shapefile=None, dir_ticks='in'):
    # --Create drawing space
    proj = ccrs.PlateCarree()  # Criar o sistema de coordenadas

    # --Definir as propriedades do mapa

    # Shapefile
    if shape:
        shape = cfeat.ShapelyFeature(
            Reader(shapefile).geometries(),
            proj, edgecolor='k',
            facecolor='none')
        ax.add_feature(shape, linewidth=.5, zorder=10)
    elif not shape:
        ax.add_feature(cfeat.COASTLINE.with_scale(
            '50m'), linewidth=1.6, zorder=10)
        # ax.add_feature(cfeat.STATES.with_scale('50m'),linewidth=0.6, zorder=10)
        ax.add_feature(cfeat.BORDERS)
        # ax.add_feature(cfeat.RIVERS.with_scale('50m'), zorder=10)
        # ax.add_feature(cfeat.LAKES.with_scale('50m'), zorder=10)

    # Axis Labels

    # Definir os xticks para longitude
    ax.set_xticks(np.arange(-180, 181, freq_lon), crs=ccrs.PlateCarree())
    lon_formatter = cticker.LongitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)

    # Definir os yticks para latitude
    ax.set_yticks(np.arange(-90, 91, freq_lat), crs=ccrs.PlateCarree())
    lat_formatter = cticker.LatitudeFormatter()
    ax.yaxis.set_major_formatter(lat_formatter)

    # --Definir a escala para os minorticks
    # ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
    # ax.yaxis.set_minor_locator(plt.MultipleLocator(1))

    ax.tick_params(axis='both', direction=dir_ticks, which='both')

    # ax.set_xticklabels([])
    # ax.set_yticklabels([])

    # - Setting range
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    return ax

# Plot shapefile cartopy


def plot_shapefile(ax, shapefile, color='k', linewidth=1, zorder=10):
    shape = cfeat.ShapelyFeature(
        Reader(shapefile).geometries(),
        ccrs.PlateCarree(), edgecolor=color,
        facecolor='none')
    ax.add_feature(shape, linewidth=linewidth, zorder=zorder)


def hovmoller_plot(ds, label, vmin, vmax, ax, step_v=10, title=None):
    # fig, ax = plt.subplots(figsize=[15, 5])
    var = ds.mean(dim='lon')
    levels = np.arange(vmin, vmax, step_v)

    cs = var.T.plot.contourf(cmap='Spectral_r',
                             levels=levels,
                             extend='both',
                             add_colorbar=False)

    cbar = plt.colorbar(cs, orientation='vertical',
                        shrink=1.0,
                        pad=0.01,
                        aspect=12.,
                        extend='both',
                        drawedges=False,
                        extendrect=False)

    cbar.set_label(label=str(label), size='large', weight='bold')
    cbar.ax.tick_params(labelsize='medium')

    # ax.tick_params(axis='y', which='both', direction='in', right=True)
    # ax.tick_params(axis='x', which='both', direction='in', top=True)

    # Ajustar ticks e labelsw
    plt.ylim(-55, 11)
    plt.xticks(rotation=0, ha='center')
    ax.set_ylabel('Latitude')
    ax.set_xlabel('Time')
    ax.set_title(str(title), fontdict={'fontweight': 'bold', 'fontsize': 12})
    ax.minorticks_on()

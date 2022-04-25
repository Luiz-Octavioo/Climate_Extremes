# Plot pdfs of precip data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from plot_kde import plot_kde
import os

# Create directory for figures
path = '/home/luiz/Jupyter_Notebook/Python_Notebook/Climate_Extremes_DOC/Scripts_Extremes/PDF-Precip-Biome/'
if not os.path.exists(path):
    os.makedirs(path)
else:
    print(f'{path} directory already exists')

# Load datasets
df = pd.read_excel('~/Jupyter_Notebook/Python_Notebook/Climate_Extremes_DOC/mean_precip-Biome-PDF.xlsx')

# Get list of Biomes areas
regions = df['Biome'].unique()
list_periods = df['Period'].unique()
# Reindex index column by list of index_order
list_index = ['r10mm', 'r20mm', 'r30mm', 'rx1day', 'rx5day', 'prcptot', 'sdii', 'r95p', 'r99p', 'cwd', 'cdd']
list_units = ['Days', 'Days', 'Days', 'Precipitation [mm]', 'Precipitation [mm]', 'Precipitation [mm]',
               'Precipitation [mm/day]', 'Precipitation [mm]', 'Precipitation [mm]', 'Days', 'Days']
# create dict for index_order
dict_index = dict(zip(list_index, range(len(list_index))))
# Reindex index column by dict_index
df['Index_Order'] = df['Index'].map(dict_index)
# Sort by index_order
df = df.sort_values(by=['Index_Order', 'Period'])
print(df.head())
# Plot pdfs
nrows = 4
ncols = 3
gridspec_kw = {'hspace': 0.25, 'wspace': 0.25}
colors = ['royalblue', 'darkgreen', 'darkorange', 'firebrick']
ABC = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
for region in regions:
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols,
                            figsize=(12, 12), gridspec_kw=gridspec_kw)
    # Flatten axs
    axs = axs.flatten()
    for index, unit, abc, ax in zip(list_index, list_units, ABC, enumerate(axs)):
        for period, color in zip(list_periods, colors):
            # Plot pdf
            filter_data = df.query('Biome == @region & Index == @index & Period == @period')['Mean']

            # print(filter_data)
            try:
                plot_kde(filter_data, label=f'{period}', color=f'{color}', ax=axs[ax[0]])
            except (np.linalg.LinAlgError, ValueError) as error:
                pass
            # Set parameters to plot
            axs[ax[0]].set_xlabel(f'{unit}')
            axs[ax[0]].set_ylabel('PDF')

            # Set annotations
            axs[ax[0]].annotate(f'{index.capitalize()}', xy=(0.05, 0.90), xycoords='axes fraction', fontsize=12)
            axs[ax[0]].annotate(f'{abc.upper()}', xy=(0.90, 0.90), xycoords='axes fraction', fontsize=12)

            # Set up string formatter of axis y to two decimal places
            axs[ax[0]].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

        # Filter data mean
        filter_data_mean = df.query('Biome == @region & Index == @index')['Mean'].mean()
        # Plot vertical line
        axs[ax[0]].axvline(x=filter_data_mean, color='black', linestyle='--', linewidth=1, label='Mean')
        # Set Minorticks
        axs[ax[0]].minorticks_on()

    # Set suptitle
    # fig.suptitle(f'{region}')

    # Set up legend outside of plot
    axs[10].legend(loc='upper right', frameon=False,
                   bbox_to_anchor=(2.15, .85), fontsize=12)

    # Remove last axis
    fig.delaxes(axs[-1])
    # Save figure
    fig.savefig(f'{path}{region}_precip.png', bbox_inches='tight', dpi=350)
    # plt.show()

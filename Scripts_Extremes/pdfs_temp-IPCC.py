# Plot pdfs of precip data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from plot_kde import plot_kde
import os

# Create directory for figures
path = '/home/luiz/Jupyter_Notebook/Python_Notebook/Climate_Extremes_DOC/Scripts_Extremes/PDF-Temp-IPCC/'
if not os.path.exists(path):
    os.makedirs(path)
else:
    print(f'{path} directory already exists')

# Load datasets
df = pd.read_excel('~/Jupyter_Notebook/Python_Notebook/Climate_Extremes_DOC/mean_temp-IPCC-Regions-PDF.xlsx')
# Rename columns
df.rename(columns={'IPCC-Area': 'IPCC_Area'}, inplace=True)

# Get list of IPCC areas
regions = df['IPCC_Area'].unique()
list_periods = df['Period'].unique()
# Reindex index column by list of index_order
list_index = ['txx', 'tnx', 'txn', 'tnn', 'dtr', 'wsdi', 'csdi', 'tx90p', 'tn90p', 'tx10p', 'tn10p', 'fd']
list_units = ['Temperature [°C]', 'Temperature [°C]', 'Temperature [°C]', 'Temperature [°C]', 'Temperature [°C]',
              'Days',
              'Days', '% Days during year', '% Days during year', '% Days during year', '% Days during year', 'Days']
# create dict for index_order
dict_index = dict(zip(list_index, range(len(list_index))))
# Reindex index column by dict_index
df['Index_Order'] = df['Index'].map(dict_index)
# Sort by index_order
df = df.sort_values(by=['Index_Order', 'Period'])

# Plot pdfs
nrows = 4
ncols = 3
gridspec_kw = {'hspace': 0.25, 'wspace': 0.25}
colors = ['royalblue', 'darkgreen', 'darkorange', 'firebrick']
ABC = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
for region in regions:
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols,
                            figsize=(12, 12), gridspec_kw=gridspec_kw)
    # Flatten axs
    axs = axs.flatten()
    for index, unit, abc, ax in zip(list_index, list_units, ABC, enumerate(axs)):
        for period, color in zip(list_periods, colors):

            # Plot pdf
            filter_data = df.query('IPCC_Area == @region & Index == @index & Period == @period')['Mean']

            # print(filter_data)
            try:
                plot_kde(filter_data, label=f'{period}', color=f'{color}', ax=axs[ax[0]])
            except np.linalg.LinAlgError as e:
                pass

            # Set parameters to plot
            axs[ax[0]].set_xlabel(f'{unit}')
            axs[ax[0]].set_ylabel('PDF')

            # Set annotations
            axs[ax[0]].annotate(f'{index.capitalize()}', xy=(0.03, 0.90), xycoords='axes fraction', fontsize=12)
            axs[ax[0]].annotate(f'{abc.upper()}', xy=(0.90, 0.90), xycoords='axes fraction', fontsize=12)

            # Set up string formatter of axis y to two decimal places
            axs[ax[0]].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

        # Filter data mean
        filter_data_mean = df.query('IPCC_Area == @region & Index == @index')['Mean'].mean()
        # Plot vertical line
        axs[ax[0]].axvline(x=filter_data_mean, color='black', linestyle='--', linewidth=1, label='Mean')
        # Set Minor ticks
        axs[ax[0]].minorticks_on()

    # Set subtitle
    # fig.suptitle(f'{region}')

    # Set up legend outside of plot
    axs[0].legend(loc='center', frameon=False, ncol=5,
                  bbox_to_anchor=(1.5, 1.15), fontsize=12)
    # Save figure
    fig.savefig(f'{path}{region}_Temp.png', bbox_inches='tight', dpi=350)
    # plt.show()

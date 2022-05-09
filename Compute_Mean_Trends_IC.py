import numpy as np
import pandas as pd
import scipy.stats as st

# Load data
df = pd.read_excel('Results/Trend_ETCCDI_Pixel_to_Pixel_Precip-IPCC-Regions.xlsx')

# Rename columns
df.rename(columns={'IPCC-Region': 'IPCC_Region'}, inplace=True)

# Get unique values
IPCC_Regions = df['IPCC_Region'].unique()
ETCCDI_index = df['Index_ETCCDI'].unique()

MEAN_TREND = []
MEAN_TREND_CIMAX = []
MEAN_TREND_CIMIN = []
INDEX_LIST = []
IPCC_REGION_LIST = []
CONFIDENCE_INTERVAL = []
MEAN_IC = []

# Compute confidence interval
for IPCC_Region in IPCC_Regions:
    for Index_ETCCDI in ETCCDI_index:
        # Get data
        filter_data = df.query('IPCC_Region == @IPCC_Region & Index_ETCCDI == @Index_ETCCDI')
        trend = filter_data['Trend']
        # Compute confidence interval
        # create 95% confidence interval for population mean weight
        IC_min, IC_max = st.t.interval(alpha=0.95, df=len(trend) - 1, loc=np.mean(trend), scale=st.sem(trend))
        trend_mean = round(trend.mean(), 3)
        IC_min = round(IC_min, 3)
        IC_max = round(IC_max, 3)
        # Calculate mean +/- confidence interval
        confidence = (trend_mean - IC_min + IC_max - trend_mean) / 2

        # Mean +/- IC
        mean_ic = f'{round(trend_mean, 2)} \u00B1 {confidence:.2f}'

        print(trend_mean, IC_min, IC_max, confidence)

        # Append to list
        MEAN_TREND.append(trend_mean)
        MEAN_TREND_CIMIN.append(IC_min)
        MEAN_TREND_CIMAX.append(IC_max)
        INDEX_LIST.append(Index_ETCCDI)
        IPCC_REGION_LIST.append(IPCC_Region)
        CONFIDENCE_INTERVAL.append(confidence)
        MEAN_IC.append(mean_ic)

# Create dataframe
df_mean_trend = pd.DataFrame({'IPCC_Region': IPCC_REGION_LIST,
                              'Index_ETCCDI': INDEX_LIST,
                              'Mean_Trend': MEAN_TREND,
                              'Mean_Trend_CI_Min': MEAN_TREND_CIMIN,
                              'Mean_Trend_CI_Max': MEAN_TREND_CIMAX,
                              'Confidence_Interval': CONFIDENCE_INTERVAL,
                              'TREND_IC': MEAN_IC})

# Save dataframe
df_mean_trend.to_excel('Results/Mean_IC_Precip-IPCC.xlsx')

print(df_mean_trend)

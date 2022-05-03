# Import modules
import pandas as pd

# Load data
df = pd.read_excel('NINO_indices.xlsx', sheet_name='ONI')
df.set_index('Time', inplace=True)
# round oni column to 2 decimal places
df['ONI'] = df['ONI'].apply(lambda x: round(x, 1))

NINO = 0.5
NINA = -0.5
CONSECUTIVE_MONTHS = 5

# Create mask for NINO and NINA
m_nino = df['ONI'].ge(NINO)
m_nina = df['ONI'].le(NINA)
########################################
s_nino = (~m_nino).cumsum()[m_nino]
s_nina = (~m_nina).cumsum()[m_nina]
# Filter values above or below NINO or NINA threshold for five consecutive months
df['Check_Nino'] = df.ONI[s_nino.map(s_nino.value_counts()).ge(CONSECUTIVE_MONTHS).reindex(df.index, fill_value=False)]
df['Check_Nina'] = df.ONI[s_nina.map(s_nina.value_counts()).ge(CONSECUTIVE_MONTHS).reindex(df.index, fill_value=False)]

# Create a new column with a category of Nino or Nina or Neutral
df['Condition'] = 'Neutral'
df.loc[df['Check_Nino'].notnull(), 'Condition'] = 'El Nino'
df.loc[df['Check_Nina'].notnull(), 'Condition'] = 'La Nina'

# Remove the columns that are not needed
df.drop(['Check_Nino', 'Check_Nina'], axis=1, inplace=True)

# Save the dataframe to a excel file
df.to_excel('Anomalies_SST.xlsx', index=True)
print(df)

import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Load the observed data
observed_data = pd.read_csv('forcings/Haandvaerkervej_Perma_road_All_data_04Jan2023_to_07feb2024.csv', delimiter=',')

# Load the simulated data and handle irregular lines
with open('output/soil_temp.dat', 'r') as file:
    lines = file.readlines()

# Remove comment lines from simulated data
cleaned_lines = [line for line in lines if not line.startswith('#')]

# Read the cleaned lines into a DataFrame
simulated_data_cleaned = pd.read_csv(StringIO(''.join(cleaned_lines)), delimiter=',')

# Specify the depth increment value
depth_increment = 3  # Change this value to set a different increment

# Correct the column names based on the provided instruction
new_column_names_corrected = ['index', 'time'] + [f'Temp_{i*depth_increment}cm_below_surface' for i in range(1, 31)]

# Ensure the correct number of columns in the simulated data
simulated_data_cleaned = simulated_data_cleaned.iloc[:, :32]  # Only take the first 32 columns to match the new names

# Assign the new column names to the simulated data
simulated_data_cleaned.columns = new_column_names_corrected

# Convert simulated temperatures from Kelvin to Celsius
for col in simulated_data_cleaned.columns:
    if 'Temp_' in col:
        simulated_data_cleaned[col] = simulated_data_cleaned[col] - 273.15

# Convert time columns to datetime for proper alignment
observed_data['time'] = pd.to_datetime(observed_data['time'], format='%m/%d/%y %H:%M')
simulated_data_cleaned['time'] = pd.to_datetime(simulated_data_cleaned['time'], format='%m/%d/%y %H:%M')

# Merge datasets on the time column for comparison
merged_data = pd.merge(observed_data, simulated_data_cleaned, on='time', suffixes=('_observed', '_simulated'))

# Specify the time period for visualization
start_date = '2023-01-04 13:50'
end_date = '2023-02-06 16:00'

# Filter the merged data for the specified time period
mask = (merged_data['time'] >= start_date) & (merged_data['time'] <= end_date)
filtered_data = merged_data.loc[mask]

# Specify aggregation level: None, 'hourly', or 'daily'
#aggregation = None 
aggregation = 'hourly'
#aggregation = 'daily'

# Perform aggregation if specified
if aggregation == 'hourly':
    filtered_data.set_index('time', inplace=True)
    filtered_data = filtered_data.resample('H').mean().reset_index()
elif aggregation == 'daily':
    filtered_data.set_index('time', inplace=True)
    filtered_data = filtered_data.resample('D').mean().reset_index()

# Calculate statistical measures: correlation and mean difference
stat_summary = {
    'Depth (cm)': [],
    'Correlation': [],
    'Mean Difference (Observed - Simulated)': []
}

# Depth columns to compare
depth_columns = [6, 30]

for depth in depth_columns:
    observed_col = f'Temp_{depth}cm_below_surface_observed'
    simulated_col = f'Temp_{depth}cm_below_surface_simulated'
    
    correlation = filtered_data[observed_col].corr(filtered_data[simulated_col])
    mean_diff = (filtered_data[observed_col] - filtered_data[simulated_col]).mean()
    
    stat_summary['Depth (cm)'].append(depth)
    stat_summary['Correlation'].append(correlation)
    stat_summary['Mean Difference (Observed - Simulated)'].append(mean_diff)

# Convert summary to DataFrame and display
stat_summary_df = pd.DataFrame(stat_summary)
print(stat_summary_df)

# Plot the data
fig, ax = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# Plot for 6 cm below surface
ax[0].plot(filtered_data['time'], filtered_data['Temp_6cm_below_surface_observed'], label='Observed', color='blue')
ax[0].plot(filtered_data['time'], filtered_data['Temp_6cm_below_surface_simulated'], label='Simulated', color='orange')
ax[0].set_title('Temperature at 6 cm Below Surface')
ax[0].set_ylabel('Temperature (°C)')
ax[0].legend()

# Plot for 30 cm below surface
ax[1].plot(filtered_data['time'], filtered_data['Temp_30cm_below_surface_observed'], label='Observed', color='blue')
ax[1].plot(filtered_data['time'], filtered_data['Temp_30cm_below_surface_simulated'], label='Simulated', color='orange')
ax[1].set_title('Temperature at 30 cm Below Surface')
ax[1].set_xlabel('Time')
ax[1].set_ylabel('Temperature (°C)')
ax[1].legend()

plt.tight_layout()
plt.show()
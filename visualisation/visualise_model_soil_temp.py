import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import os
import numpy as np

# Load the observed data
observed_data = pd.read_csv('forcings/Haandvaerkervej_Perma_road_All_data_04Jan2023_to_07feb2024.csv', delimiter=',')
observed_data['time'] = pd.to_datetime(observed_data['time'], format='%m/%d/%y %H:%M')

# Define a function to load and process a single simulation file
def load_and_process_simulation(file_path, depth_increment):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    cleaned_lines = [line for line in lines if not line.startswith('#')]
    simulated_data = pd.read_csv(StringIO(''.join(cleaned_lines)), delimiter=',')
    
    new_column_names = ['index', 'time'] + [f'Temp_{i*depth_increment}cm_below_surface' for i in range(1, 31)]
    simulated_data = simulated_data.iloc[:, :32]
    simulated_data.columns = new_column_names
    
    for col in simulated_data.columns:
        if 'Temp_' in col:
            simulated_data[col] = simulated_data[col] - 273.15
    
    simulated_data['time'] = pd.to_datetime(simulated_data['time'], format='%m/%d/%y %H:%M')
    
    return simulated_data

# Load multiple simulation files
simulation_files = [f for f in os.listdir('output/tc_factor_exp') if f.endswith('.dat')]
simulations = {}

for file in simulation_files:
    sim_name = os.path.splitext(file)[0]
    simulations[sim_name] = load_and_process_simulation(os.path.join('output/tc_factor_exp', file), depth_increment=3)

# Merge datasets on the time column for comparison
merged_data = observed_data.copy()
for sim_name, sim_data in simulations.items():
    merged_data = pd.merge(merged_data, sim_data, on='time', suffixes=('', f'_{sim_name}'))

# Filter the merged data for the specified time period
start_date = '2023-01-04 13:50'
end_date = '2023-02-06 16:00'
mask = (merged_data['time'] >= start_date) & (merged_data['time'] <= end_date)
filtered_data = merged_data.loc[mask]

# Specify the time period for visualization
start_date = '2023-01-04 13:50'
end_date = '2023-02-06 16:00'

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
    'Simulation': [],
    'Correlation': [],
    'Mean Difference (Observed - Simulated)': []
}

# Depth columns to compare
depth_columns = [6, 30]

for depth in depth_columns:
    observed_col = f'Temp_{depth}cm_below_surface'
    for sim_name in simulations.keys():
        simulated_col = f'Temp_{depth}cm_below_surface_{sim_name}'
        
        correlation = filtered_data[observed_col].corr(filtered_data[simulated_col])
        mean_diff = (filtered_data[observed_col] - filtered_data[simulated_col]).mean()
        
        stat_summary['Depth (cm)'].append(depth)
        stat_summary['Simulation'].append(sim_name)
        stat_summary['Correlation'].append(correlation)
        stat_summary['Mean Difference (Observed - Simulated)'].append(mean_diff)

stat_summary_df = pd.DataFrame(stat_summary)
print(stat_summary_df)

# Plot the data
fig, ax = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

colors = plt.cm.rainbow(np.linspace(0, 1, len(simulations) + 1))

for depth, subplot in zip([6, 30], ax):
    subplot.plot(filtered_data['time'], filtered_data[f'Temp_{depth}cm_below_surface'], label='Observed', color=colors[0])
    
    for i, (sim_name, _) in enumerate(simulations.items(), 1):
        subplot.plot(filtered_data['time'], filtered_data[f'Temp_{depth}cm_below_surface_{sim_name}'], 
                     label=f'Simulated ({sim_name})', color=colors[i])
    
    subplot.set_title(f'Temperature at {depth} cm Below Surface')
    subplot.set_ylabel('Temperature (°C)')
    subplot.legend()

ax[1].set_xlabel('Time')

plt.tight_layout()
plt.show()
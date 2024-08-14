import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import os
import numpy as np

# Load the observed data
observed_data = pd.read_csv('forcings/Haandvaerkervej_Perma_road_04Jan2023_to_07feb2024_updated.csv', delimiter=',')
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
start_date = '2023-11-07 13:50'
end_date = '2024-02-07 11:00'
mask = (merged_data['time'] >= start_date) & (merged_data['time'] <= end_date)
filtered_data = merged_data.loc[mask]

# # Specify the time period for visualization
# start_date = '2023-12-04 13:50'
# end_date = '2024-02-06 16:00'

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

# Calculate statistical measures: correlation, mean difference, and RMSE
stat_summary = {
    'Depth (cm)': [],
    'Simulation': [],
    'Correlation': [],
    'Mean Difference (Observed - Simulated)': [],
    'RMSE': []
}

# Depth columns to compare
depth_columns = [6, 30]

for depth in depth_columns:
    observed_col = f'Temp_{depth}cm_below_surface'
    for sim_name in simulations.keys():
        simulated_col = f'Temp_{depth}cm_below_surface_{sim_name}'
        
        correlation = filtered_data[observed_col].corr(filtered_data[simulated_col])
        mean_diff = (filtered_data[observed_col] - filtered_data[simulated_col]).mean()
        rmse = np.sqrt(((filtered_data[observed_col] - filtered_data[simulated_col]) ** 2).mean())
        
        stat_summary['Depth (cm)'].append(depth)
        stat_summary['Simulation'].append(sim_name)
        stat_summary['Correlation'].append(correlation)
        stat_summary['Mean Difference (Observed - Simulated)'].append(mean_diff)
        stat_summary['RMSE'].append(rmse)

stat_summary_df = pd.DataFrame(stat_summary)
stat_summary_df.to_csv('statistical_summary.csv', index=False)
print(stat_summary_df)

# Plot the data
depths_to_compare = [6, 30]
fig, axes = plt.subplots(2, 1, figsize=(14, 12), sharex=True)

observed_color = 'blue'
observed_style = '--'
sim_colors = plt.cm.Accent(np.linspace(0, 1, len(simulations)))

for depth, ax in zip(depths_to_compare, axes):
    ax.plot(filtered_data['time'], filtered_data[f'Temp_{depth}cm_below_surface'], 
            label='Observed', color=observed_color, linestyle=observed_style, linewidth=2)
    
    for i, (sim_name, _) in enumerate(sorted(simulations.items())):
        ax.plot(filtered_data['time'], filtered_data[f'Temp_{depth}cm_below_surface_{sim_name}'], 
                label=f'Simulated ({sim_name})', color=sim_colors[i], linewidth=1.5, alpha=0.8)
    
    ax.set_title(f'Temperature at {depth} cm Below Surface (aggregation level = {aggregation})', fontsize=14)
    ax.set_ylabel('Temperature (°C)', fontsize=12)
    ax.legend(fontsize=10, loc='lower left')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.tick_params(axis='both', which='major', labelsize=10)

axes[1].set_xlabel('Time', fontsize=12)

plt.tight_layout()
plt.suptitle('Soil Temperature Comparison at Different Depths', fontsize=16, y=1.02)
plt.show()
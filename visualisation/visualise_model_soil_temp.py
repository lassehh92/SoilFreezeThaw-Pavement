import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import os
import numpy as np

# Load the observed data
# observed_data = pd.read_csv('forcings/Haandvaerkervej_Perma_road_04Jan2023_to_07feb2024_updated.csv', delimiter=',') 
observed_data = pd.read_csv('forcings/Haandvaerkervej_Perma_road_TRANSIENT_2-nov-2022--7-feb-2024.csv', delimiter=',')
observed_data['time'] = pd.to_datetime(observed_data['time'], format='%m/%d/%y %H:%M')

# Load multiple simulation files
output_dir = 'output/tc_factor_frozen_0.5_unfrozen_2.0_porosity_exp'
simulation_files = [f for f in os.listdir(output_dir) if f.endswith('.dat')]

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


# Process all simulation files
simulations = {
    os.path.splitext(file)[0]: load_and_process_simulation(os.path.join(output_dir, file), depth_increment=3)
    for file in simulation_files
}

# Merge datasets on the time column for comparison
merged_data = observed_data.copy()
for sim_name, sim_data in simulations.items():
    merged_data = pd.merge(merged_data, sim_data, on='time', suffixes=('', f'_{sim_name}'))

# Specify the time period for visualization

# # entire period
# start_date = '2022-11-02 00:00'
# end_date = '2024-02-07 13:30'
# aggregation = 'daily'
# plot_legend_loc='upper left'

# # 1st freeze period
# start_date = '2022-11-02 00:00'
# end_date = '2023-04-07 13:30'
# aggregation = 'hourly'
# plot_legend_loc='lower left'

# # 1st freeze period - local 1st
# start_date = '2022-11-15 00:00'
# end_date = '2023-01-15 13:30'
# aggregation = 'hourly'
# plot_legend_loc='lower left'

# 2nd freeze period
start_date = '2023-11-07 00:00'
end_date = '2024-02-07 13:30'
aggregation = 'hourly'
plot_legend_loc='lower left'

# Filter the merged data for the specified time period
mask = (merged_data['time'] >= start_date) & (merged_data['time'] <= end_date)
filtered_data = merged_data.loc[mask]

# Specify aggregation level: None, 'hourly', or 'daily'
#aggregation = None
#aggregation = 'hourly'
#aggregation = 'daily'

# Perform aggregation if specified
if aggregation == 'hourly':
    filtered_data.set_index('time', inplace=True)
    filtered_data = filtered_data.resample('H').mean().reset_index()
elif aggregation == 'daily':
    filtered_data.set_index('time', inplace=True)
    filtered_data = filtered_data.resample('D').mean().reset_index()

# Calculate statistical measures: r-squared, mean difference, and RMSE
stat_summary = {
    'Depth (cm)': [],
    'Simulation': [],
    'R-squared': [],
#'Mean Difference (Observed - Simulated)': [],
    'NSE': [],
    'RMSE': []
}

# Depth columns to compare
depth_columns = [6, 30]

for depth in depth_columns:
    observed_col = f'Temp_{depth}cm_below_surface'
    for sim_name in simulations.keys():
        simulated_col = f'Temp_{depth}cm_below_surface_{sim_name}'
        
        r_squared = filtered_data[observed_col].corr(filtered_data[simulated_col], method='pearson') ** 2
        mean_diff = (filtered_data[observed_col] - filtered_data[simulated_col]).mean()
        rmse = np.sqrt(((filtered_data[observed_col] - filtered_data[simulated_col]) ** 2).mean())
        # Calculate Nash-Sutcliffe Efficiency (NSE)
        nse = 1 - (np.sum((filtered_data[observed_col] - filtered_data[simulated_col])**2) / 
                   np.sum((filtered_data[observed_col] - filtered_data[observed_col].mean())**2))
        
        stat_summary['Depth (cm)'].append(depth)
        stat_summary['Simulation'].append(sim_name)
        stat_summary['R-squared'].append(r_squared)
        #stat_summary['Mean Difference (Observed - Simulated)'].append(mean_diff)
        stat_summary['NSE'].append(nse)
        stat_summary['RMSE'].append(rmse)
        

stat_summary_df = pd.DataFrame(stat_summary)
stat_summary_df.to_csv('statistical_summary.csv', index=False)
print(stat_summary_df)

# Plot the data
depths_to_compare = [6, 30]
fig, axes = plt.subplots(2, 1, figsize=(14, 12), sharex=True)

observed_color = 'blue'
observed_style = '--'
# Other color map options include:
# sim_colors = plt.cm.Set1(np.linspace(0, 1, len(simulations)))
# sim_colors = plt.cm.Set2(np.linspace(0, 1, len(simulations)))
# sim_colors = plt.cm.Set3(np.linspace(0, 1, len(simulations)))
# sim_colors = plt.cm.Paired(np.linspace(0, 1, len(simulations)))
# sim_colors = plt.cm.tab10(np.linspace(0, 1, len(simulations)))
# sim_colors = plt.cm.tab20(np.linspace(0, 1, len(simulations)))
# sim_colors = plt.cm.Pastel1(np.linspace(0, 1, len(simulations)))
# sim_colors = plt.cm.Pastel2(np.linspace(0, 1, len(simulations)))

# Using 'Set2' as an example:
sim_colors = plt.cm.Set1(np.linspace(0, 1, len(simulations)))

for depth, ax in zip(depths_to_compare, axes):
    ax.plot(filtered_data['time'], filtered_data[f'Temp_{depth}cm_below_surface'], 
            label='Observed', color=observed_color, linestyle=observed_style, linewidth=2)
    
    for i, (sim_name, _) in enumerate(sorted(simulations.items())):
        ax.plot(filtered_data['time'], filtered_data[f'Temp_{depth}cm_below_surface_{sim_name}'], 
                label=f'Simulated ({sim_name})', color=sim_colors[i], linewidth=1.5, alpha=0.8)
    
    ax.set_title(f'Temperature at {depth} cm Below Surface (aggregation level = {aggregation})', fontsize=14)
    ax.set_ylabel('Temperature (°C)', fontsize=12)
    ax.legend(fontsize=10, loc=plot_legend_loc)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.tick_params(axis='both', which='major', labelsize=10)

axes[1].set_xlabel('Time', fontsize=12)

plt.tight_layout()
plt.suptitle('Soil Temperature Comparison at Different Depths', fontsize=16, y=1.02)
plt.show()
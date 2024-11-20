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
#output_dir = 'output/best_NSE_exp_25-sep-2024' # exp 1
#output_dir = 'output/best_NSE_3_level_exp_25-sep-2024' # exp 2
#output_dir = 'output/best_NSE_exp_18-oct' # exp 3
#output_dir = 'output/best_21-oct' # exp 4
#output_dir = 'output/best_24-oct' # exp 5

# output_dir = 'output/best_clay_2_level_25-sep-2024' # exp 1
# soiltype = 'Clay'
# parameters = 'TC\\ Frozen,\\ TC\\ Unfrozen'

# output_dir = 'output/best_clay_3_level_25-sep-2024' # exp 2
# soiltype = 'Clay'
# parameters = 'TC\\ Frozen,\\ TC\\ Unfrozen,\\ Porosity'

# output_dir = 'output/best_clay_23-oct' # exp 6
# soiltype = 'Clay'
# parameters = 'TC\\ Frozen,\\ TC\\ Unfrozen,\\ HC\\ Soil'

# output_dir = 'output/best_sand_soil' # exp 7
# soiltype = 'Sand' 
# parameters = 'TC\\ Frozen,\\ TC\\ Unfrozen,\\ HC\\ Soil'


# output_dir = 'output/best-15-nov-fine' 
# soiltype = 'Clay'
# parameters = 'TC\\ Frozen,\\ TC\\ Unfrozen,\\ HC\\ Soil'



output_dir = 'output/sensitivity_analysis_smcmax'
soiltype = 'Clay'
parameters = 'SMCmax'


# output_dir = 'output/sensitivity_analysis_hcsoil'
# soiltype = 'Clay'
# parameters = 'HCsoil'

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
# period = 'Entire'
# ylimit_range = (-5, 35)

# # 1st freeze period 
# start_date = '2022-11-15 00:00'
# end_date = '2023-01-15 13:30'
# aggregation = 'hourly'
# plot_legend_loc='lower left'
# period = '1st\\ freeze'
# ylimit_range = (-12, 12)

# 2nd freeze period
start_date = '2023-11-07 00:00'
end_date = '2024-02-07 13:30'
aggregation = 'hourly'  
plot_legend_loc='lower left'
period = '2nd\\ freeze'


# # 2nd freeze period
# start_date = '2023-11-01 00:00'
# end_date = '2024-02-01 00:00'
# aggregation = 'hourly'  
# plot_legend_loc='lower left'
# period = '2nd\\ freeze'
# ylimit_range = (-12, 12)

########

# # 1st freeze period (long)
# start_date = '2022-11-02 00:00'
# end_date = '2023-04-07 13:30'
# aggregation = 'hourly'
# plot_legend_loc='lower left'

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
depth = 6  # Only plotting 6cm depth
ylimit_range = (-12, 12)

# depth = 30  # Only plotting 30cm depth
# ylimit_range = (-5, 12)

fig, ax = plt.subplots(figsize=(14, 6))  # Single plot instead of subplots

# Get sorted simulation names to ensure consistent ordering
sorted_sim_names = sorted(simulations.keys())

# Plot observed data
ax.plot(filtered_data['time'], filtered_data[f'Temp_{depth}cm_below_surface'], 
        label='Observed', color='#B22222', linestyle='--', linewidth=2)

# Get data for all simulations
sim1_data = filtered_data[f'Temp_{depth}cm_below_surface_{sorted_sim_names[0]}']  # SMCmax = 0.4
sim2_data = filtered_data[f'Temp_{depth}cm_below_surface_{sorted_sim_names[1]}']  # SMCmax = 0.5
sim3_data = filtered_data[f'Temp_{depth}cm_below_surface_{sorted_sim_names[2]}']  # SMCmax = 0.6

# Calculate min and max values for fill_between
lower_bound = np.minimum(sim1_data, sim3_data)
upper_bound = np.maximum(sim1_data, sim3_data)

# Plot the interval area
ax.fill_between(filtered_data['time'], lower_bound, upper_bound, 
                alpha=0.15, color='grey')

# Plot all simulation lines
ax.plot(filtered_data['time'], sim1_data,
       color='#6CA6CD', linestyle='-', linewidth=1,
       label='smcmax = 0.4')

ax.plot(filtered_data['time'], sim2_data,
       color='#104E8B', linestyle='-', linewidth=1.5,
       label='smcmax = 0.5')

ax.plot(filtered_data['time'], sim3_data,
       color='#082F57', linestyle='-', linewidth=1,
       label='smcmax = 0.6')

# Set y-axis limits
ax.set_ylim(ylimit_range)

title = rf"Temperature at $\mathbf{{{depth} cm}}$ Below Surface | $\mathbf{{{period}}}$ period | $\mathbf{{{soiltype}}}$ soil | Parameters = $\mathbf{{{parameters}}}$"
ax.set_title(title, fontsize=12)
ax.set_ylabel('Temperature (°C)', fontsize=12)
ax.set_xlabel('Time', fontsize=12)
ax.legend(fontsize=10, loc=plot_legend_loc)
ax.grid(True, linestyle='--', alpha=0.7)
ax.tick_params(axis='both', which='major', labelsize=10)

plt.tight_layout()
plt.show()

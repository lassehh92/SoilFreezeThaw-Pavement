import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import os
import numpy as np
import plotly.express as px
import re
from tqdm import tqdm

# Load the observed data
# observed_data = pd.read_csv('forcings/Haandvaerkervej_Perma_road_04Jan2023_to_07feb2024_updated.csv', delimiter=',') 
observed_data = pd.read_csv('forcings/Haandvaerkervej_Perma_road_TRANSIENT_2-nov-2022--7-feb-2024.csv', delimiter=',')
observed_data['time'] = pd.to_datetime(observed_data['time'], format='%m/%d/%y %H:%M')

# Load multiple simulation files
#output_dir = 'output/tc_factor_frozen_unfrozen_exp_25-sep-2024'
output_dir = 'output/tc_factor_test'
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
simulations = {}
print("Loading and processing simulation files:")
for file in tqdm(simulation_files, desc="Processing simulations"):
    sim_name = os.path.splitext(file)[0]
    simulations[sim_name] = load_and_process_simulation(os.path.join(output_dir, file), depth_increment=3)

# Merge datasets on the time column for comparison
merged_data = observed_data.copy()
print("Merging datasets:")
for sim_name, sim_data in tqdm(simulations.items(), desc="Merging simulations"):
    # Select only the columns we need from sim_data
    sim_cols = ['time'] + [col for col in sim_data.columns if col.startswith('Temp_6cm') or col.startswith('Temp_30cm')]
    sim_data_subset = sim_data[sim_cols]
    
    # Rename the temperature columns in sim_data to avoid conflicts
    new_columns = ['time']
    for col in sim_data_subset.columns:
        if col != 'time':
            new_columns.append(f'{col}_{sim_name}')
    
    # Ensure the number of new column names matches the number of columns
    if len(new_columns) != len(sim_data_subset.columns):
        print(f"Warning: Mismatch in column numbers for simulation {sim_name}. Skipping this simulation.")
        continue
    
    sim_data_subset.columns = new_columns
    
    # Merge with the existing data
    merged_data = pd.merge(merged_data, sim_data_subset, on='time', how='outer')

#merged_data.to_csv(output_dir + 'merged_data.csv', index=False)

# print("Merge complete.")
# print("Columns in merged_data:")
# print(merged_data.columns.tolist())
# print("\nFirst few rows of merged_data:")
# print(merged_data.head())

### VISUALISATION OF SOIL TEMPERATURE USING PARALLEL COORDINATES PLOT ###


# Specify the time period for visualization

# # entire period
# start_date = '2022-11-02 00:00'
# end_date = '2024-02-07 13:30'
# aggregation = 'daily'

# # 1st freeze period
# start_date = '2022-11-02 00:00'
# end_date = '2023-04-07 13:30'
# aggregation = 'hourly'

# # 1st freeze period - local 1st
# start_date = '2022-11-15 00:00'
# end_date = '2023-01-15 13:30'
# aggregation = 'hourly'

# 2nd freeze period
start_date = '2023-11-07 00:00'
end_date = '2024-02-07 13:30'
aggregation = 'hourly'

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
    filtered_data = filtered_data.resample('h').mean().reset_index()
elif aggregation == 'daily':
    filtered_data.set_index('time', inplace=True)
    filtered_data = filtered_data.resample('D').mean().reset_index()

# Calculate statistical measures: r-squared, mean difference, and RMSE
stat_summary = {
    'Depth (cm)': [],
    'Simulation': [],
    'R-squared': [],
    'NSE': [],
    'RMSE': []
}

# Depth columns to compare
depth_columns = [6, 30]

print("Simulation names:")
print(list(simulations.keys()))

print("Calculating statistical measures:")
for depth in tqdm(depth_columns, desc="Processing depths"):
    observed_col = f'Temp_{depth}cm_below_surface'
    for sim_name in simulations.keys():
        simulated_col = f'Temp_{depth}cm_below_surface_{sim_name}'
        
        r_squared = filtered_data[observed_col].corr(filtered_data[simulated_col], method='pearson') ** 2
        mean_diff = (filtered_data[observed_col] - filtered_data[simulated_col]).mean()
        rmse = np.sqrt(((filtered_data[observed_col] - filtered_data[simulated_col]) ** 2).mean())
        nse = 1 - (np.sum((filtered_data[observed_col] - filtered_data[simulated_col])**2) / 
                   np.sum((filtered_data[observed_col] - filtered_data[observed_col].mean())**2))
        
        stat_summary['Depth (cm)'].append(depth)
        stat_summary['Simulation'].append(sim_name)
        stat_summary['R-squared'].append(r_squared)
        stat_summary['NSE'].append(nse)
        stat_summary['RMSE'].append(rmse)
        
stat_summary_df = pd.DataFrame(stat_summary)
#stat_summary_df.to_csv('output/statistical_summary.csv', index=False)
#print(stat_summary_df)

# Extract variables from simulation names
def extract_variables(sim_name):
    pattern = r'tc_f_(\d+\.\d+)_tc_uf_(\d+\.\d+)_smcmax_(\d+\.\d+)'
    match = re.search(pattern, sim_name)
    if match:
        return {
            'tc_f': float(match.group(1)),
            'tc_uf': float(match.group(2)),
            'smcmax': float(match.group(3))
        }
    return None

# Create a new dataframe for the parallel coordinate plot
plot_data = []
for _, row in stat_summary_df.iterrows():
    sim_vars = extract_variables(row['Simulation'])
    if sim_vars:
        plot_data.append({
            'Simulation': row['Simulation'],
            'Depth (cm)': row['Depth (cm)'],
            'R-squared': row['R-squared'],
            'NSE': row['NSE'],
            'RMSE': row['RMSE'],
            'tc_f': sim_vars['tc_f'],
            'tc_uf': sim_vars['tc_uf'],
            'smcmax': sim_vars['smcmax']
        })

plot_df = pd.DataFrame(plot_data)
#print(plot_df)
# Function to create parallel coordinate plot
def create_parallel_plot(depth, metric):
    # Filter data for the selected depth
    depth_df = plot_df[plot_df['Depth (cm)'] == depth]
    
    # Prepare dimensions including the metric
    #dimensions = ['tc_f', 'tc_uf', 'smcmax', metric]
    dimensions = ['tc_f', 'tc_uf', metric]
    
    # Create parallel coordinate plot
    fig = px.parallel_coordinates(
        depth_df, 
        color=metric,
        dimensions=dimensions,
        labels={
            "tc_f": "TC Frozen",
            "tc_uf": "TC Unfrozen",
            "smcmax": "SMCMAX",
            "R-squared": "R-squared",
            "NSE": "NSE",
            "RMSE": "RMSE"
        },
        color_continuous_scale=px.colors.sequential.Plasma_r,
        color_continuous_midpoint=depth_df[metric].mean()
    )

    # Update layout
    fig.update_layout(
        title=f"Parallel Coordinates Plot for {depth} cm Depth ({start_date} to {end_date})",
        coloraxis_colorbar=dict(title=metric)
    )
    # Reverse the color scale of the metric dimension only for RMSE
    for dimension in fig.data[0].dimensions:
        if dimension.label == metric and metric == 'RMSE':
            fig.update_layout(coloraxis_colorscale=px.colors.sequential.Plasma)

    return fig

# Set options
depth_option = 30  # or 30
metric_option = 'NSE'  # or 'NSE' or 'R-squared'

# Create and show the plot
fig = create_parallel_plot(depth_option, metric_option)
fig.show()

# Optionally, save the plot as an HTML file
#fig.write_html(f"output/parallel_coordinates_plot_{depth_option}cm_{metric_option}.html")

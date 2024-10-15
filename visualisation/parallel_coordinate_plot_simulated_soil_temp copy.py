import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import os
import numpy as np
import plotly.express as px
import re
from tqdm import tqdm

# Load merged data
#output_dir = 'output/tc_factor_frozen_unfrozen_exp_25-sep-2024'
output_dir = 'output/tc_frozen_unfrozen_smcmax_exp_25-sep-2024'

merged_data = pd.read_csv(os.path.join(output_dir, 'merged_data.csv'))

# Convert 'time' column to datetime
merged_data['time'] = pd.to_datetime(merged_data['time'])

# Create a list of simulation names by removing the "Temp_6cm_below_surface_" prefix
simulation_names = [col.replace("Temp_6cm_below_surface_", "") for col in merged_data.columns if col.startswith("Temp_6cm_below_surface_soil_temp")]
# print("Simulation names:")
# for name in simulation_names:
#     print(name)



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

# 1st freeze period - local 1st
start_date = '2022-11-15 00:00'
end_date = '2023-01-15 13:30'
aggregation = 'hourly'

# # 2nd freeze period
# start_date = '2023-11-07 00:00'
# end_date = '2024-02-07 13:30'
# aggregation = 'hourly'

# Filter the merged data for the specified time period
mask = (merged_data['time'] >= start_date) & (merged_data['time'] <= end_date)
filtered_data = merged_data.loc[mask].copy()

# Specify aggregation level: None, 'hourly', or 'daily'
#aggregation = None
#aggregation = 'hourly'
#aggregation = 'daily'

# Perform aggregation if specified
if aggregation == 'hourly':
    filtered_data = filtered_data.resample('H', on='time').mean().reset_index()
elif aggregation == 'daily':
    filtered_data = filtered_data.resample('D', on='time').mean().reset_index()

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

print("Calculating statistical measures:")
for depth in tqdm(depth_columns, desc="Processing depths"):
    observed_col = f'Temp_{depth}cm_below_surface'
    for sim_name in simulation_names:
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
    dimensions = ['tc_f', 'tc_uf', 'smcmax', metric]
    #dimensions = ['tc_f', 'tc_uf', metric]
    
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
depth_option = 30 # 6 or 30
metric_option = 'RMSE'  # or 'RMSE' or 'NSE' or 'R-squared'

# Create and show the plot
# fig = create_parallel_plot(depth_option, 'R-squared')
# fig.show()

# fig = create_parallel_plot(depth_option, 'RMSE')
# fig.show()

fig = create_parallel_plot(depth_option, 'NSE')
fig.show()

# Optionally, save the plot as an HTML file
#fig.write_html(f"output/parallel_coordinates_plot_{depth_option}cm_{metric_option}.html")

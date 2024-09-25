import pandas as pd
from io import StringIO
import os
import numpy as np
from tqdm import tqdm

# Load the observed data
# observed_data = pd.read_csv('forcings/Haandvaerkervej_Perma_road_04Jan2023_to_07feb2024_updated.csv', delimiter=',') 
observed_data = pd.read_csv('forcings/Haandvaerkervej_Perma_road_TRANSIENT_2-nov-2022--7-feb-2024.csv', delimiter=',')
observed_data['time'] = pd.to_datetime(observed_data['time'], format='%m/%d/%y %H:%M')

# Load multiple simulation files
output_dir = 'output/tc_factor_frozen_unfrozen_exp_25-sep-2024'
#output_dir = 'output/tc_factor_test'
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

merged_data.to_csv(os.path.join(output_dir, 'merged_data.csv'), index=False)

# print("Merge complete.")
# print("Columns in merged_data:")
# print(merged_data.columns.tolist())
# print("\nFirst few rows of merged_data:")
# print(merged_data.head())


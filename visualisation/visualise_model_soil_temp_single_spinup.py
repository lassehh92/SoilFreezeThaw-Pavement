import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Load the observed data
observed_data = pd.read_csv('forcings/Haandvaerkervej_Perma_road_SPINUP_4-okt-2022--2-nov-2022_LOOP_5_times.csv', delimiter=',')

# Load the simulated data
with open('output/soil_temp_spinup.dat', 'r') as file:
    lines = file.readlines()

# Remove comment lines from simulated data
cleaned_lines = [line for line in lines if not line.startswith('#')]

# Read the cleaned lines into a DataFrame
simulated_data = pd.read_csv(StringIO(''.join(cleaned_lines)), delimiter=',')

# Print row number 1
print("\nRow number 1 of simulated data:")
print(simulated_data.iloc[0])

# Print row number 10
print("\nRow number 10 of simulated data:")
print(simulated_data.iloc[9])

# Rename columns for clarity
observed_data = observed_data.rename(columns={
    'Temp_6cm_below_surface': 'Observed_Temp_6cm',
    'Temp_30cm_below_surface': 'Observed_Temp_30cm'
})
simulated_data = simulated_data.rename(columns={
    simulated_data.columns[3]: 'Simulated_Temp_6cm',
    simulated_data.columns[11]: 'Simulated_Temp_30cm'  
})

# Convert simulated temperatures from Kelvin to Celsius
simulated_data['Simulated_Temp_6cm'] = simulated_data['Simulated_Temp_6cm'] - 273.15
simulated_data['Simulated_Temp_30cm'] = simulated_data['Simulated_Temp_30cm'] - 273.15

# Define the index where you want the color to change
change_index = 4250  # Change this to your desired index

# Create subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# Plot 6cm data
ax1.plot(observed_data.index[:change_index], observed_data['Observed_Temp_6cm'][:change_index], label='Observed (4-okt-2022 - 2-nov-2022)', color='blue')
ax1.plot(observed_data.index[change_index:], observed_data['Observed_Temp_6cm'][change_index:], label='Added 4 Loops (11-okt - 2-nov)', color='lightblue')
ax1.plot(simulated_data.index, simulated_data['Simulated_Temp_6cm'], label='Simulated', color='orange')
ax1.set_title('Temperature at 6cm Depth')
ax1.set_ylabel('Temperature (°C)')
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.7)

# Plot 30cm data
ax2.plot(observed_data.index[:change_index], observed_data['Observed_Temp_30cm'][:change_index], label='Observed (4-okt-2022 - 2-nov-2022)', color='blue')
ax2.plot(observed_data.index[change_index:], observed_data['Observed_Temp_30cm'][change_index:], label='Added 4 Loops (11-okt - 2-nov)', color='lightblue')
ax2.plot(simulated_data.index, simulated_data['Simulated_Temp_30cm'], label='Simulated', color='orange')
ax2.set_title('Temperature at 30cm Depth')
ax2.set_xlabel('Index')
ax2.set_ylabel('Temperature (°C)')
ax2.legend()
ax2.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

# Print some debug information
print("Observed data shape:", observed_data.shape)
print("Simulated data shape:", simulated_data.shape)
print("Observed columns:", observed_data.columns)
print("Simulated columns:", simulated_data.columns)
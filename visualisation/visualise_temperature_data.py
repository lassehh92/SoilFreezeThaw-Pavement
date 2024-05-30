import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = 'forcings/Haandvaerkervej_Perma_road_All_data_04Jan2023_to_07feb2024_updated_converted.csv'  # Replace with your file path
df = pd.read_csv(file_path)

# Parse the 'time' column to datetime
df['time'] = pd.to_datetime(df['time'], errors='coerce')

# Plot the temperature values at different depths
plt.figure(figsize=(14, 7))
plt.plot(df['time'], df['Temp_3cm_below_surface'], label='Temp 3cm below surface')
plt.plot(df['time'], df['Temp_6cm_below_surface'], label='Temp 6cm below surface')
plt.plot(df['time'], df['Temp_30cm_below_surface'], label='Temp 30cm below surface')

plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.title('Temperature Measurements at Different Depths')
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()

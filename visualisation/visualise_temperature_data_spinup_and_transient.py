import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the SpinUp CSV file
file_path_1 = '/Users/lhh/github-projects/SoilFreezeThaw-Pavement-2/forcings/Haandvaerkervej_Perma_road_SPINUP_4-okt-2022--2-nov-2022.csv'
df1 = pd.read_csv(file_path_1)
df1['time'] = pd.to_datetime(df1['time'], format='%m/%d/%y %H:%M', errors='coerce')

# Load the new CSV file
file_path_2 = '/Users/lhh/github-projects/SoilFreezeThaw-Pavement-2/forcings/Haandvaerkervej_Perma_road_TRANSIENT_2-nov-2022--7-feb-2024.csv'
df2 = pd.read_csv(file_path_2)
df2['time'] = pd.to_datetime(df2['time'], format='%m/%d/%y %H:%M', errors='coerce')

# Remove rows with NaT (Not a Time) values
df1 = df1.dropna(subset=['time'])
df2 = df2.dropna(subset=['time'])

# Sort dataframes by time
df1 = df1.sort_values('time')
df2 = df2.sort_values('time')

# Plot the temperature values at different depths
plt.figure(figsize=(14, 7))
plt.plot(df2['time'], df2['Temp_3cm_below_surface'], label='Temp 3cm below surface (Transient)', color='lightblue', linewidth=0.75)
plt.plot(df1['time'], df1['Temp_3cm_below_surface'], label='Temp 3cm below surface (SpinUp)', color='lightgreen', linewidth=0.75)

plt.plot(df2['time'], df2['Temp_30cm_below_surface'], label='Temp 30cm below surface (Transient)', color='blue', linewidth=0.75)
plt.plot(df1['time'], df1['Temp_30cm_below_surface'], label='Temp 30cm below surface (SpinUp)', color='green', linewidth=0.75)

plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.title('Observed Temperature at 3cm and 30cm below surface')
plt.legend()
plt.grid(True)

# Format x-axis to show dates nicely
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.gcf().autofmt_xdate()  # Rotate and align the tick labels

plt.tight_layout()
plt.show()

# Print some diagnostic information
print(f"SpinUp data range: {df1['time'].min()} to {df1['time'].max()}")
print(f"Transient data range: {df2['time'].min()} to {df2['time'].max()}")
print(f"SpinUp data points: {len(df1)}")
print(f"Transient data points: {len(df2)}")
import pandas as pd
import matplotlib.pyplot as plt

# Load the SpinUp CSV file
file_path_1 = '/Users/lhh/github-projects/SoilFreezeThaw-Pavement-2/forcings/Haandvaerkervej_Perma_road_SPINUP_4-okt-2022--2-nov-2022.csv'
df1 = pd.read_csv(file_path_1)
df1['time'] = pd.to_datetime(df1['time'], errors='coerce')

# Load the new CSV file
file_path_2 = '/Users/lhh/github-projects/SoilFreezeThaw-Pavement-2/forcings/Haandvaerkervej_Perma_road_TRANSIENT_2-nov-2022--7-feb-2024.csv'
df2 = pd.read_csv(file_path_2)
df2['time'] = pd.to_datetime(df2['time'], errors='coerce')

# Set start and end dates for visualization
start_date = '2022-10-03'  # Replace with your desired start date
end_date = '2024-02-07'    # Replace with your desired end date

# Filter the DataFrames based on the specified date range
mask1 = (df1['time'] >= start_date) & (df1['time'] <= end_date)
filtered_df1 = df1.loc[mask1]

mask2 = (df2['time'] >= start_date) & (df2['time'] <= end_date)
filtered_df2 = df2.loc[mask2]

# Plot the temperature values at different depths
plt.figure(figsize=(14, 7))
plt.plot(filtered_df2['time'], filtered_df2['Temp_3cm_below_surface'], label='Temp ground surface (Transient)', color='lightblue', linewidth=0.75)
plt.plot(filtered_df1['time'], filtered_df1['Temp_3cm_below_surface'], label='Temp ground surface (SpinUp)', color='lightgreen', linewidth=0.75)

#plt.plot(filtered_df1['time'], filtered_df1['Temp_30cm_below_surface'], label='Temp 30cm below surface (Old)', color='blue')
plt.plot(filtered_df2['time'], filtered_df2['Temp_30cm_below_surface'], label='Temp 30cm below surface (Transient)', color='blue', linewidth=0.75)
plt.plot(filtered_df1['time'], filtered_df1['Temp_30cm_below_surface'], label='Temp 30cm below surface (SpinUp)', color='green', linewidth=0.75)

# plt.plot(filtered_df2['time'], filtered_df2['Temp_6cm_below_surface'], label='Temp 6cm below surface (New)', color='orange')
# plt.plot(filtered_df1['time'], filtered_df1['Temp_6cm_below_surface'], label='Temp 6cm below surface (Old)', color='blue', linewidth=0.6)



plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.title('Observed Temperature at ground surface and 30cm below surface')
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()
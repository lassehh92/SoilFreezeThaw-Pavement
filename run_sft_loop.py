import subprocess
import os
import shutil

# Define the range of values for each parameter
tc_factor_frozen_values = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
tc_factor_unfrozen_values = [1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0]
smcmax_values = [0.468]

# Path to the configuration file
config_file = 'configs/haandvaerkervej_config_sft_dz_3cm_transient.txt'

def update_config(tc_frozen, tc_unfrozen, smcmax):
    with open(config_file, 'r') as f:
        lines = f.readlines()

    # Update or add the parameters
    params = {
        'tc_factor_frozen': tc_frozen,
        'tc_factor_unfrozen': tc_unfrozen,
        'soil_params.smcmax': smcmax
    }

    updated_lines = []
    for line in lines:
        key = line.split('=')[0].strip()
        if key in params:
            updated_lines.append(f"{key}={params[key]}\n")
            del params[key]
        else:
            updated_lines.append(line)

    # Add any remaining parameters that weren't in the original file
    for key, value in params.items():
        updated_lines.append(f"{key}={value}\n")

    with open(config_file, 'w') as f:
        f.writelines(updated_lines)

# Loop through all combinations of parameters
for tc_frozen in tc_factor_frozen_values:
    for tc_unfrozen in tc_factor_unfrozen_values:
        for smcmax in smcmax_values:
            # Update the configuration file
            update_config(tc_frozen, tc_unfrozen, smcmax)

            # Run the shell script
            print(f"Running with tc_factor_frozen={tc_frozen}, tc_factor_unfrozen={tc_unfrozen}, smcmax={smcmax}")
            subprocess.run(['./run_sft.sh', 'PFRAMEWORK'], check=True)

            # Rename the output file
            original_file = 'output/soil_temp.dat'
            new_filename = f'soil_temp_tc_f_{tc_frozen}_tc_uf_{tc_unfrozen}_smcmax_{smcmax}.dat'
            new_file = os.path.join('output', new_filename)
            
            if os.path.exists(original_file):
                shutil.move(original_file, new_file)
                print(f"Renamed output file to: {new_filename}")
            else:
                print(f"Warning: {original_file} not found after simulation.")

print("All simulations completed.")
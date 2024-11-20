import subprocess
import os
import shutil

# Define the range of values for each parameter

# Exp TC frozen Unfrozen -- 25-sep-2024
# tc_factor_frozen_values = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
# tc_factor_unfrozen_values = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0]
# smcmax_values = [0.468]

# # Exp TC frozen Unfrozen SMCmax -- 25-sep-2024
# tc_factor_frozen_values = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
# tc_factor_unfrozen_values = [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8]
# smcmax_values = [0.2, 0.3, 0.4, 0.45, 0.5, 0.6, 0.7]
# hcsoil_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

# # Exp TC frozen Unfrozen SMCmax HCsoil -- 18-oct-2024
# tc_factor_frozen_values = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
# tc_factor_unfrozen_values = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8]
# smcmax_values = [0.3, 0.4]
# hcsoil_values = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]

# # Exp TC frozen Unfrozen SMCmax HCsoil -- 21-oct-2024
# tc_factor_frozen_values = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
# tc_factor_unfrozen_values = [1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4]
# smcmax_values = [0.35]
# hcsoil_values = [1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5]

# # Exp TC frozen Unfrozen SMCmax HCsoil -- 22-oct-2024
# tc_factor_frozen_values = [0.3, 0.4, 0.5, 0.6]
# tc_factor_unfrozen_values = [2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5]
# smcmax_values = [0.35]
# hcsoil_values = [2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5]


# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 23-oct-2024
# tc_factor_frozen_values = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
# tc_factor_unfrozen_values = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
# smcmax_values = [0.35]
# hcsoil_values = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0]



# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 24-oct-2024
# tc_factor_frozen_values = [0.8, 1.0, 1.5, 2.0, 2.5]
# tc_factor_unfrozen_values = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]
# smcmax_values = [0.35]
# hcsoil_values = [5.0, 6.0, 7.0, 8.0, 9.0, 10.0]



# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 24-oct-2024
# tc_factor_frozen_values = [1.0, 1.5, 2.0]
# tc_factor_unfrozen_values = [5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
# smcmax_values = [0.35]
# hcsoil_values = [8.0, 9.0, 10.0, 11.0, 12.0]

# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 24-oct-2024
# tc_factor_frozen_values = [1.5, 2.0, 2.5]
# tc_factor_unfrozen_values = [7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0]
# smcmax_values = [0.35]
# hcsoil_values = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0]

# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 23-oct-2024 -- FINAL
# tc_factor_frozen_values = [1.0, 1.5, 2.0, 2.5, 3.0]
# tc_factor_unfrozen_values = [4.0, 6.0, 8.0, 10.0, 12.0, 14.0]
# smcmax_values = [0.468]
# hcsoil_values = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0]
# config_file = 'configs/haandvaerkervej_config_sft_dz_3cm_transient.txt'

### SAND SOIL ###

# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 24-oct-2024
# tc_factor_frozen_values = [1.0, 1.5, 2.5, 3.0]
# tc_factor_unfrozen_values = [4.0, 6.0, 8.0, 10.0, 12.0, 14.0]
# smcmax_values = [0.35]
# hcsoil_values = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0]
# #config_file = 'configs/haandvaerkervej_config_sft_dz_3cm_transient_sand_soil.txt'

# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 24-oct-2024
# tc_factor_frozen_values = [1.0, 1.5, 2.5, 3.0]
# tc_factor_unfrozen_values = [4.0, 6.0, 8.0, 10.0, 12.0, 14.0]
# smcmax_values = [0.35]
# hcsoil_values = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0]
# #config_file = 'configs/haandvaerkervej_config_sft_dz_3cm_transient_sand_soil.txt'

# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 24-oct-2024
# tc_factor_frozen_values = [0.25, 0.5, 0.75, 1.0]
# tc_factor_unfrozen_values = [1.0, 2.0, 3.0, 4.0, 5.0]
# smcmax_values = [0.35]
# hcsoil_values = [2.0, 4.0, 6.0, 8.0, 10.0]
# #config_file = 'configs/haandvaerkervej_config_sft_dz_3cm_transient_sand_soil.txt'

# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 24-oct-2024
# tc_factor_frozen_values = [1.0, 1.5, 2.5, 3.0, 4.0, 5.0]
# tc_factor_unfrozen_values = [4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0] #4.0, 6.0, 8.0, 10.0, 12.0, 14.0  
# smcmax_values = [0.35]
# hcsoil_values = [6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0] #
# #config_file = 'configs/haandvaerkervej_config_sft_dz_3cm_transient_sand_soil.txt'


# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 24-oct-2024
# tc_factor_frozen_values = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
# tc_factor_unfrozen_values = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0] #4.0, 6.0, 8.0, 10.0, 12.0, 14.0  
# smcmax_values = [0.35]
# hcsoil_values = [20.0, 22.0, 24.0, 26.0, 28.0, 30.0] #6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0
# #config_file = 'configs/haandvaerkervej_config_sft_dz_3cm_transient_sand_soil.txt'


# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 24-oct-2024
# tc_factor_frozen_values = [4.0, 5.0, 6.0, 7.0, 8.0]
# tc_factor_unfrozen_values = [16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0] #4.0, 6.0, 8.0, 10.0, 12.0, 14.0  
# smcmax_values = [0.35]
# hcsoil_values = [28.0, 30.0, 32.0, 34.0, 36.0, 38.0, 40.0] #6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0
# #config_file = 'configs/haandvaerkervej_config_sft_dz_3cm_transient_sand_soil.txt'

# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 24-oct-2024
# tc_factor_frozen_values = [5.0, 6.0, 7.0, 8.0]
# tc_factor_unfrozen_values = [30.0] #[16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0] #4.0, 6.0, 8.0, 10.0, 12.0, 14.0  
# smcmax_values = [0.35]
# hcsoil_values = [32.0, 34.0, 36.0, 38.0, 40.0] #[28.0, 30.0, 32.0, 34.0, 36.0, 38.0, 40.0] #6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0
#config_file = 'configs/haandvaerkervej_config_sft_dz_3cm_transient_sand_soil.txt'

#### 14 November 2024 ###
#### CLAY SOIL ###

## Exp TC frozen Unfrozen SMCmax HCsoil -- 14-nov-2024
# tc_factor_frozen_values = [1.0, 1.5, 2.0, 2.5]
# tc_factor_unfrozen_values = [6.0, 8.0, 10.0, 12.0]
# smcmax_values = [0.5]
# hcsoil_values = [10.0, 15.0, 20.0]



# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 15-nov-2024
# tc_factor_frozen_values =  [1.5, 2.0, 2.5, 2.75, 3.0, 3.5]
# tc_factor_unfrozen_values = [7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0]
# smcmax_values = [0.5]
# hcsoil_values = [18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0]

# ## Exp TC frozen Unfrozen SMCmax HCsoil -- 15-nov-2024
# tc_factor_frozen_values =  [2.0, 2.1, 2.2, 2.3, 2.4, 2.5]
# tc_factor_unfrozen_values = [10.0, 10.5, 11.0, 11.5, 12.0]
# smcmax_values = [0.5]
# hcsoil_values = [22.0]


# ## Exp TC frozen Unfrozen SMCmax HCsoil -- sensitivity analysis on smcmax
# tc_factor_frozen_values =  [2.3]
# tc_factor_unfrozen_values = [10.5]
# smcmax_values = [0.5]
# hcsoil_values = [12.0, 22.0, 32.0]


# #### corrected gravel layer depth 20-nov-2024 ###
# tc_factor_frozen_values =  [2.0, 2.1, 2.2, 2.3, 2.4, 2.5]
# tc_factor_unfrozen_values = [10.0, 10.5, 11.0, 11.5, 12.0]
# smcmax_values = [0.5]
# hcsoil_values = [22.0]

## Exp TC frozen Unfrozen SMCmax HCsoil -- sensitivity analysis on smcmax
tc_factor_frozen_values =  [2.2]
tc_factor_unfrozen_values = [10.5]
smcmax_values = [0.5]
hcsoil_values = [12.0, 22.0, 32.0]


# Path to the configuration file
config_file = 'configs/haandvaerkervej_config_sft_dz_3cm_transient.txt'
#config_file = 'configs/haandvaerkervej_config_sft_dz_3cm_transient_sand_soil.txt'

def update_config(tc_frozen, tc_unfrozen, smcmax, hcsoil):
    with open(config_file, 'r') as f:
        lines = f.readlines()

    # Update or add the parameters
    params = {
        'tc_factor_frozen': tc_frozen,
        'tc_factor_unfrozen': tc_unfrozen,
        'soil_params.smcmax': smcmax,
        'hcsoil_factor': hcsoil,
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
            for hcsoil in hcsoil_values:
                # Update the configuration file
                update_config(tc_frozen, tc_unfrozen, smcmax, hcsoil)

                # Run the shell script
                print(f"Running with tc_factor_frozen={tc_frozen}, tc_factor_unfrozen={tc_unfrozen}, smcmax={smcmax}, hcsoil={hcsoil}")
                subprocess.run(['./run_sft.sh', 'PFRAMEWORK'], check=True)

                # Rename the output file
                original_file = 'output/soil_temp.dat'
                new_filename = f'soil_temp_tc_f_{tc_frozen}_tc_uf_{tc_unfrozen}_smcmax_{smcmax}_hcsoil_{hcsoil}.dat'
                new_file = os.path.join('output', new_filename)
                
                if os.path.exists(original_file):
                    shutil.move(original_file, new_file)
                    print(f"Renamed output file to: {new_filename}")
                else:
                    print(f"Warning: {original_file} not found after simulation.")

print("All simulations completed.")
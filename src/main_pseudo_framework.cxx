#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#include "../bmi/bmi.hxx"
#include "../include/bmi_soil_freeze_thaw.hxx"
#include "../include/soil_freeze_thaw.hxx"

#include "SoilMoistureProfiles/include/bmi_soil_moisture_profile.hxx"
#include "SoilMoistureProfiles/include/soil_moisture_profile.hxx"

#define FrozenFraction true

// struct having two vectors
struct Vectors {
  std::vector<double> GT_v;
  std::vector<double> WL_v; // water level
  std::vector<string> Time_v; // time
};

Vectors ReadForcingData(std::string config_file);



/************************************************************************
    This main program is a mock framwork.
    This is not part of BMI, but acts as the driver that calls the model.
************************************************************************/
int
main(int argc, const char *argv[])
{

  /************************************************************************
      A configuration file is required for running this model through BMI
  ************************************************************************/
  if(argc<=2){
    printf("make sure to include a path to the CFE config file\n");
    exit(1);
  }
  
  BmiSoilFreezeThaw sft_bmi_model;

  BmiSoilMoistureProfile smp_bmi_model;

  printf("Initializeing BMI SFT model %s\n",argv[1]);
  const char *cfg_file_sft = argv[1];
  sft_bmi_model.Initialize(cfg_file_sft);

  //Read ground temperature data for SFT
  Vectors data = ReadForcingData(cfg_file_sft);
  
  printf("Initializeing BMI SMP model %s\n",argv[2]);
  const char *cfg_file_smp = argv[2];
  smp_bmi_model.Initialize(cfg_file_smp);

  /************************************************************************
    This is the basic process for getting the four things to talk through BMI
    1. Update the AORC forcing data
    2. Getting forcing from AORC and setting forcing for PET
    3. Update the PET model
    3. Getting forcing from AORC and setting forcing for CFE
    4. Getting PET from PET and setting for CFE
    5. Get ice fraction from freeze-thaw model
    5. Update the CFE model.
    6. Update BMI SMP to get updated soil storage/change for the SFT model
    7. Update the Freeze-thaw model (soil temperature/ice content update)
  ************************************************************************/

  
  /************************************************************************
    Now loop through time and call the models with the intermediate get/set
  ************************************************************************/
  printf("looping through and calling updata\n");

  // get time steps
  double endtime  = sft_bmi_model.GetEndTime();
  double timestep = sft_bmi_model.GetTimeStep();
  int nsteps = int(endtime/timestep); // total number of time steps
  std::cout << "End time: " << endtime << std::endl;
  std::cout << "Timestep: " << timestep << std::endl;
  std::cout << "Calculated nsteps: " << nsteps << std::endl;
  std::cout << "Size of GT_v: " << data.GT_v.size() << std::endl;

  assert (nsteps <= int(data.GT_v.size()) ); // assertion to ensure that nsteps are less or equal than the input data
  //nsteps = std::min(nsteps,int(data.GT_v.size())) + 10000;
  //nsteps = std::min(nsteps, int(data.GT_v.size()));
  int ncells;
  sft_bmi_model.GetValue("num_cells", &ncells);
  
  double *ST = new double[ncells];
  double *SMC = new double[ncells];
  double *SICE = new double[ncells];

  std::ofstream fp_st, fp_smc, fp_ice;
  fp_st.open("./output/soil_temp.dat");
  fp_smc.open("./output/soil_moisture.dat");
  fp_ice.open("./output/soil_ice_content.dat");
  
  if (!fp_st || !fp_smc) {
    std::cout<<"output directory does not exist... quiting";
    abort();
  }
  
  fp_st << "#soil temperature profile data [K] \n";
  fp_st << "#index, time, data\n";

  fp_smc << "#soil moisture profile data [-] \n";
  fp_smc << "#index, time, data\n";
  
  for (int i = 0; i < nsteps; i++){
    // data.GT_v[i] = 265.;
    std::cout<<"------------------------------------------------------ \n";
    std::cout<<"Timestep | "<< i <<", ground temp, WL = "<< data.GT_v[i] <<", "<<data.WL_v[i]<<"\n";
    std::cout<<"------------------------------------------------------ \n";

    sft_bmi_model.SetValue("ground_temperature", &data.GT_v[i]);
    smp_bmi_model.SetValue("soil_water_table", &data.WL_v[i]);

    smp_bmi_model.Update(); // Update model

    sft_bmi_model.SetValue("soil_moisture_profile", &SMC[0]);
    
    sft_bmi_model.Update(); // Update model

    sft_bmi_model.GetValue("soil_temperature_profile", &ST[0]);
    smp_bmi_model.GetValue("soil_moisture_profile", &SMC[0]);
    sft_bmi_model.GetValue("soil_ice_profile", &SICE[0]);
    
    fp_st << i<<","<<data.Time_v[i]<<",";
    fp_smc << i<<","<<data.Time_v[i]<<",";
    fp_ice << i<<","<<data.Time_v[i]<<",";
    
    for (int k=0; k<30; k++) {
      fp_st << ST[k] <<",";
      fp_smc << SMC[k] <<",";
      fp_ice << SICE[k] <<",";
    }
    fp_st<<"\n";
    fp_smc<<"\n";
    fp_ice<<"\n";
  }

  fp_st.close();
  fp_smc.close();
  fp_ice.close();
  
  // Run the Mass Balance check
  //mass_balance_check(cfe);

  /************************************************************************
    Finalize both the CFE and AORC bmi models
  ************************************************************************/
  //printf("Finalizing CFE and AORC models\n");
  sft_bmi_model.Finalize();
  return 0;
}


Vectors
ReadForcingData(std::string config_file)
{
  // get the forcing file from the config file

  std::ifstream file;
  file.open(config_file);

  if (!file) {
    std::stringstream errMsg;
    errMsg << config_file << " does not exist";
    throw std::runtime_error(errMsg.str());
  }

  std::string forcing_file;
  bool is_forcing_file_set=false;
  
  while (file) {
    std::string line;
    std::string param_key, param_value;

    std::getline(file, line);

    int loc_eq = line.find("=") + 1;
    param_key = line.substr(0, line.find("="));
    param_value = line.substr(loc_eq,line.length());

    if (param_key == "forcing_file") {
      forcing_file = param_value;
      is_forcing_file_set = true;
      break;
    }
  }

  if (!is_forcing_file_set) {
    std::stringstream errMsg;
    errMsg << config_file << " does not provide forcing_file";
    throw std::runtime_error(errMsg.str());
  }
  
  std::ifstream fp;
  fp.open(forcing_file);
  if (!fp) {
    cout<<"file "<<forcing_file<<" doesn't exist. \n";
    abort();
  }

  Vectors data;
  //std::vector<string> Time_v;
  //std::vector<double> GT_v(0.0);
  //std::vector<double> WT_v(0.0);
  std::vector<string> vars;
  std::string line, cell;
  
  //read first line of strings which contains forcing variables names.
  std::getline(fp, line);
  std::stringstream lineStream(line);
  int ground_temp_index=-1;
  int water_table_index=-1;
  
  while(std::getline(lineStream,cell, ',')) {
    vars.push_back(cell);
  }

  for (unsigned int i = 0; i < vars.size(); i++) {
    if (vars[i] == "TMP_ground_surface") {
      ground_temp_index = i;
      std::cout << "Found TMP_ground_surface at index: " << i << std::endl;
    }
    if (vars[i] ==  "Waterlevel_300cm") {
      water_table_index = i;
      std::cout << "Found Waterlevel_300cm at index: " << i << std::endl;
    }
  }

  if (ground_temp_index <0) {
    ground_temp_index = 1; // 1 is the temperature 3 cm below surface column, if not coupled and ground temperature is not provided
    std::cout << "TMP_ground_surface not found, defaulting ground_temp_index to 1 (Temp_3cm_below_surface)" << std::endl;
  }

  int len_v = vars.size(); // number of forcing variables + time
  std::cout << "Number of forcing variables + time: " << len_v << std::endl;

  int count = 0;
  
  while (fp) {
    std::getline(fp, line);
    std::stringstream lineStream(line);
    while(std::getline(lineStream,cell, ',')) {
      
      if (count % len_v == 0) {
	data.Time_v.push_back(cell);
	count +=1;
	continue;
      }

      if (count % len_v == ground_temp_index) {
	data.GT_v.push_back(stod(cell) +  273.15);
	count +=1;
	continue;
      }

      if (count % len_v == water_table_index) {
	data.WL_v.push_back(stod(cell));
	count +=1;
	continue;
      }
      
      count +=1;
    }

  }
  
  return data;
 
}

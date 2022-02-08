#ifndef FSC_INCLUDED
#define FSC_INCLUDED

#include <cstring>
#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include "../include/smc_profile.hxx"
#define OK (1)

const double smc_profile::SMCProfile::grav = 9.86;
const double smc_profile::SMCProfile::wden = 1000.;

smc_profile::SMCProfile::
SMCProfile()
{
  this->shape[0] = 1;
  this->shape[1] = 1;
  this->shape[2] = 1;
  this->spacing[0] = 1.;
  this->spacing[1] = 1.;
  this->origin[0] = 0.;
  this->origin[1] = 0.;
  this->D =0.0;
  this->config_file = "";
}

smc_profile::SMCProfile::
SMCProfile(std::string config_file)
{
  this->config_file = config_file;
  this->InitFromConfigFile();
  this->shape[0] = this->nz;
  this->shape[1] = 1;
  this->shape[2] = 1;
  this->spacing[0] = 1.;
  this->spacing[1] = 1.;
  this->origin[0] = 0.;
  this->origin[1] = 0.;
  this->InitializeArrays();
  SetLayerThickness(); // get soil layer thickness
}


void smc_profile::SMCProfile::
InitializeArrays(void)
{
  this->Dz = new double[nz];
  this->SMCT = new double[nz];
  this->storage_m = new double[1];
  this->storage_change_m = new double[1];
  //this->water_table_m = new double[1];
  // this->water_table_prev_m = new double[1];
  this->storage_m[0] = 0.0;
  this->storage_change_m[0] = 0.0;
}

void smc_profile::SMCProfile::
InitFromConfigFile()
{ 
  std::ifstream fp;
  fp.open(config_file);
  
  bool is_Z_set = false;
  bool is_smcmax_set = false;
  bool is_bexp_set = false;
  bool is_satpsi_set = false;
  bool is_wt_set = false;
  //bool is_SMCT_set = false; //total moisture content
    
  while (fp) {

    std::string key;
    std::getline(fp, key);
    
    int loc = key.find("=");
    std::string key_sub = key.substr(0,loc);
    
    if (key_sub == "Z") {
      std::string tmp_key = key.substr(loc+1,key.length());
      std::vector<double> vec = ReadVectorData(tmp_key);
      //this->Z = new double[vec.size()];
      this->Z.resize(vec.size());
      for (unsigned int i=0; i < vec.size(); i++) {
	this->Z[i] = vec[i];
	//this->Zv[i] = vec[i];
	//std::cout<<"Z_read: "<<this->Z[i]<<" "<<vec[i]<<" "<<Zv[i]<<"\n";
      }
      this->nz = vec.size();
      this->D = this->Z[this->nz-1];
      is_Z_set = true;
      continue;
    }
    if (key_sub == "soil_params.smcmax") {
      this->smcmax = std::stod(key.substr(loc+1,key.length()));
      is_smcmax_set = true;
      continue;
    }
    if (key_sub == "soil_params.b") {
      this->bexp = std::stod(key.substr(loc+1,key.length()));
      assert (this->bexp > 0);
      is_bexp_set = true;
      continue;
    }
    if (key_sub == "soil_params.satpsi") {  //Soil saturated matrix potential
      this->satpsi = std::stod(key.substr(loc+1,key.length()));
      is_satpsi_set = true;
      continue;
    }

    if (key_sub == "soil_params.water_table") {  //Soil saturated matrix potential
      this->water_table_m = std::stod(key.substr(loc+1,key.length()));
      is_wt_set = true;
      continue;
    }
    
  }
  fp.close();
    
  
  if (!is_Z_set) {
    std::cout<<"Config file: "<<this->config_file<<"\n";
    throw std::runtime_error("Z not set in the config file!");
  }
  
  if (!is_smcmax_set) {
    std::cout<<"Config file: "<<this->config_file<<"\n";
    throw std::runtime_error("smcmax not set in the config file!");
  }
  
  if (!is_bexp_set) {
    std::cout<<"Config file: "<<this->config_file<<"\n";
    throw std::runtime_error("bexp (Clapp-Hornberger's parameter) not set in the config file!");
  }
  if (!is_satpsi_set) {
    std::cout<<"Config file: "<<this->config_file<<"\n";
    throw std::runtime_error("satpsi not set in the config file!");
  }
  
  if (is_wt_set) {
    this->water_table_m = this->D - this->water_table_m;
    *this->water_table_prev_m = this->water_table_m;
  }
  else {
    this->water_table_m = this->D - 1.9; //initial water table location 1.9 m deep, if not provided in the config file
    this->water_table_prev_m = new double[1];
    this->water_table_prev_m[0] = this->water_table_m;
  }

  //  for (int i=0; i < 4; i++)
  //  std::cout<<"Z: "<<this->Z[i]<<"\n";
  // check if the size of the input data is consistent
  assert (this->nz >0);
  
}


std::vector<double> smc_profile::SMCProfile::
ReadVectorData(std::string key)
{
  int pos =0;
  std::string delimiter = ",";
  std::vector<double> value(0);
  std::string z1 = key;

  while (z1.find(delimiter) != std::string::npos) {
    pos = z1.find(delimiter);
    std::string z_v = z1.substr(0, pos);

    value.push_back(stod(z_v.c_str()));

    z1.erase(0, pos + delimiter.length());
    if (z1.find(delimiter) == std::string::npos)
      value.push_back(stod(z1));
  }

  return value;
}


void smc_profile::SMCProfile::
SetLayerThickness() {
  
  const int n_z = this->shape[0];

  Dz[0] = Z[0];
  for (int i=0; i<n_z-1;i++) {
    Dz[i+1] = Z[i+1] - Z[i];
  }
}


// given bulk soil moisture quantity, distribute vertically
void smc_profile::SMCProfile::
SoilMoistureVerticalProfile()
{
  double lam=1.0/this->bexp; // pore distribution index
  double hb=this->satpsi * 100.; //7.82;  //[cm] //soil_res->hp;     
  double D= this->D * 100.;
  double z1= *this->water_table_prev_m * 100; //previous water table location, [cm]
  //double z0=0;        /* bottom of computational domain */
  double Vmax=D* this->smcmax;
  double beta=1.0-lam;
  double alpha=pow(hb,lam)/beta;
  double tol=0.000001;
  double phi = this->smcmax;
  double V1 = 100.0 * (*this->storage_m - *this->storage_change_m);  //change in soil moisture
  //  std::cout<<"water table: "<<*this->water_table_prev_m<<"\n";
  //double Vinit=V1;
  double V2= 100.0 * (*this->storage_m);  /* start-up condition before adding any water */

  int count = 0;
  
  if(V2>=Vmax) {
    for(int j=0;j<this->nz;j++)
      this->SMCT[j] = phi;
    return;
  }
   
   double diff=1000.0;

   double f, z2, z2new, df_dz2;

   z2=z1;  /* first guess, use Newton-Raphson to find new Z2 */
   do {
     count++;
    
     if(count>15000) {
       throw std::runtime_error("No convergence loop count: after 15000 iterations!");
     }
     
     f=phi*(z2-z1) + alpha * phi * (std::pow((D-z2),beta)-std::pow((D-z1),beta)) - (V2-V1);

     df_dz2=phi - alpha*phi*beta*std::pow((D-z2),(beta-1.0));
     
     z2new=z2-f/df_dz2*1.0;
     
     diff=z2new-z2;

     z2=z2new;     
     
   } while (std::fabs(diff)>tol);
   
   z1=z2;  // reset to new water table elevation value
   *this->water_table_prev_m = z1/100.;
   //   std::cout<<"storage change: "<<*this->storage_change_m<<" "<<z1<<" "<<*this->water_table_prev_m <<"\n";
   /* get a high resolution curve */
   int z_hres = 1001;
   double *smct_temp = new double[z_hres];
   double *z_temp = new double[z_hres];
   double dz1 = hb;
   double dz2 = this->Z[this->nz-1]*100.0 - z1;
   
   for (int i=0;i<z_hres;i++) {
     smct_temp[i] = std::pow((hb/dz1),lam)*phi;
     z_temp[i] = z1  + dz1;
     dz1 += dz2/(z_hres-1);
   }
   
   // mapping the updated soil moisture curve to the heat conduction discretization depth (Dz)
   for (int i=0; i<this->nz; i++) {
     for (int j=0; j<z_hres; j++) {
       if (z_temp[j]  >= (D - this->Z[i]*100) ) {
	 this->SMCT[i] = smct_temp[j];
	 break;
       }
     }
   }
   //std::cout<<"SMC: storage = "<< *this->storage_m <<"\n";
   //   for (int i=0; i<this->nz; i++)
   //std::cout<<"SMC = "<<this->SMCT[i]<<"\n ";
}


smc_profile::SMCProfile::
~SMCProfile()
{}

#endif

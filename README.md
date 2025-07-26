# Soil Freeze-Thaw Model for Permeable Pavements

> **Note:** This repository is a fork of the official [NOAA-OWP/SoilFreezeThaw](https://github.com/NOAA-OWP/SoilFreezeThaw) model, specifically adapted to support the findings of the publication listed below.

This version of the Soil Freeze-Thaw (SFT) model has been modified and configured to simulate the thermal dynamics of permeable pavement systems under freeze-thaw conditions. The work was conducted as part of a study using unique field data from a permeable pavement test site in Aalborg, Denmark.

The implementation adapts the model's **"pseudo framework mode"**, coupling the SFT physics engine with a custom soil moisture component. This component uses observed water table data from the field site to empirically determine the vertical moisture profiles needed as input for the thermal simulations.

## Associated Publication

The code and data in this repository were used to produce the results presented in the following paper:

**Title:** Thermal Behavior of Permeable Pavements under Freeze-Thaw Conditions  
**Authors:** Dansani Vasanthan Muttuvelu, Lasse Hedegaard Hansen, Ahmad Jan Khattak, and Jes Vollertsen  
**Journal:** *Preprint submitted to Elsevier* (or update with final journal information)  
**Link:** [Link to your preprint or final paper]

## Contents of this Repository

This repository contains:
*   The modified SFT model source code.
*   The specific forcing data from the Aalborg test site used for the simulations presented in the paper.
*   The configuration files required to reproduce the paper's results.

## How to Use This Repository

This repository is primarily intended to provide the code and data necessary to reproduce the results presented in the associated publication.

1.  **Build the Model:** For general build instructions, please refer to the original [`INSTALL.md`](https://github.com/NOAA-OWP/SoilFreezeThaw/blob/master/INSTALL.md) file. This project specifically uses the **pseudo framework mode**, so you will need to use the `-DPFRAMEWORK=ON` flag during the `cmake` step.
2.  **Forcing Data:** The forcing data for the Aalborg test site can be found in the `forcings/` directory.
3.  **Configuration:** The model configuration files used for the calibrated simulations and sensitivity analyses are located in the `configs/` directory.

## Original Model Documentation

For general documentation, information on other run modes (standalone, nextgen), and to report issues with the core model, please refer to the official **[NOAA-OWP/SoilFreezeThaw repository](https://github.com/NOAA-OWP/SoilFreezeThaw)**.

## Citation

If you use this code or data in your research, please cite our paper:

```bibtex
@article{Muttuvelu2024,
  title   = {Thermal Behavior of Permeable Pavements under Freeze-Thaw Conditions},
  author  = {Muttuvelu, Dansani Vasanthan and Hansen, Lasse Hedegaard and Khattak, Ahmad Jan and Vollertsen, Jes},
  journal = {Preprint submitted to Elsevier},
  year    = {2024}
}
```

## Acknowledgments

This work builds directly upon the excellent modeling framework developed by the NOAA Office of Water Prediction (OWP). We thank the original developers for making their code publicly available.

## License

This software is licensed under the same terms as the original [NOAA-OWP/SoilFreezeThaw](https://github.com/NOAA-OWP/SoilFreezeThaw) repository.

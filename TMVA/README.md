# $tHq$ (2$\ell$ SS +$\tau_{had}$) - Lepton Origin Assignment

ML-based tool based on TMVA library of ROOT to determine the parent particle of the light leptons in the  $tHq$ (2$\ell$ SS +$\tau_{\text{had}}$) search.


# Contentent

  - scripts
      - `LeptonAssignmentTools.py`: Collection of classes and functions.
      - `TMVA_LeptonAssignment_Training.py` : Training of a gradient BDT with k-folding cross-validation.
      - `LepAssignment_config.config`: Configuration file to manage the training process.
      - `TMVA_CompareFolds.py`: Draw roc curves of each model and plots them together.
      - `TMVA_DeltaRCone_Study.py`: Plots the distribution of $\Delta R$ cone to match reconstruction-level and truth-level light leptons.
      - `TMVA_LeptonAssignment_Optimisation.py`: Optimisation of hyperparameters. 
  - simplified_code
      - `TMVA_LeptonAssignment.py`: Light version of the script.
      - `LepAssignment_Redux.config`: Configures training.
      - `TMVA_DrawCurvesROC.py`
- data: Data samples used for the training.

# Usage

Use python3. The training is configured via an external configuration file (`LepAssignment_config.config`).
Do:
 `python3 TMVA_LeptonAssignment.py -d 0 `
 The option `-d` sets the debug level of the prints.


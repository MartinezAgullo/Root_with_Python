This set of scripts was developed for the validation of truth information, new variables definition and plot production.

The main script of these plotting macros is `4TruthHistos.py`, which is used as both the skeleton for the macros and the script where the new variables are defined. It loops over all events in the truth and in each iteration it fills the histograms of interest. 
As auxiliary scripts we have:
-  `ToolsForTruth.py`: Contains several funcions and tools for generating the plots to be later used by `4TruthHistos.py`
-  `ConfigFile.py` : The branches of the truth tree to be used as well as the details of the 1D histograms are specified here. This scripts reads the `config.yaml` for setting the cuts and has the functions to access the NTuples with rucio. 
-  `MsgHelper.py`: Display the prints of the code using the ATLAS style. Let us select the debug level.
-  `merge_plots.py`: Merge the different plots produced in `4TruthHistos.py`. These plots are the plots to include in the internal note.

Perform basic plots: `python 4TruthHistos.py -i /lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/TopPartons_Output/user.martinpa.mc16_13TeV.346676.aMCPy8EG_tHjb125_4fl_CPalpha_0.SGTOP1.e7815_a875_r10724_p4174.ll.v31.test0_taus_out.root `


The cuts are configured in the `config.yaml`. There we can set the minimum and maximum values for pt and eta for the tau and the light leptons.

Options

- -d :: Debug level - Select which information to print
- -i :: Set input file or directory
- -c :: Set the configuration file to use. By default it takes the config.taml in the directory
- -f :: Maximum number of files to be processed
- -e :: Maximum number of events to be processed 
- -s :: Show stat box in the final plots
- --outputformat :: Set output format of plots, by fault its saved in: png, pdf and root
- --interactive :: Run the macros inteactively (note that this takes much more time)




# Set up
```
kinit martinpa@CERN.CH
aklog CERN.CH
export RUCIO_ACCOUNT=martinpa
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
alias setupATLAS='source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh'
setupATLAS
lsetup "asetup AnalysisBase,21.2.143,here" git pyami panda
lsetup "rucio 1.21.11.patch1"
```

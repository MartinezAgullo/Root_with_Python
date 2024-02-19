import os,sys
import ROOT

########################################################################
#     Script to check if the BDT socres have been properly sotred.     #
#     It reads all the samples and checks that the mean score has a    # 
#     standard deviation different than zero.                          # 
########################################################################

########## 
# main
########## 
def main():
    # Specify the root folder to start the search
    samples_folder = "/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/EBreview_v34_dilepOStau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV_BDT_tHq_ttbar/"
    output_file_tHq = "Problematic_samples_bdt_tHq.txt"
    output_file_ttbar = "Problematic_samples_bdt_ttbar.txt"

    print("Open "+str(output_file_tHq)+" and "+str(output_file_ttbar))
    with open(output_file_tHq, 'w') as f1, open(output_file_ttbar, 'w') as f2:
        # Recursively search for subfolders
        print("Looping over all root samples...")
        print("[Looking for RMS = 0]")
        for systematic in os.listdir(samples_folder):
            systematic_path = os.path.join(samples_folder, systematic)
            for file_name in os.listdir(systematic_path):
                if file_name.endswith(".root"):
                    sample_path = os.path.join(systematic_path, file_name)
                    tree_name = treeNamer(systematic, file_name)
                    GoodInjection_bdt_tHq, GoodInjection_bdt_ttbar = calculate_mean(sample_path, tree_name)
                    if GoodInjection_bdt_tHq == False:
                        f1.write(sample_path + '\n') #Problematic_samples_bdt_tHq.txt
                    if GoodInjection_bdt_ttbar == False:
                        f2.write(sample_path + '\n') #Problematic_samples_bdt_ttbar.txt
                    if GoodInjection_bdt_ttbar == False or GoodInjection_bdt_tHq== False: print("!!!!!!!!!! MALO !!!!!!!!!!")
    print("File paths have been stored in", output_file_tHq, "and", output_file_ttbar)

                    
    
##########
# calculate_mean(): Calculates the mean and std of the bdt_tHq and bdt_ttbar for each process and systematic.
#                   The bdts to test have to be hardcoded. 
##########
def calculate_mean(file_path, tree_name):
    #print("Reading :: " + str(file_path))
    #print("Tree :: "+str(tree_name))

    GoodInjection_bdt_tHq = True
    GoodInjection_bdt_ttbar = True

    try:
        # Open the ROOT file and the TTree
        root_file = ROOT.TFile.Open(file_path)
        tree = root_file.Get(tree_name)
    
        temp_h1_tHq = ROOT.TH1F("BDT(tHq) Score", "BDT(tHq) Score", 100, 0, 1)
        temp_h1_ttbar = ROOT.TH1F("BDT(ttbar) Score", "BDT(ttbar) Score", 100, 0, 1)

        # Loop over the entries in the TTree
        for event in tree:
            temp_h1_tHq.Fill(event.bdt_tHq)
            temp_h1_ttbar.Fill(event.bdt_ttbar)
    except Exception as e:
        print("ERROR with: " + file_path)
        print(e)
        return False, False

        
    bdt_tHq_RMS = temp_h1_tHq.GetRMS() # Get Standard deviation
    bdt_tHq_mean = temp_h1_tHq.GetMean() # Get mean
    bdt_ttbar_RMS = temp_h1_ttbar.GetRMS()
    bdt_ttbar_mean = temp_h1_ttbar.GetMean()

    if bdt_tHq_RMS == 0.0:
        #print("Warning for "+file_path+": The bdt_tHq was not stored properly. BDT(tHq) = "+str(bdt_tHq_mean) +" \pm "+str(bdt_tHq_RMS))
        GoodInjection_bdt_tHq = False
    if bdt_ttbar_RMS == 0.0:
        #print("Warning for "+file_path+": The bdt_ttbar was not stored properly. BDT(ttbar) = "+str(bdt_ttbar_mean) +" \pm "+str(bdt_ttbar_RMS))
        GoodInjection_bdt_ttbar = False
    
    root_file.Close()
    
    return GoodInjection_bdt_tHq, GoodInjection_bdt_ttbar

########## 
# treeNamer(): The AFII samples have different tree names
########## 
def treeNamer(systName, processName):

    tree_name = "tHqLoop_" + systName
    if "AFII" in processName:
        if systName == "JET_PunchThrough_MC16__1up_Loose": tree_name = "tHqLoop_JET_PunchThrough_AFII__1up_Loose"
        if systName == "JET_PunchThrough_MC16__1down_Loose": tree_name = "tHqLoop_JET_PunchThrough_AFII__1down_Loose"
        if systName == "JET_JER_DataVsMC_MC16__1up_PseudoData_Loose": tree_name = "tHqLoop_JET_JER_DataVsMC_AFII__1up_PseudoData_Loose"
        if systName == "JET_JER_DataVsMC_MC16__1down_PseudoData_Loose": tree_name = "tHqLoop_JET_JER_DataVsMC_AFII__1down_PseudoData_Loose"
        if systName == "JET_JER_DataVsMC_MC16__1up_Loose": tree_name = "tHqLoop_JET_JER_DataVsMC_AFII__1up_Loose"
        if systName == "JET_JER_DataVsMC_MC16__1down_Loose": tree_name = "tHqLoop_JET_JER_DataVsMC_AFII__1down_Loose"

    if systName == "alternative_sample": tree_name = "tHqLoop_nominal_Loose"
   # if systName == "alternative_sample" and "AFII" in processName: tree_name = "tHqLoop_nominal_Loose"
    return tree_name

if __name__ == '__main__':
  main()

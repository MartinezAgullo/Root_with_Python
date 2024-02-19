import os

# Check if there is any AFII sample missing. 
# Very often I forget to inject the BDT scores in these

directory_path = '/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/EBreview_v34_dilepOStau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV_BDT_tHq_ttbar/'
#directory_path = '/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/EBreview_v34_dilepSStau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV_BDT_tHq/'

print("Reading "+str(directory_path))
for folder_name in os.listdir(directory_path):
    folder_path = os.path.join(directory_path, folder_name)
    
    if folder_name == 'alternative_sample': continue
    
    # Check if the item is a directory
    if os.path.isdir(folder_path):
        # Count files with 'AFII' in the name within the directory
        afii_files = [file for file in os.listdir(folder_path) if "AFII" in file]
        afii_file_count = len(afii_files)
        
        # If such files are found, print the folder name and the count
        if afii_file_count > 0:
            print(" - "+str(afii_file_count) +" file(s) with 'AFII' in their name found on "+str(folder_name)+" ")

        else:
            print(" - WARNING: Directory "+str(folder_name)+" does not  contain AFII samples!!!!!!")

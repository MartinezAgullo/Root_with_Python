
#############################################
#  CountFiles.py
#   Check if there are the same number of subdirectories in 
#   two paths. Used to make sure that the BDT scores have
#   been injected in all systematics.
#   Usage: python CountFiles.py -c
#          python CountFiles.py -f -m
import os
import re
from optparse import OptionParser

def main():
    parser = OptionParser(usage="usage: %prog [options]")
    
    parser.add_option("-c", "--check-subdir-count",
                      action="store_true", dest="check_subdir", default=False,
                      help="Check if dir_A and dir_B have the same number of subdirectories. To check if an entire systematic was lost during the injecton of the BDT score.")
    
    parser.add_option("-f", "--compare-file-counts",
                      action="store_true", dest="compare_files", default=False,
                      help="Compare the file counts between all systematics in dir_A and dir_B. To check for each systematic if a sample was lost during the injection of the BDT score")
    parser.add_option("-m", "--find-missing-files", dest="find_missing_files", default=False,
                      action="store_true",
                      help="Search which files are missing withing NotCompleteSyst.txt list")
    parser.add_option("-a", "--alternative", dest="alternative", default=False,
                      action="store_true",
                      help="Checks that there are no mising alternative samples")

    (options, args) = parser.parse_args()
    

    basedir = "/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/"
    #dir_A = os.path.join(basedir, "NewSamples_FromBonnOS_Valencia_Structure_BDT_tHq/")
    dir_A = os.path.join(basedir, "EBreview_v34_dilepOStau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV_BDT_tHq_ttbar/")
    dir_B = os.path.join(basedir, "EBreview_v34_dilepOStau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV_BDT_tHq/")
    
    if options.check_subdir:
        check_subdir_count(dir_A, dir_B)
    if options.compare_files:
        compare_directory_file_counts(dir_A, dir_B)
    if options.find_missing_files:
        check_missing_files(dir_A, dir_B)
    if options.alternative:
        check_alternative_samples()
    else:
        print "Please choose an option. Use -h for help."

####
# get_all_subdirs_with_file_count() :: Creates a dictionary
# with and entry per syst folder and where the enties are "folder:numFiles"
####
def get_all_subdirs_with_file_count(generic_dir):
    dir_count_map = {}
    
    for root, dirs, files in os.walk(generic_dir):
        if 'samples_merged' in dirs:
            dirs.remove('samples_merged')  
        relative_root = os.path.relpath(root, generic_dir)
        dir_count_map[relative_root] = len(files)
    return dir_count_map


#####
# compare_directory_file_counts() :: Checks that all directories
# have the same amount of files than its correspondent directory
#####
def compare_directory_file_counts(dir_A, dir_B):
    print("Comparing:")
    print dir_A
    print dir_B
    dir_A_counts = get_all_subdirs_with_file_count(dir_A)
    dir_B_counts = get_all_subdirs_with_file_count(dir_B)

    filename = "NotCompleteSyst.txt"
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, "w") as file:
        for subdir, count_A in dir_A_counts.items():
            count_B = dir_B_counts.get(subdir, None)
        
            if count_B is None:
                print("Subdirectory "+str(subdir)+" was not found in "+str(dir_B))
                continue

            if count_A != count_B:
                print("Subdirectory "+str(subdir)+" has different file counts: "+str(dir_A)+" ("+str(count_A)+" files) vs "+str(dir_B)+" ("+str(count_B)+" files)")
                file.write(subdir + "\n")

#######
# For the systematic folders with diferent number of files, this funciton
# indetifies the files that have been lost when injecting the scores
#####
def check_missing_files(dir_A, dir_B, filename="NotCompleteSyst.txt"):
    try:
        with open(filename, "r") as file:
            subdirs = file.read().splitlines()


        missing_DSIDs =[]
        for syst in subdirs:
            dir_systA = os.path.join(dir_A, syst)
            dir_systB = os.path.join(dir_B, syst)

            files_A = set(os.listdir(dir_systA))
            files_B = set(os.listdir(dir_systB))

            missing_files = files_A - files_B

            if missing_files:
                print("Files present in "+str(dir_systA)+" but missing in "+str(dir_systB)+" ") 
                for file in missing_files:
                    print(file)
                    match = re.search(r'\.(\d+)\.', file)
                    if match:
                        dsid = match.group(1)
                        missing_DSIDs.append(dsid)
                    
            else:
                print("All files in "+str(dir_systA)+" are present in "+str(dir_systB)+" ")

        print("\n")
        missing_DSIDs_final = []
        for item in missing_DSIDs:
            if item not in missing_DSIDs_final:
                missing_DSIDs_final.append(item)
        print("Missing DSIDs: ")
        print(missing_DSIDs_final)

    except FileNotFoundError:
        print("File "+str(filename)+" not found.")
    except Exception as e:
        print("An error occurred: "+str(e))



#####
# check_subdir_count() :: ecks if dir_A and dir_B have the same number 
# of subdirectories. If not, prints which are missing.
#####
def check_subdir_count(dir_A, dir_B):
    print("Comparing:")
    print dir_A
    print dir_B
    dir_A_subdirs = list(get_all_subdirs_with_file_count(dir_A).keys())
    dir_B_subdirs = list(get_all_subdirs_with_file_count(dir_B).keys())

    # Check folders missing in dir_B
    missing_in_B = set(dir_A_subdirs) - set(dir_B_subdirs)
    if missing_in_B:
        print("Folders present in "+str(dir_A)+" but missing in "+str(dir_B)+":")
        for d in missing_in_B:
            print "{}".format(d)

    # Check folders missing in dir_A
    missing_in_A = set(dir_B_subdirs) - set(dir_A_subdirs)
    if missing_in_A:
        print("Folders present in "+str(dir_B)+" but missing in "+str(dir_A)+":")
        for d in missing_in_A:
            print "{}".format(d)

    if not missing_in_A and not missing_in_B:
        print("Both directories have the same number of folders and the same folder names.")



def check_alternative_samples():
    dir_Original = "/lustre/ific.uv.es/grid/atlas/t3/cescobar/tHq_analysis/13TeV/EBreview_v34_2L1tau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV/"
    dir_Injected = "/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/EBreview_v34_dilepOStau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV_BDT_tHq_ttbar/"
    #dir_Injected = "/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/EBreview_v34_dilepOStau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV_BDT_tHq/"
    dir_Injected = "/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/EBreview_v34_dilepSStau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV_BDT_tHq/"

    # List of filenames in each directory
    files_in_A = os.listdir(os.path.join(dir_Original,'alternative_sample'))
    files_in_B = os.listdir(os.path.join(dir_Injected,'alternative_sample'))

    print("Number of alternative samples (original):       \t"+str(len(files_in_A)))
    print("Number of alternative samples (after injection):\t"+str(len(files_in_B)))
    # Find files present in A but not in B
    files_not_in_B = [file for file in files_in_A if file not in files_in_B]
    print("List of the "+str(len(files_not_in_B))+" missing alternative samples in "+str(dir_Injected))
    for missing in files_not_in_B:
        print(missing)




###
# Execute main
###
if __name__ == "__main__":
   main()

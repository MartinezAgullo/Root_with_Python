#####################################################################
#     Script to adapt the directory structure of the Bonn NTuples   # 
#     to the one used in Valencia.                                  #
#####################################################################

import os


def main():
    ListOfSytematicFolders = "/lhome/ific/p/pamarag/Work/New_BDT/tHqIFIC/tHqMVA/ListOfSystematics_full.txt"
    target_directory = "/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/dilepSStau_2024/"
    folder_names = create_folders_from_txt(ListOfSytematicFolders, target_directory)

    origin_dir = "/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/NewSamples_2024/treeSyst_SS/"
    os.chdir(origin_dir)
    
    # Systematic trees
    create_symlinks_systTrees(origin_dir, target_directory, folder_names)
    
    #nominal samples
    create_symlinks_nominal("/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/NewSamples_2024/nominal_SS/", target_directory, "nominal_Loose")
    
    #Alternative samples
    create_symlinks_nominal("/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/NewSamples_2024/model_SS/", target_directory, "alternative_sample")

    print("Done")



# Creates the directories for the tree based systematics
def create_folders_from_txt(input_file, target_directory):
    print("Creating new directories")
    with open(input_file, 'r') as file:
        folder_names = [line.strip() for line in file.readlines() if line.strip()]

    for folder_name in folder_names:
        folder_path = os.path.join(target_directory, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        else:
            print("Folder "+str(folder_path)+" already exists.")

    return folder_names

# Create the symlinks to the files copied from Bonn site
# in a way that it has our directory structure, i. e.
# each tree-based systematic is in a dedicated directory 
def create_symlinks_systTrees(tree_based_directory, target_directory, folder_names):
    print("Creating sylinks")
    for file_name in os.listdir(tree_based_directory):
        file_path = os.path.join(tree_based_directory, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.root'):
            for folder_name in folder_names:
                if folder_name in file_name:
                    folder_path = os.path.join(target_directory, folder_name)
                    symlink_path = os.path.join(folder_path, file_name)
                    if os.path.exists(symlink_path):
                        continue
                        #os.remove(symlink_path) # The script may not have the permision to delete symlinks
                    try:
                        os.symlink(file_path, symlink_path)
                        print("Created symlink: "+str(symlink_path))
                    except OSError as e:
                        print("Failed to create symlink: "+str(symlink_path))
                        print("Error: "+str(e))
                else:
                    if "AFII" in file_name: # The name of the systematic is modified in AFII samples
                        compatible_file_name = file_name.replace('AFII','MC16') # The name of the sys is with MC16
                        if folder_name in compatible_file_name:
                            folder_path = os.path.join(target_directory, folder_name)
                            symlink_path = os.path.join(folder_path, file_name)
                            try:
                                os.symlink(file_path, symlink_path)
                                print("Created symlink for the AFII sample: "+str(symlink_path))
                            except OSError as e:
                                print("Failed to create symlink: "+str(symlink_path))
                                print("Error: "+str(e))

# Create softlinks for systematic and alternative samples
def create_symlinks_nominal(source_directory, target_directory_base, target_folder):
    print("Creating symlinks for "+str(target_folder))
    target_directory = os.path.join(target_directory_base, target_folder)
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    else:
         print("Folder "+str(target_directory)+" already exists.")

    for file_name in os.listdir(source_directory):
        file_path = os.path.join(source_directory, file_name)
        if os.path.isfile(file_path):
            symlink_path = os.path.join(target_directory, file_name)
            if os.path.exists(symlink_path):
                os.remove(symlink_path)
            try:
                os.symlink(file_path, symlink_path)
                print("Created symlink: "+str(symlink_path))
            except OSError as e:
                print("Failed to create symlink: "+str(symlink_path))
                print("Error: "+str(e))


if __name__ == "__main__":
    main()

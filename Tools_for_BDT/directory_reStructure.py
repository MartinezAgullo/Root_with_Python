import os,sys
# Script to adapt the directory structure from the tHqLoop output to that used for the fit
# Symlink_creator <- Creates the new structure with symlinks
# Checker <- Compare the number of files to check that none has been lost

def main(argv): 
    path_of_NTuples = '/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/EBreview_v34_2L1tau_PLIV_SFs_syst_nonBDTassignment_lep3_pt_min14GeV_tZqNew_OS_BDT_tHq_ttbar_Zjets_tZq/'
    general_dir_new = '/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/2LOS1Tau_AllBDTscores/'

    systTree_dir_new = general_dir_new + '3l1tau_syst_tree/'
    systModel_dir_new = general_dir_new +'3l1tau_syst_model/'


    if True: Symlink_creator(path_of_NTuples, general_dir_new, systTree_dir_new, systModel_dir_new)
    if True: Checker(path_of_NTuples, general_dir_new, systTree_dir_new, systModel_dir_new)

def Symlink_creator(path_of_NTuples, general_dir_new, systTree_dir_new, systModel_dir_new):
    print("Symlink_creator")
    if not os.path.exists(path_of_NTuples):
        print("The given path of the NTuples does not exist")
        exit()

    if not os.path.exists(general_dir_new): os.makedirs(general_dir_new)
    if not os.path.exists(systTree_dir_new): os.makedirs(systTree_dir_new)
    if not os.path.exists(systModel_dir_new): os.makedirs(systModel_dir_new)


    for dirname in os.listdir(path_of_NTuples):
        if dirname == 'nominal_Loose':
            print(str(dirname) + ' are the nominal samples')
            src0 = os.path.join(path_of_NTuples, dirname)
            for root_file in os.listdir(src0):
                src = os.path.join(path_of_NTuples, dirname, root_file)
                dst = os.path.join(general_dir_new, root_file)
                if not os.path.isfile(dst):
                    os.symlink(src, dst)
                else:
                    print("The link for "+str(root_file)+" already exists")
                    print(dst)
                    print("\n")

        elif dirname == 'alternative_sample':
            print(str(dirname) + ' is modeling systematic')
            src1 = os.path.join(path_of_NTuples, dirname)
            for root_file in os.listdir(src1):
                src = os.path.join(path_of_NTuples, dirname, root_file)
                dst = os.path.join(systModel_dir_new, root_file)
                if not os.path.isfile(dst):
                    os.symlink(src, dst)
                
        else:
            src2 = os.path.join(path_of_NTuples, dirname)
            for root_file in os.listdir(src2):
                src = os.path.join(src2, root_file)
                dst = os.path.join(systTree_dir_new, str(dirname)+"_"+root_file)
                if os.path.islink(dst) == False:
                    os.symlink(src, dst)
                else:
                    print("Already exists")
                    print("src :: "+str(src))
                    print("dst :: "+str(dst))
                    exit()



    print("End of symlink_creator")



def Checker(path_of_NTuples, general_dir_new, systTree_dir_new, systModel_dir_new): # Check the number of symlinks created
    print("Checker")
    original_nominal = 0
    original_model = 0
    original_tree = 0
    new_nominal = 0
    new_model = 0
    new_tree = 0
    for folder in os.listdir(path_of_NTuples):
        if folder == 'nominal_Loose':
            for root_file in os.listdir(os.path.join(path_of_NTuples, folder)):
                if os.path.isfile(os.path.join(path_of_NTuples, folder, root_file)):
                    original_nominal +=1

        if folder == 'alternative_sample':
            for root_file in os.listdir(os.path.join(path_of_NTuples, folder)):
                if os.path.isfile(os.path.join(path_of_NTuples, folder, root_file)):
                    original_model +=1

        if folder not in ['nominal_Loose', 'alternative_sample']:
            for root_file in os.listdir(os.path.join(path_of_NTuples, folder)):
               if os.path.isfile(os.path.join(path_of_NTuples, folder, root_file)):
                    original_tree +=1      

                    
    for item in os.listdir(general_dir_new):
        if os.path.isfile(os.path.join(general_dir_new, item)): 
            new_nominal +=1
        if item == '3l1tau_syst_model':
            for root_file  in os.listdir(os.path.join(general_dir_new, item)):
                if os.path.isfile(os.path.join(general_dir_new, item, root_file)): new_model +=1
        if item == '3l1tau_syst_tree':
            for root_file  in os.listdir(os.path.join(general_dir_new, item)):
                if os.path.isfile(os.path.join(general_dir_new, item, root_file)): new_tree +=1

    print("# nominal files (original) :: " +str(original_nominal))
    print("# alternative sample files (original) :: " +str(original_model))
    print("# systematic trees files (original) :: " +str(original_tree))
    print("# nominal files (new) :: " +str(new_nominal))
    print("# alternative sample files (new) :: " +str(new_model))
    print("# systematic trees files (new) :: " +str(new_tree))

        
    


if __name__ == '__main__':
  main(sys.argv[1:])

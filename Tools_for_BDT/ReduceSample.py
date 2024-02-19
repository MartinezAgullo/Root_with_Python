import os,sys
import multiprocessing as mp
import array

from ROOT import TFile, TTree

from optparse import OptionParser

parser = OptionParser(usage = "usage: %prog arguments", version="%prog")

parser.add_option("-t", "--tree-name", dest="treeName",     help="set the tree name to process (default: %default)")
parser.add_option("-i", "--inputpudir",  dest="inputdir",    help="input directory (default: %default)")
parser.add_option("-o", "--ouput",dest= "output", help = "Folder for the ouput BDT (default: %default)")
parser.add_option("-m", "--method",dest= "method", help = "Method for open file (default: %default)")
parser.add_option("-r", "--reweight",dest= "reScale", help = "Re-scale weights to remove negative weights (default: %default)")

parser.set_defaults(treeName = 'tHqLoop_nominal_Loose', inputdir = '/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/v34_2l1HadTau_PLVTight_PreBDT_Selection/nominal_Loose/',output = '/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/v34_2l1HadTau_PLVTight_PreBDT_Selection_ReScaledWeights_2/nominal_Loose/',method = 'recreate', reScale = False)


(options,args) = parser.parse_args()

dir_path = options.inputdir
tree_t = options.treeName
dirName = options.output
reScale = options.reScale

reScale = True

aux_File_name = dir_path  
aux_tree_name = tree_t  #'tHqLoop_nominal_Loose'


bdt_tHq = []
bdt_ttbar = []

# ===========================
# GetMinWeight
# ===========================
def GetMinWeight(File,filename,tree, min_weight, max_weight):
    m_file = TFile.Open(File)
    m_tree = m_file.Get(tree)
    if m_tree.GetEntries()==0:
        m_file.Close()
        return min_weight, max_weight

    for event in m_tree:
        if event.weight_nominal < min_weight: min_weight = event.weight_nominal
        if event.weight_nominal > max_weight: max_weight = event.weight_nominal
    #print("min: " + str(min_weight)) #debug
    #print("max: " + str(max_weight)) #debug
    return min_weight, max_weight

# ===========================
# ReWeight: Re-Scale the weights to avoid negatively weighted events
# ===========================
def ReWeight(File,filename,tree, min_Weight, max_Weight):
    #print(File)
    m_file = TFile.Open(File)
    m_tree = m_file.Get(tree)
    if m_tree.GetEntries()==0:
        m_file.Close()
        return
    out_file = TFile(dirName+'/'+filename,options.method)
    new_tree = m_tree.CloneTree(0)

    for event in m_tree:
        if event.weight_nominal > max_Weight: 
            print("WARNING: Maximum not properly identified. ")
            print("   Max identified:      " + str(max_Weight))
            print("   Event weight found : " + str(event.weight_nominal))
        if event.weight_nominal < min_Weight: 
            print("WARNING: Minimum weight not properly identified")
            print("   Min identified:      " + str(min_Weight))
            print("   Event weight found : " + str(event.weight_nominal))
        event.weight_nominal = event.weight_nominal - min_Weight
        if event.weight_nominal < 0:
            print("WARNING: We have a negatively weighted event")
        new_tree.Fill()

    m_file.Close()
    out_file.Write()
    out_file.Close()


# ===========================
# Reduction: Introduce cuts to remove events from your sample
# ===========================
def Reduction(File,filename,tree):
    print(File)
    m_file = TFile.Open(File)
    m_tree = m_file.Get(tree)
    if m_tree.GetEntries()==0:
        m_file.Close()
        return

    out_file = TFile(dirName+'/'+filename,options.method)
    new_tree = m_tree.CloneTree(0)

    # APPLY YOU STUFF HERE    
    for event in m_tree:
        if (3 > event.m_nbjets > 0) and (0 < event.m_nNoBjets < 7): # 2L1HadTau preselection: n(b-jets) \in [1, 2] and n(light-jets) \in [1, 6]
            new_tree.Fill()
        else:
            if (dir_path == '/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/v34_2l1HadTau_PLVTight_NoSelection/nominal_Loose/'):
                print("WARNING: An event not matching the PreBDT requierements passed the selection")

    m_file.Close()
    out_file.Write()
    out_file.Close()

Thread = False  #To use python threading
if Thread : pool = mp.Pool(processes = 20)


if not os.path.exists(dirName):
    os.mkdir(dirName)

print aux_File_name

min_weight = 1
max_weight = 0
if reScale:
    for file in os.listdir(aux_File_name):
        file_path = dir_path + file
        min_weight, max_weight = GetMinWeight(file_path,file,tree_t, min_weight, max_weight)


    print("Re-scaling to avoid negative weights")
    print(" Original weight_nominal max:" + str(max_weight))
    print(" Original weight_nominal min:" + str(min_weight))
    print(" New weight_nominal max:" + str(max_weight - min_weight))
    print(" New weight_nominal min:" + str(min_weight - min_weight) + " <-- Should be 0") # 0


for file in os.listdir(aux_File_name):
    file_path = dir_path + file
    if Thread :
        pool.apply_async(Reduction,args=(file_path,file,tree_t,))
    else:
        if not reScale:
            Reduction(file_path,file,tree_t)
        else:
            ReWeight(file_path,file,tree_t, min_weight, max_weight)
if Thread :
    pool.close()
    pool.join()

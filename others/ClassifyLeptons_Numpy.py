import os,sys
from ROOT import TFile, TTree
import numpy as np
import pandas as pd
from root_numpy import tree2array
#from root_numpy import root2array
from root_numpy import testdata




def main(argv):
    # Load dataset, filter the required events and define the training variables                                                               
    filename = "lepton_assigment_output.root"
    filepath ="/lhome/ific/p/pamarag/Work/data/" + filename
    treename = "tHqLoop_nominal_Loose"

    inFile = TFile.Open(filepath, "READ")
    tree = inFile.Get(treename)
    
    #RootFile=testdata.get_filepath(filepath)
    Array=tree2array(tree) # Convert a TTree in a ROOT file into a NumPy structured array 
    
    





if __name__ == '__main__':
  main(sys.argv[1:])

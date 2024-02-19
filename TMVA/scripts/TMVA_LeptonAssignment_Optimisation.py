########################################################################
#                      Find optimal hyperparam                         #
########################################################################
import os,sys
try:
    import ROOT
except:
    print("import ROOT Failed")
    print("Version of Python used:: " +str(sys.version))
    exit()
import numpy as np
import configparser
import multiprocessing as mp
from optparse import OptionParser
import time

from LeptonAssignmentTools import tools, msgServer

# =================================================================================
#  main
# =================================================================================
def main(argv):
    parser = OptionParser()
    parser.add_option("-d", "--debugLevel", dest="debugLevel", default=1, type="int",
                      help="Set debug level (DEBUG=0, INFO=1, WARNING=2, ERROR=3, FATAL=4) [default: %default]", metavar="LEVEL")

    try:
        (options, args) = parser.parse_args()
    except:
        parser.print_help()
        exit()
    
    config = configparser.ConfigParser()
    config.read("LepAssignment_config.config")
    
    #global msg
    msg = msgServer('TMVA_LeptonAssignment.py', options.debugLevel)
    msg.printBold('Running TMVA_LeptonAssignment_Training.py')
    
    #filepath = "/Users/pablo/Desktop/tHq_Analysis/3-LeptonAssigment/Studies/SamplesDir/"
    filepath = "/Users/pablo/Desktop/tHq_Analysis/3-LeptonAssigment/Studies/new_TrainingSamples/"
    treeName = "tHqLoop_nominal_Loose"
    tree = tools.Loader(options.debugLevel,filepath, treeName)
    
    
    msg.printGreen("Running TMVA_Optimiser()")
    TMVA_Optimiser(options.debugLevel, config, tree) # Explore different TMVA methods



# =====================================================================
#  TMVA_Optimiser: To explore different TMVA methods appart from the Gradient BDT
# =====================================================================
def TMVA_Optimiser(debugLevel, config, tree):
    msg = msgServer('TMVA_Optimiser', debugLevel)
    start_time = time.time()
    NegativeWeightTreatment = config['MVA']['NegativeWeightTreatment']
    
    outfileName = str(config['output']['outfileName_optimisation'])
    outputFile = ROOT.TFile.Open(outfileName, "RECREATE")
    
    dataloader = ROOT.TMVA.DataLoader('dataset')
    variables_tmva = tools.getVars(config['Features']['variables_tmva'])
    variable_target = config['Features']['variable_target']
    
    msg.printDebug("Adding variables for the TMVA training")
    for var in variables_tmva:
        dataloader.AddVariable(var[0],var[1])
    dataloader.AddSpectator("eventNumber") # the eventNumber is used for the splitExpr
    dataloader.AddSpectator("weight_nominal")
    dataloader.AddSpectator("is_Lep1_from_TruthTop")
    
    msg.printDebug("Designatig is_Lep1_from_TruthTop = 1 as signal and is_Lep1_from_TruthTop=0 as background")
    
    tree_sig, tree_bkg = tools.cutCollection(debugLevel, tree)
    
    dataloader.AddSignalTree(tree_sig, 1.0)
    dataloader.SetSignalWeightExpression("weight_nominal")
    dataloader.AddBackgroundTree(tree_bkg, 1.0)
    dataloader.SetBackgroundWeightExpression("weight_nominal")

    
    dataloader.PrepareTrainingAndTestTree("", "",
                                    "nTrain_Signal=0:nTrain_Background=0:NormMode=NumEvents:!V")

   
    depth = config['MVA']['BDT_depth']
    shrink = config['MVA']['BDT_shrink']
    ntrees = config['MVA']['BDT_ntrees']
    ncuts = config['MVA']['BDT_ncuts']
    sizenode = config['MVA']['BDT_MinNodeSize']
    baggingFraction = config['MVA']['BDT_BaggedSampleFraction']
    
    
    factory = ROOT.TMVA.Factory("TMVAClassification", outputFile,"!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification")
    factory.BookMethod(dataloader, ROOT.TMVA.Types.kBDT, "BDTG","!H:!V:VarTransform=D,G:NTrees="+str(ntrees)+":BoostType=Grad:Shrinkage="+str(shrink)+":UseBaggedBoost:BaggedSampleFraction="+str(baggingFraction)+":nCuts="+str(ncuts)+":MaxDepth="+str(depth)+":NegWeightTreatment="+str(NegativeWeightTreatment))
    
    factory.OptimizeAllMethods("ROCIntegral","FitGA")
    #factory.OptimizeAllMethods("Separation","Minuit")
    #factory.OptimizeAllMethods("ROCIntegral","Scan")
    #factory.OptimizeAllMethods("ROCIntegral","GA")
    
    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()
    
    
    
    


   
    outputFile.Close()
    end_time = time.time()
    msg.printInfo("Optimising took : " + "{:.3f}".format((end_time - start_time)) + " seconds")
    msg.printInfo("\t root")
    msg.printInfo("\t TMVA::TMVAGui(\""+str(outputFile.GetName())+"\")")

    

            


# ==========
# main
# ========
if __name__ == '__main__':
  main(sys.argv[1:])


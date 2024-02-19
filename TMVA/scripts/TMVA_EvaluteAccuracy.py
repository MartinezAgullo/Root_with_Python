###############################################################
#       Takes the output of tHqLoop and evaluates the         #
#       accuracy of the lepton-assignment model.              #
###############################################################
import os,sys
try:
    import ROOT
except:
    print("import ROOT Failed")
    print("Version of Python used:: " +str(sys.version))
    exit()
import array
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
    #parser.add_option("-s", "--stats", dest="stats", default=False, action='store_true', help="Print some metrics (no training)")
    try:
        (options, args) = parser.parse_args()
    except:
        parser.print_help()
        exit()
    msg = msgServer('TMVA_LeptonAssignment.py', options.debugLevel)
    config = configparser.ConfigParser()
    config.read("LepAssignment_config.config")
    
    #filepath = "/Users/pablo/Desktop/Tests_for_BDT_LepOrigin/mejor/ResultOfImplementation_tHqLoopOutput/"
    #filepath = "/Users/pablo/Desktop/tHq_Analysis/3-LeptonAssigment/Studies/OldAssignmentApplied_samples/" #<--- Best accuracy so far
    #filepath = "/Users/pablo/Desktop/tHq_Analysis/3-LeptonAssigment/Studies/FivefoldsNewModel_SamplesWithScore/"
    #filepath = "/Users/pablo/Desktop/tHq_Analysis/3-LeptonAssigment/Studies/StoredScores/FivefoldsNewModel_SamplesWithScore_No_Hvis2/"
    #filepath = "/Users/pablo/Desktop/Tests_for_BDT_LepOrigin/Model_02_02_I/Samples/"
    #filepath = "/Users/pablo/Desktop/Tests_for_BDT_LepOrigin/Model_02_03_i/Samples_withScore_fromtHqloop/" #<--- Best model so far
    #filepath = "/Users/pablo/Desktop/Tests_for_BDT_LepOrigin/Model_02_07/Samples_withScore_fromtHqloop/"
    filepath = "/Users/pablo/Desktop/tHq_Analysis/2-LeptonAssigment/Studies/samples_2024/ScoreInjected/"
    #filepath = "/Users/pablo/Desktop/Tests_for_BDT_LepOrigin/Model_02_03_ii/Samples_withScore_fromtHqloop/"
    tree = "tHqLoop_nominal_Loose"
    baseline_samples = "/Users/pablo/Desktop/tHq_Analysis/3-LeptonAssigment/Studies/BaselineSamples/"
    baseline_samples = "/Users/pablo/Desktop/tHq_Analysis/2-LeptonAssigment/Studies/samples_2024/"
        
        
    RecoLevelTree = tools.Loader(options.debugLevel,filepath, tree)
    BaselineTree = tools.Loader(options.debugLevel,baseline_samples, tree)
    
    
    msg.printBlue("Evaluate the accuracy of the baseline model")
    tools.EvaluateBaselineAccuracy(0, BaselineTree)
    msg.printBlue("Evaluate the accuracy of BDT-based model")
    tools.EvaluateAccuracy(0, RecoLevelTree, -0.315)
    #exit()
    msg.printBlue("Evaluate the accuracy of the model depending on the cut value")
    cuts=[-0.45, -0.40, -0.35, -0.33, -0.32, -0.31, -0.30, -0.29, -0.28, -0.27, -0.25, -0.20, -0.15, -0.10, -0.05, 0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]
    accuracies = cuts.copy()
    i = 0
    for bdt_cut in cuts:
        #tools.EvaluateAccuracy(1, RecoLevelTree, bdt_cut)
        accuracies[i] = tools.EvaluateAccuracy(1, RecoLevelTree, bdt_cut)
        i = i+1
    #print(cuts)
    #print(accuracies)
        
    tools.giraffe()


# ==========
# main
# ========
if __name__ == '__main__':
  main(sys.argv[1:])


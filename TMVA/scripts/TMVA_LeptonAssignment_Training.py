########################################################################
#       Training of a gradient BDT with k-folding for the              #
#       light-lepton origin assignment in the tHq(2lepSS+qtau)         #
#       The training is configured via an external configuration       #
#       file: LepAssignment_config.config                              #
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
    parser.add_option("-s", "--stats", dest="stats", default=False, action='store_true', help="Print some metrics (no training)")
    parser.add_option("-c", "--codeSnippet", dest="snippet", default=False, action='store_true', help="Print conde sinppet to contruct the tmva.reader for the applicaton phase (True/False)")
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
    
    if options.stats:
        tool.Stats(tree)
        #exit()
    
    msg.printGreen("Running TMVA_Runner()")
    TMVA_Runner(options.debugLevel, config, tree, options.snippet) # Explore different TMVA methods



# =====================================================================
#  TMVA_Runner: To explore different TMVA methods appart from the Gradient BDT
# =====================================================================
def TMVA_Runner(debugLevel, config, tree, produceSnippet):
    msg = msgServer('TMVA_Runner', debugLevel)
    start_time = time.time()
    NegativeWeightTreatment = config['MVA']['NegativeWeightTreatment']
    #IgnoreNegWeightsInTraining, Pray, WeightsInverseBoostNegWeights, PairNegWeightsGlobal
    
    #Create a ROOT output file where TMVA will store ntuples, histograms, etc
    outfileName = str(config['output']['outfileName'])
    outputFile = ROOT.TFile.Open(outfileName, "RECREATE")
    
    msg.printDebug("Formating the dataloader")
    dataloader = ROOT.TMVA.DataLoader('dataset')
    msg.printDebug("Reading config for variables")
    variables_tmva = tools.getVars(config['Features']['variables_tmva'])
    variable_target = config['Features']['variable_target']
    
    msg.printDebug("Adding variables for the TMVA training")
    for var in variables_tmva:
        #print("    float "+ str(var[0])+";")
        #print("    Float_t "+str(var[0])+", "+str(var[0])+";")
        #print('reader->AddVariable( "'+str(var[0])+'", &'+str(var[0])+');') #snippet for thqloop
        #print("float "+str(var[0])+";")
        dataloader.AddVariable(var[0],var[1])
        #msg.printBlue(str(var[0]) + ", " +str(var[1]))
    dataloader.AddSpectator("eventNumber") # the eventNumber is used for the splitExpr
    dataloader.AddSpectator("weight_nominal")
    dataloader.AddSpectator("is_Lep1_from_TruthTop")
    msg.printDebug("Addig is_Lep1_from_TruthTop and  weight_nominal as spectator to later use them in TMVA_CompareFolds.py")
    #dataloader.AddSpectator("phi_lep1")
    
    if produceSnippet:
        msg.printBlue("Snipet of code for TMVA_LeptonAssignment_Application.py")
        for var in variables_tmva:print("    var_"+str(var[0])+" = array.array('f',[0])")
        print("    var_eventNumber = array.array('f',[0])")
        print("    var_weight_nominal = array.array('f',[0]) ")
        print("    var_is_Lep1_from_TruthTop = array.array('f',[0]) \n")
        for var in variables_tmva: print("    reader.AddVariable(\""+str(var[0])+"\", var_"+str(var[0])+")")
        print("    reader.AddSpectator(\"eventNumber\", var_eventNumber)")
        print("    reader.AddSpectator(\"weight_nominal\", var_weight_nominal)")
        print("    reader.AddSpectator(\"is_Lep1_from_TruthTop\", var_is_Lep1_from_TruthTop) \n")
        print("    weightFileDir =  \"/Users/pablo/Desktop/tHq_Analysis/3-LeptonAssigment/Script/dataset/weights/TMVACrossValidation_BDTG.weights.xml\" ")
        
    msg.printDebug("Designatig is_Lep1_from_TruthTop = 1 as signal and is_Lep1_from_TruthTop=0 as background")
        
    useOS = bool(config['input']['train_with_OS'])
    print(useOS)
    useOS = False
    if useOS == True:
        print("test")
        msg.printBlue("Training with SS + OS")
        tree_sig, tree_bkg = tools.cutCollectionAll(debugLevel, tree)
    elif useOS == False:
        msg.printBlue("Training with SS only")
        tree_sig, tree_bkg = tools.cutCollection(debugLevel, tree)
    else:
        msg.printFatal("exit")
        exit()
        
    
    dataloader.AddSignalTree(tree_sig, 1.0)
    dataloader.SetSignalWeightExpression("weight_nominal")
    dataloader.AddBackgroundTree(tree_bkg, 1.0)
    dataloader.SetBackgroundWeightExpression("weight_nominal")

    
    dataloader.PrepareTrainingAndTestTree("", "",
                                    "nTrain_Signal=0:nTrain_Background=0:NormMode=NumEvents:!V")
    # - nTrain_Signal andnTrain_Background allow us to assign the number of events used for training.
    #   A value of 0 is a special value and would split the 50%/50%
    # - Independently from what is chosen in the "PrepareTrainingAndTestTree", the cross-validation
    #   uses a separate splitting mechanism.



    depth = config['MVA']['BDT_depth']
    shrink = config['MVA']['BDT_shrink']
    ntrees = config['MVA']['BDT_ntrees']
    ncuts = config['MVA']['BDT_ncuts']
    sizenode = config['MVA']['BDT_MinNodeSize']
    baggingFraction = config['MVA']['BDT_BaggedSampleFraction']
    
    
    msg.printGreen("BDT configuration")
    msg.printGreen(" - depth : " + str(depth))
    msg.printGreen(" - shrink : " + str(shrink))
    msg.printGreen(" - ntrees : " +str(ntrees))
    msg.printGreen(" - ncuts : " + str(ncuts))
    msg.printGreen(" - NegativeWeightTreatment : " + str(NegativeWeightTreatment))
    msg.printGreen(" - MinNodeSize : " + str(sizenode)+"%")
    msg.printGreen(" - BaggedSampleFraction : " + str(baggingFraction))

    numFolds = config['MVA']['numFolds']
    msg.printGreen(" - NumFolds : " + str(numFolds))
    FoldFileOutput = config['MVA']['FoldFileOutput']    # Stores a TMVA output for each fold. Set it to True just
                                                            # for testing the overtraining in cross validation.
        
    msg.printDebug("Preparing kFolding with "+str(numFolds)+" folds")
    # Random splitting is the default mode if no SplitExpr is especified to the CrossValidation constructor
    # If you want to run TMVACrossValidationApplication, make sure you have
    # run this tutorial with Deterministic splitting type, i.e.
    # with the option useRandomSPlitting = false
    # https://root.cern/doc/master/TMVACrossValidation_8C.html
    
    #For data application functional splitting is preferred
    splitType = "Deterministic"#(useRandomSplitting) ? "Random" : "Deterministic"
    #splitExpr = "int([eventNumber])\ "+ str(numFolds) #(!useRandomSplitting) ? "int(fabs([eventID]))%int([NumFolds])" : ""
    splitExpr = "int(fabs([eventNumber]))%int([numFolds])"
    #splitExpr = "int([eventNumber])%int([NumFolds])"
    #splitExpr = "fabs([phi_lep1]+0.1)/int([numFolds])"
        
    if splitType == "Deterministic":
        msg.printInfo("The split expression used is '" +str(splitExpr)+"' with numFolds = " + str(numFolds))
    else:
        msg.printInfo("Using random sppliting")

    cvOptions="!V:!Silent:ModelPersistence:AnalysisType=Classification:SplitType="+str(splitType)+":NumFolds="+str(numFolds)+":SplitExpr="+str(splitExpr)+":FoldFileOutput="+str(FoldFileOutput)
        
    #
    #OutputEnsembling: Combine outputs from contained methods. For the application phase. Valid values are "None" and "Avg"
        
    cv = ROOT.TMVA.CrossValidation("TMVACrossValidation", dataloader, outputFile,cvOptions)
        
    cv.BookMethod(ROOT.TMVA.Types.kBDT, "BDTG",
                "!H:!V:NTrees="+str(ntrees)+":MinNodeSize="+str(sizenode)+"%:BoostType=Grad:Shrinkage="+str(shrink)+":UseBaggedBoost:BaggedSampleFraction="+str(baggingFraction)+":nCuts="+str(ncuts)+":MaxDepth="+str(depth)+":NegWeightTreatment="+str(NegativeWeightTreatment))
    cv.Evaluate()
    msg.printBlue("GetResults")
    cv_results = cv.GetResults()
    for i in range(0, len(cv_results)):
        cv_results[i].Print()

    msg.printDebug("Closing output file")
    outputFile.Close()
    end_time = time.time()
    msg.printInfo("Running the traing took : " + "{:.2f}".format((end_time - start_time)) + " seconds")
    msg.printInfo("Wrote root file: "+str(outputFile.GetName()))
    msg.printInfo("TMVAClassification is done!")
    msg.printInfo("Launch the TMVA graphical interface with the commands:")
    msg.printInfo("\t root")
    if FoldFileOutput == "True":
        i = 1
        while i < (int(numFolds)+1):
            msg.printInfo("\t TMVA::TMVAGui(\"BDTG_fold"+str(i)+".root\")")
            i = i+1
            #msg.printInfo("Use 'OutputEnsembling' with option "None" for the application phase")
    else:
        msg.printInfo("\t TMVA::TMVAGui(\""+str(outputFile.GetName())+"\")")
    

            


# ==========
# main
# ========
if __name__ == '__main__':
  main(sys.argv[1:])


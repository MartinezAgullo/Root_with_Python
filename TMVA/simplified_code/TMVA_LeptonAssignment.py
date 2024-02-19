###############################################################
#   TMVA_LeptonAssignment
#   Script to train a BDTG model to assign the origin of
#   the light leptons.
#   Usage:  python 3
#           configure via external configuration file
#           LepAssignment_Redux
###################################################################

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



def main(argv):
    
    parser = OptionParser()
    parser.add_option("-d", "--debugLevel", dest="debugLevel", default=1, type="int",
                      help="Set debug level (DEBUG=0, INFO=1, WARNING=2, ERROR=3, FATAL=4) [default: %default]", metavar="LEVEL")
    parser.add_option("-s", "--stats", dest="stats", default=False, action='store_true', help="Print some metrics (no training)")

    try:
        (options, args) = parser.parse_args()
    except:
        parser.print_help()
        exit()
    msg = msgServer('TMVA_LeptonAssignment.py', options.debugLevel)
    config = configparser.ConfigParser()
    config.read("LepAssignment_Redux.config")
    
    #filepath = "/Users/pablo/Desktop/tHq_Analysis/2-LeptonAssigment/Studies/SamplesDir/"
    filepath = "/Users/pablo/Desktop/tHq_Analysis/2-LeptonAssigment/Studies/samples_2024/"
    treeName = "tHqLoop_nominal_Loose"
    #tree, inFile = Loader(options.debugLevel,filepath, treeName) #keep the TFile alive so that the TTree doesn't become "none"
    tree = Loader(options.debugLevel,filepath, treeName)
    
    
    if options.stats:
        Stats(tree)
        #exit()
    
    msg.printGreen("Running TMVA_Runner()")
    TMVA_Runner(options.debugLevel, config, tree) # Explore different TMVA methods



# =====================================================================
#  TMVA_Runner: To explore different TMVA methods appart from the Gradient BDT
# =====================================================================
def TMVA_Runner(debugLevel, config, tree):
    msg = msgServer('TMVA_Runner', debugLevel)
    
    NegativeWeightTreatment = config['MVA']['NegativeWeightTreatment']
    #IgnoreNegWeightsInTraining, Pray, WeightsInverseBoostNegWeights, PairNegWeightsGlobal
    
    #Create a ROOT output file where TMVA will store ntuples, histograms, etc
    outfileName = str(config['output']['outfileName'])
    outputFile = ROOT.TFile.Open(outfileName, "RECREATE")
    
    msg.printDebug("Formating the dataloader")
    dataloader = ROOT.TMVA.DataLoader('dataset')
    msg.printDebug("Reading config for variables")
    variables_tmva = getVars(config['Features']['variables_tmva'])
    variable_target = config['Features']['variable_target']
    
    msg.printDebug("Adding variables for the TMVA training")
    for var in variables_tmva:
        if False: print("reader->AddVariable( \""+str(var[0])+"\", &"+str(var[0])+");")
        #print("    float "+ str(var[0])+";")
        #print("    Float_t "+str(var[0])+", "+str(var[0])+";")
        dataloader.AddVariable(var[0],var[1])
        #msg.printBlue(str(var[0]) + ", " +str(var[1]))
    dataloader.AddSpectator("eventNumber") # the eventNumber is used for the splitExpr
        
    msg.printDebug("Designatig is_Lep1_from_TruthTop = 1 as signal and is_Lep1_from_TruthTop=0 as background")
    if False:print("reader->AddSpectator(\"eventNumber\")")
    
    tree_sig, tree_bkg = cutCollection(debugLevel, tree)
    
    dataloader.AddSignalTree(tree_sig, 1.0)
    dataloader.SetSignalWeightExpression("weight_nominalWtau")
    dataloader.AddBackgroundTree(tree_bkg, 1.0)
    dataloader.SetBackgroundWeightExpression("weight_nominalWtau")

    
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

                
    kfold= True
    if kfold == False:
        msg.printDebug("Creating factory objet")
        factoryOptions = ["TMVAClassification","!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification"]
        factory = ROOT.TMVA.Factory(factoryOptions[0], outputFile,factoryOptions[1])
    
        msg.printDebug("Booking the BDT")
        msg.printDebug("Booking: Gradient BDT")
        factory.BookMethod(dataloader, ROOT.TMVA.Types.kBDT, "BDTG",
                    "!H:!V:NTrees="+str(ntrees)+":MinNodeSize="+str(sizenode)+"%:BoostType=Grad:Shrinkage="+str(shrink)+":UseBaggedBoost:BaggedSampleFraction="+str(baggingFraction)+":nCuts="+str(ncuts)+":MaxDepth="+str(depth)+":NegWeightTreatment="+str(NegativeWeightTreatment))
                    
      
            
        # The factory runs the train, test, and evaluate the MVAs
        msg.printDebug("Training")
        factory.TrainAllMethods()       #Train MVAs using the set of training events
        msg.printDebug("Evaluating with test")
        factory.TestAllMethods()        #Evaluate all MVAs using the set of test events
        msg.printDebug("Evaluating different methods")
        factory.EvaluateAllMethods()    #Evaluate and compare performance of all configured MVAs
        
        
        
    
    if kfold == True:
        roc_curves = []  # List to store ROC curves for each fold
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
        
        if True:
            splitType = "Random"
            splitExpr = ""
        
        if splitType == "Deterministic":
            msg.printInfo("The split expression used is '" +str(splitExpr)+"' with numFolds = " + str(numFolds))
        else:
            msg.printInfo("Using random sppliting")

        cvOptions="!V:!Silent:ModelPersistence:AnalysisType=Classification:SplitType="+str(splitType)+":NumFolds="+str(numFolds)+":SplitExpr="+str(splitExpr)+":FoldFileOutput="+str(FoldFileOutput)
        
        #OutputEnsembling: Combine outputs from contained methods. For the application phase. Valid values are "None" and "Avg"
        
        cv = ROOT.TMVA.CrossValidation("TMVACrossValidation", dataloader, outputFile,cvOptions)
        
        cv.BookMethod(ROOT.TMVA.Types.kBDT, "BDTG",
                    "!H:!V:NTrees="+str(ntrees)+":MinNodeSize="+str(sizenode)+"%:BoostType=Grad:Shrinkage="+str(shrink)+":UseBaggedBoost:BaggedSampleFraction="+str(baggingFraction)+":nCuts="+str(ncuts)+":MaxDepth="+str(depth)+":NegWeightTreatment="+str(NegativeWeightTreatment))
        cv.Evaluate()
        
        #msg.printDebug("Model evaluated")
        #msg.printDebug("Separating roc curves")
        
        iMethod = 0
        for result in cv.GetResults():
            print(result)
            #methodName = cv.GetMethods()[iMethod].Data().GetMethodName()
            #print("Summary for method: {}".format(methodName))
            for iFold in range(cv.GetNumFolds()):
                print("\tFold {}: ROC int: {}, BkgEff@SigEff=0.3: {}".format(
                iFold, result.GetROCValues()[iFold], result.GetEff30Values()[iFold]))
                #roc_curve_data = result.GetROCValues()[iFold]
                cv.GetResults()[0].DrawAvgROCCurve(True, "Avg ROC for BDTG")
                #roc_curve_data = cv.GetResults()[0]
                #roc_curves.append(roc_curve_data)
                
            iMethod += 1
            



    msg.printDebug("Closing output file")
    outputFile.Close()
    msg.printInfo("Wrote root file: "+str(outputFile.GetName()))
    msg.printInfo("TMVAClassification is done!")
    msg.printInfo("Launch the TMVA graphical interface with the commands:")
    msg.printInfo("\t root")
    if kfold == True and FoldFileOutput == "True":
            i = 1
            while i < (int(numFolds)+1):
                msg.printInfo("\t TMVA::TMVAGui(\"BDTG_fold"+str(i)+".root\")")
                i = i+1
            #msg.printInfo("Use 'OutputEnsembling' with option "None" for the application phase")
    else:
            msg.printInfo("\t TMVA::TMVAGui(\""+str(outputFile.GetName())+"\")")
    

            


# =====================================================================
#  Loader: Loads the root files (for the training input and for the other samples)
# =====================================================================
def Loader(debugLevel, filepath, treeName):
    msg = msgServer('Loader', debugLevel)
    if not os.path.exists(str(filepath)):
        msg.printFatal("The path " + str(filepath) + " does not exist.")
        msg.printInfo("Exiting")
        exit()
    
    if len(os.listdir(filepath)) == 0:
        msg.printFatal("The path " + str(filepath) + " is empty.")
        msg.printInfo("Exiting")
        exit()
    
    there_are_root_files = False
    for file in os.listdir(filepath):
        if file.endswith('.root'):
            there_are_root_files = True
    if there_are_root_files == False:
        msg.printFatal("There is no root file in " + str(filepath) + ". ")
        msg.printInfo("Exiting")
        exit()
        
    tree = ROOT.TChain(treeName)
    msg.printInfo("Reading files in " + str(filepath)+":")
    for ifile in os.listdir(filepath):
        if '346799' in ifile:
            msg.printInfo(" - " + str(ifile))
            file = filepath  + ifile
            tree.Add(file)
    msg.printInfo("Total entries = %d" % tree.GetEntries())
    msg.printInfo("Total SS entries = %d" % tree.GetEntries("SS_LepHad == 1"))
    msg.printInfo("Entries used with successfull labeling = %d" % tree.GetEntries("SS_LepHad == 1 && is_Lep1_from_TruthTop > -1"))
    msg.printInfo("Entries used for training = %d" % tree.GetEntries("SS_LepHad == 1 && is_Lep1_from_TruthTop > -1 && isTruthTopWLep ==1 && (isTruthHiggsTauTauLepHad==1 || isTruthHiggsWWLepHad==1)"))
    msg.printInfo("Entries used for training (without negatively weighted events) = %d" % tree.GetEntries("SS_LepHad == 1 && is_Lep1_from_TruthTop > -1 && isTruthTopWLep ==1 && (isTruthHiggsTauTauLepHad==1 || isTruthHiggsWWLepHad==1) && weight_nominalWtau>0"))
    
    return tree
    
    #inFile = ROOT.TFile.Open(filepath, "READ")
    #tree = inFile.Get(treeName)
    #msg.printDebug("Tree : " + str(tree))
    #return tree, inFile
    

# =====================================================================
#  getVars
# =====================================================================
def getVars(varString):
    varString = varString.replace(" ", "")
    varlist = varString.split(",")
    varArray = []
    for v in varlist :
        varArray.append(v.strip().split(":"))
    return varArray

# =====================================================================
#  getList
# =====================================================================
def getList(varString):
    varString = varString.replace(" ", "")
    varArray = varString.split(",")
    return varArray
# =====================================================================
#  plot_roc_curves
# =====================================================================
def plot_roc_curves(roc_curves):
    msg = msgServer('plot_roc_curves', 0)
    msg.printInfo("Plotting roc curves")
    canvas = ROOT.TCanvas("canvas", "", 800, 600)
    legend = ROOT.TLegend(0.1, 0.7, 0.48, 0.9)
    for i, roc_curve in enumerate(roc_curves):
        roc_curve.SetLineColor(i+1)  # Set different color for each curve
        roc_curve.SetTitle(f"Fold {i+1}")
        legend.AddEntry(roc_curve, f"Fold {i+1}", "l")
        if i == 0:
            roc_curve.Draw("AL")  # Draw the first curve with axis labels
        else:
            roc_curve.Draw("L same")  # Draw over the existing curve without axis labels
    legend.Draw()
    canvas.Update()
    canvas.SaveAs("roc_curves.png")

# =====================================================================
#  Stats: Prints basic
# =====================================================================
def Stats(tree):
    msg = msgServer('Stats', 0)
    total_entries = tree.GetEntries()
    SS_entires = tree.GetEntries("SS_LepHad == 1")
    SS_withTauHadFromH = tree.GetEntries("SS_LepHad == 1 && isTruthTopWLep==1")
    OS_withTauHadFromH = tree.GetEntries("OS_LepHad == 1 && isTruthTopWLep==1")
    OS_entires = tree.GetEntries("OS_LepHad == 1")
    total_ssuccessful = tree.GetEntries("minDeltaR_lep_2_truthlep < 0.01 && minDeltaR_lep_1_truthlep < 0.01")
    SS_successful = tree.GetEntries("SS_LepHad == 1 && minDeltaR_lep_2_truthlep < 0.01 && minDeltaR_lep_1_truthlep < 0.01 && isTruthTopWLep==1")
    OS_successful = tree.GetEntries("OS_LepHad == 1 && minDeltaR_lep_2_truthlep < 0.01 && minDeltaR_lep_1_truthlep < 0.01 && isTruthTopWLep==1")
    #SS_successful = tree.GetEntries("SS_LepHad == 1 && is_Lep1_from_TruthTop > -1")
    #OS_successful = tree.GetEntries("OS_LepHad == 1 && is_Lep1_from_TruthTop > -1")
    tauHad_from_Higgs = tree.GetEntries("isTruthTopWLep==1")
    SS_type1 = tree.GetEntries("SS_LepHad == 1 && minDeltaR_lep_2_truthlep < 0.01 && minDeltaR_lep_1_truthlep < 0.01 && isTruthTopWLep==1 && is_Lep1_from_TruthTop == 1")
    SS_type2 = tree.GetEntries("SS_LepHad == 1 && minDeltaR_lep_2_truthlep < 0.01 && minDeltaR_lep_1_truthlep < 0.01 && isTruthTopWLep==1 && is_Lep1_from_TruthTop == 0")
    
    SS_type1_HWW_Htautau = tree.GetEntries("SS_LepHad == 1 && minDeltaR_lep_2_truthlep < 0.01 && minDeltaR_lep_1_truthlep < 0.01 && isTruthTopWLep==1 && is_Lep1_from_TruthTop == 1 && (isTruthHiggsTauTauLepHad==1 || isTruthHiggsWWLepHad==1)")
    SS_type2_HWW_Htautau = tree.GetEntries("SS_LepHad == 1 && minDeltaR_lep_2_truthlep < 0.01 && minDeltaR_lep_1_truthlep < 0.01 && isTruthTopWLep==1 && is_Lep1_from_TruthTop == 0 && (isTruthHiggsTauTauLepHad==1 || isTruthHiggsWWLepHad==1)")
    SS_successfull_HWW_Htautau = SS_type1_HWW_Htautau + SS_type2_HWW_Htautau
    
        
    # Cross-check with Loader()
    msg.printInfo("Total entries = " + str(total_entries))
    msg.printInfo("Entries with hadronic tau from Higgs = " + str(tauHad_from_Higgs) + " ("+str(tauHad_from_Higgs*100/total_entries)+" %)")
    msg.printInfo("SS entries = " + str(SS_entires))
    msg.printInfo("OS entries = " + str(OS_entires))
    msg.printInfo("SS entries with TauHad from Higgs = " + str(SS_withTauHadFromH) +" ("+ str(100*SS_withTauHadFromH/SS_entires) +" %)")
    msg.printInfo("OS entries with TauHad from Higgs = " + str(OS_withTauHadFromH)+ " ("+ str(100*OS_withTauHadFromH/OS_entires) +" %)")
    msg.printInfo("Events with succssesfull labeling = " + str(total_ssuccessful) +" ("+ str(100*total_ssuccessful/total_entries) +" %)")
    msg.printInfo("SS events with succssesfull labeling = " + str(SS_successful) +" ("+ str(100*SS_successful/SS_entires) +" %)")
    msg.printInfo("OS events with succssesfull labeling = " + str(OS_successful) +" ("+ str(100*OS_successful/OS_entires) +" %)")
    msg.printInfo("SS events labeled as type1 = " + str(SS_type1) +" ("+ str(100*SS_type1/SS_successful) +" %)")
    msg.printInfo("SS events labeled as type2 = " + str(SS_type2) +" ("+ str(100*SS_type2/SS_successful) +" %)")
    
    msg.printInfo("SS events with succssesfull labeling in H-> WW and H-> tau tau = " + str(SS_successfull_HWW_Htautau) +" ("+ str(100*SS_successfull_HWW_Htautau/SS_successful) +" %)")
    msg.printInfo("SS events labeled as type1 in H-> WW and H-> tau tau = " + str(SS_type1_HWW_Htautau) +" ("+ str(100*SS_type1_HWW_Htautau/SS_successfull_HWW_Htautau) +" %)")
    msg.printInfo("SS events labeled as type2 in H-> WW and H-> tau tau = " + str(SS_type2_HWW_Htautau) +" ("+ str(100*SS_type2_HWW_Htautau/SS_successfull_HWW_Htautau) +" %)")
    
    
    
# =====================================================================
#  cutCollection: Set of TCuts to select the events to input into the model.
# =====================================================================
def cutCollection(debugLevel,tree):
    msg = msgServer('cutCollection', debugLevel)
    msg.printDebug("Preparing train and test trees for signal (type1) and backgorund (type2)")
    msg.printDebug(" Requirements for training:")
    msg.printDebug("   - Succesfull truth-reco matching (is_Lep1_from_TruthTop > -1)")
    msg.printDebug("   - Security check for truth-reco matching (minDeltaR_lep_2_truthlep < 0.01 && minDeltaR_lep_1_truthlep < 0.01)")
    msg.printDebug("   - SS events only (SS_LepHad = 1)")
    msg.printDebug("   - Hadronic tau from Higgs (isTruthTopWLep==1)")
    msg.printDebug("   - H-> WW or H->TauTau (isTruthHiggsTauTauLepHad=1 or isTruthHiggsWWLepHad=1)")
    selectionCut_SS = ROOT.TCut("is_Lep1_from_TruthTop > -1 && SS_LepHad == 1")
    selectionCut_Cones = ROOT.TCut("minDeltaR_lep_2_truthlep < 0.01 && minDeltaR_lep_1_truthlep < 0.01")
    selectionCut_Channels = ROOT.TCut("isTruthHiggsTauTauLepHad==1 || isTruthHiggsWWLepHad==1")
    selectionCut_TauFromHiggs = ROOT.TCut("isTruthTopWLep==1")
    mycuts = ROOT.TCut("is_Lep1_from_TruthTop==1") # Type 1: l1 from t and l2 from H
    mycutb = ROOT.TCut("is_Lep1_from_TruthTop==0") # Type 2: l1 from H and l2 from t
    mycut_type1 = mycuts + selectionCut_Cones + selectionCut_Channels + selectionCut_TauFromHiggs + selectionCut_SS #+ selectionCut_Channels
    mycut_type2 = mycutb + selectionCut_Cones + selectionCut_Channels + selectionCut_TauFromHiggs + selectionCut_SS #+ selectionCut_Channels
    removeNegWeight = True
    if removeNegWeight:
        msg.printDebug("   - Removing negatively weighted events (weight_nominalWtau>0)")
        mycut_type1 = mycut_type1 + ROOT.TCut("weight_nominalWtau>0")
        mycut_type2 = mycut_type2 + ROOT.TCut("weight_nominalWtau>0")
    else:
        msg.printDebug("   - Not removing negatively weighted events yet")
    
    msg.printDebug("mycut_type1 = " + str(mycut_type1))
    msg.printDebug("mycut_type2 = " + str(mycut_type2))
    
    Tree_for_type1 = tree.CopyTree(str(mycut_type1))
    Tree_for_type2 = tree.CopyTree(str(mycut_type2))
    
    if debugLevel == 0: # For cross-checking with Stats()
        SS_type1_cutCollection = Tree_for_type1.GetEntries()
        SS_type2_cutCollection = Tree_for_type2.GetEntries()
        msg.printInfo("Total tree entries = " + str(tree.GetEntries()))
        msg.printInfo("SS events with succssesfull labeling = " + str(SS_type1_cutCollection + SS_type2_cutCollection))
        msg.printInfo("SS events labeled as type1 = " + str(SS_type1_cutCollection) +" ("+ str(100*SS_type1_cutCollection/(SS_type1_cutCollection + SS_type2_cutCollection)) +" %)")
        msg.printInfo("SS events labeled as type2 = " + str(SS_type2_cutCollection) +" ("+ str(100*SS_type2_cutCollection/(SS_type1_cutCollection + SS_type2_cutCollection)) +" %)")
        
    
    
    return Tree_for_type1, Tree_for_type2

# =====================================================================
#  msgServer: Display text in a fancy way
# =====================================================================
class msgServer:
    def __init__(self, algName='',debugLevel=4):
        self.algName = algName
        self.text = ''

        # output debug level: DEBUG=0, INFO=1, WARNING=2, ERROR=3, FATAL=4
        self.debugLevel = debugLevel
        self.EndColor='\033[0m'       # Text color reset
        self.Black='\033[0;30m'        # Black
        self.Red='\033[0;31m'          # Red
        self.Green='\033[0;32m'        # Green
        self.Yellow='\033[0;33m'       # Yellow
        self.Blue='\033[0;34m'         # Blue
        self.Purple='\033[0;35m'       # Purple
        self.Cyan='\033[0;36m'         # Cyan
        self.White='\033[0;37m'        # White
        self.BBlack='\033[1;30m'       # Bold Black
        self.BRed='\033[1;31m'         # Bold Red
        self.BGreen='\033[1;32m'       # Bold Green
        self.BYellow='\033[1;33m'      # Bold Yellow
        self.BBlue='\033[1;34m'        # Bold Blue
        self.BPurple='\033[1;35m'      # Bold Purple
        self.BCyan='\033[1;36m'        # Bold Cyan
        self.BWhite='\033[1;37m'       # Bold White
        self.BOLD = "\033[1m"


        # Print methods
    def printDebug(self, msg):
        if self.debugLevel < 1: print(str(self.algName) + '\t' + str('DEBUG') + '\t \t' + str(msg))
    def printInfo(self, msg):
        if self.debugLevel < 2: print(str(self.algName) + '\t' + str('INFO') + '\t\t' + str(msg))
    def printWarning(self, msg):
        if self.debugLevel < 3: print(str(self.Yellow) + str(self.algName) + '\t' + str('WARNING') + '\t\t' + str(msg) + str(self.EndColor))
    def printError(self, msg):
        if self.debugLevel < 4: print(str(self.Red) + str(self.algName) + '\t' + str('ERROR') + '\t\t' + str(msg)  + str(self.EndColor))
    def printFatal(self, msg):
        print(str(self.BRed) + str(self.algName) + '\t' + str('FATAL') + '\t\t' + str(msg) + str(self.EndColor)) #'-16s %-12s %s'+str(self.EndColor)) % (self.algName, 'FATAL', msg)
    # colors
    def printBlue(self, msg): print(str(self.Blue) + str(self.algName) + '\t' + str('INFO') + '\t\t' + str(msg)+ str(self.EndColor))
    def printRed(self, msg): print(str(self.Red) + str(self.algName) + '\t' + str('INFO') + '\t\t' + str(msg)+ str(self.EndColor))
    def printGreen(self, msg): print(str(self.Green) + str(self.algName) + '\t' + str('INFO') + '\t\t' + str(msg)+ str(self.EndColor))

    # extras
    def printBold(self, msg): print(str(self.BOLD) + str(self.algName) + '\t' + str('INFO') + '\t\t' + str(msg)+ str(self.EndColor))


# ==========
# main
# ========
if __name__ == '__main__':
  main(sys.argv[1:])


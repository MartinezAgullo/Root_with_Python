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



def main(argv):
    debugLevel = 0
    msg = msgServer('ClassifyLeptonsTMVA.py', debugLevel)
    config = configparser.ConfigParser()
    config.read("LepAssignment.config")
    
    tree, inFile = Loader(debugLevel, config) #it is necessary to keep the TFile alive so taht the TTree doesn't become "none"
    
    scanParams(debugLevel, config, tree)    # Run Gradinet BDTs over a grid of hyperparameters
    #TMVA_Runner(debugLevel, config, tree)  # Explore different TMVA methods
    
    

# =====================================================================
#  scanParams: Grid exploration of hyperparameters for the Gradient BDT
# =====================================================================
def scanParams(debugLevel, config, tree):
    import itertools
    msg = msgServer('scanParams', debugLevel)
    
    i = 1
    depth = getList(config['BDT_scanner']['depth'])
    ncuts = getList(config['BDT_scanner']['ncuts'])
    ntrees = getList(config['BDT_scanner']['ntrees'])
    shrink = getList(config['BDT_scanner']['shrink'])
    negWeights = getList(config['BDT_scanner']['negWeights'])
    
    comb = [shrink, depth, ncuts, ntrees, negWeights]
    ncomb = list(itertools.product(*comb))

    msg.printInfo("Grid exploration of BDT")
    msg.printInfo(" --> depth = "+str(depth))
    msg.printInfo(" --> ncuts = "+str(ncuts))
    msg.printInfo(" --> ntrees = "+str(ntrees))
    msg.printInfo(" --> shrink = "+str(shrink))
    msg.printInfo("Number of configurations = "+str(len(ncomb)))
    
    msg.printDebug("Storing log files in: " + config['BDT_scanner']['log_dir'])
    msg.printDebug("Storing BDTs in: " + config['BDT_scanner']['BDTs_dir'])
    if not os.path.exists(str(config['BDT_scanner']['log_dir'])): msg.printFatal("log_dir :: The path '" + str(config['BDT_scanner']['BDTs_dir']) + "' does not exist")
    if not os.path.exists(str(config['BDT_scanner']['BDTs_dir'])): msg.printFatal("BDTs_dir :: The path '" + str(config['BDT_scanner']['BDTs_dir']) + "' does not exist")
    
    pool = mp.Pool(processes = 10)
    msg.printGreen("Start pooling:")
    for conf in ncomb :
        msg.printDebug("Pooling for "+str(conf))
        #defineBDT(debugLevel, config, tree, "BDTG_"+str(i), i, conf[0], conf[1], conf[2], conf[3], conf[4])
        result = pool.apply_async(defineBDT,args=(debugLevel, config, tree, "BDTG_"+str(i), i, conf[0], conf[1], conf[2], conf[3], conf[4]))
        #The Pool object a convenient means of parallelizing the execution of a function across multiple input values, distributing the input data across processes.
        #if i == 1:
        #    msg.printInfo("Leaving loop after BTD_" + str(i))
        #    break
        i = i+1
    msg.printDebug("End pooling")
    
    msg.printDebug("Waiting for the processes to end")
    pool.close()
        
    msg.printDebug("Waiting all asynchronous processes to end")
    pool.join()
                   
    msg.printDebug("All processes finished")



# =====================================================================
#  defineBDT: To explore the performance of the BDT depending on the hypeparameters used
# =====================================================================
def defineBDT(debugLevel, config, tree, output, i, shrink=0.2, depth=5, ncuts=30, ntrees=1500, negWeights = "IgnoreNegWeightsInTraining"):
    msg = msgServer('defineBDT', debugLevel)
    log_dir = config['BDT_scanner']['log_dir']
    BDTs_dir = config['BDT_scanner']['BDTs_dir']
    msg.printGreen(" Running BDT "+str(i)+" -> [NTrees="+str(ntrees)+", Shrinkage="+str(shrink)+", nCuts="+str(ncuts)+" MaxDepth="+str(depth)+", NegWeightTreatment="+str(negWeights))
    #ROOT.gSystem.RedirectOutput(str(log_dir)+"log_"+output+"_"+str(os.getpid()) + ".log")
    outName = str(BDTs_dir)+output+"_"+str(shrink)+"_"+str(depth)+"_"+str(ncuts)+"_"+str(ntrees)+".root"
    rootFile = ROOT.TFile(outName,"RECREATE")
    msg.printDebug(str(i) + " --> rootFile :: " + str(rootFile.GetName()))
    
    msg.printDebug(str(i)+ " --> Defining the dataloader")
    dataloader = ROOT.TMVA.DataLoader('dataset')
    variables_tmva = getVars(config['Features']['variables_tmva'])
    variables_spectator = getVars(config['Features']['variables_spectator'])
    variable_target = config['Features']['variable_target']
    
    msg.printDebug(str(i)+ " --> Defining variables")
    for var in variables_tmva:
        dataloader.AddVariable(var[0],var[1])
    for var in variables_spectator:
        dataloader.AddSpectator(var[0],var[1])

    msg.printBlue(str(i)+ " --> Defining signal and background")
    # is_Lep1_from_Top = 1 is defined as signal and is_Lep1_from_Top=0 as background"
    dataloader.AddSignalTree(tree, 1.0)
    dataloader.SetSignalWeightExpression("weight_nominal")
    dataloader.AddBackgroundTree(tree, 1.0)
    dataloader.SetBackgroundWeightExpression("weight_nominal")
    mycuts = ROOT.TCut("is_Lep1_from_Top==1")
    mycutb = ROOT.TCut("is_Lep1_from_Top==0")
    
    msg.printBlue(str(i)+ " --> Preparing test and train samples")
    dataloader.PrepareTrainingAndTestTree(mycuts, mycutb,
                                        "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V")
        
    msg.printDebug(str(i)+ " --> Defining Classification factory")
    factory = ROOT.TMVA.Factory("TMVAClassification", rootFile,"!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification")

                                        
    msg.printDebug(str(i)+ " --> Booking TMVA method")
    #msg.printDebug("!H:!V:VarTransform=D,G:NTrees="+str(ntrees)+":BoostType=Grad:Shrinkage="+str(shrink)+":UseBaggedBoost:BaggedSampleFraction=0.5:nCuts="+str(ncuts)+":MaxDepth="+str(depth)+":NegWeightTreatment="+str(negWeights))
    factory.BookMethod(dataloader, ROOT.TMVA.Types.kBDT, "BDTG_"+str(i),"!H:!V:VarTransform=D,G:NTrees="+str(ntrees)+":BoostType=Grad:Shrinkage="+str(shrink)+":UseBaggedBoost:BaggedSampleFraction=0.5:nCuts="+str(ncuts)+":MaxDepth="+str(depth)+":NegWeightTreatment="+str(negWeights))
                
    # Run training, test and evaluation
    msg.printDebug(str(i)+ " --> Train, test and evaluate the BDT")
    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()

    rootFile.Close()
    msg.printGreen(" Running BDT "+str(i)+" -> Finnished")

    return 1


# =====================================================================
#  Loader: Loads the input root file
# =====================================================================
def Loader(debugLevel, config):
    msg = msgServer('Loader', debugLevel)
    filename = config['input']['filename']
    filepath = config['input']['filepath']
    if not os.path.exists(str(filepath)):
        msg.printFatal("The path " + str(filepath) + " does not exist.")
        msg.printInfo("Exiting")
        exit()
    filepath = str(filepath) + str(filename)
    treeName = str(config['input']['treeName'])
    
    if not os.path.exists(filepath):
        msg.printFatal("The file " + str(filename) + " does not exist in the given path.")
    
    inFile = ROOT.TFile.Open(filepath, "READ")
    tree = inFile.Get(treeName)
    msg.printDebug("Tree : " + str(tree))
    return tree, inFile

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


# =====================================================================
#  TMVA_Runner: To explore different TMVA methods appart from the Gradient BDT
# =====================================================================
def TMVA_Runner(debugLevel, config, tree):
    msg = msgServer('TMVA_Runner', debugLevel)
    AnalysisType = config['MVA']['AnalysisType']
    NegativeWeightTreatment = config['MVA']['NegativeWeightTreatment']
    if not (AnalysisType == "Classification" or AnalysisType == "Regression"): msg.printFatal(" The selected AnalysisType method" + str(AnalysisType) + " is not known. Review your configuration file.")
    
    #Create a ROOT output file where TMVA will store ntuples, histograms, etc
    outfileName = str(config['output']['outfileName'])
    outputFile = ROOT.TFile.Open(outfileName, "RECREATE")
    
    msg.printDebug("Formating the dataloader")
    dataloader = ROOT.TMVA.DataLoader('dataset')
    msg.printDebug("Reading config for variables")
    variables_tmva = getVars(config['Features']['variables_tmva'])
    variables_spectator = getVars(config['Features']['variables_spectator'])
    variable_target = config['Features']['variable_target']
    
    msg.printDebug("Adding variables for the TMVA training")
    for var in variables_tmva:
        dataloader.AddVariable(var[0],var[1])
    msg.printDebug("Adding spectator variables")  # not used in the MVA training but will appear in the final tree produced by TMVA
    for var in variables_spectator:
        dataloader.AddSpectator(var[0],var[1])
    
    if AnalysisType == "Regression":
        msg.printDebug("Adding the variable carrying the regression taret")
        dataloader.AddTarget("is_Lep1_from_Top")
        msg.printDebug("Label loaded")
        
        msg.printDebug("Using weight_nominal")
        dataloader.AddRegressionTree(tree, 1.0)
        dataloader.SetWeightExpression("weight_nominal", "Regression")
        msg.printDebug("Preparing train and test trees")
        selectionCut = ROOT.TCut("is_Lep1_from_Top > -1")
        # If no number are given, half of the events are are in the tree are used for training and the other half for test
        dataloader.PrepareTrainingAndTestTree(selectionCut,"nTrain_Regression=0:nTest_Regression=0:SplitMode=Random:NormMode=NumEvents:!V" )
        
    if AnalysisType == "Classification":
        msg.printDebug("Designatig is_Lep1_from_Top = 1 as signal and is_Lep1_from_Top=0 as background")
        dataloader.AddSignalTree(tree, 1.0)
        dataloader.SetSignalWeightExpression("weight_nominal")
        dataloader.AddBackgroundTree(tree, 1.0)
        dataloader.SetBackgroundWeightExpression("weight_nominal")
        msg.printDebug("Preparing train and test trees for signal and backgorund")
        mycuts = ROOT.TCut("is_Lep1_from_Top==1")
        mycutb = ROOT.TCut("is_Lep1_from_Top==0")
        dataloader.PrepareTrainingAndTestTree( mycuts, mycutb,
                                        "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V")
    
    
    msg.printDebug("Creating factory objet")
    if AnalysisType == "Regression":
        msg.printDebug("Regression factory")
        factoryOptions = ["TMVARegression","!V:!Silent:Color:DrawProgressBar:AnalysisType=Regression"]
    if AnalysisType == "Classification":
        msg.printDebug("Classification factory")
        factoryOptions = ["TMVAClassification","!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification"]
    
    factory = ROOT.TMVA.Factory(factoryOptions[0], outputFile,factoryOptions[1])
    
    
    msg.printDebug("Booking MVA methods")
    if False:
        msg.printDebug("Using Linear discriminant")
        factory.BookMethod(dataloader, ROOT.TMVA.Types.kLD, 'Linear Discriminant',"!H:!V:VarTransform=None")
    
    BDT_BoostType = getList(config['MVA']['BDT_BoostType'])
    Classification_algorithm = getList(config['MVA']['Classification_algorithm'])
    depth = config['MVA']['BDT_depth']
    shrink = config['MVA']['BDT_shrink']
    ntrees = config['MVA']['BDT_ntrees']
    ncuts = config['MVA']['BDT_ncuts']
                

    
    if BDT_BoostType == "AdaBoostR2":
        msg.printDebug("Using AdaBoostR2 BDT")
        factory.BookMethod(dataloader, ROOT.TMVA.Types.kBDT, 'BDT_AdaBoost', "!H:!V:NTrees=100:MinNodeSize=1.0%:BoostType=AdaBoostR2:SeparationType=RegressionVariance:nCuts=20:PruneMethod=CostComplexity:PruneStrength=30")
    
    if AnalysisType == "Regression":
        if BDT_BoostType == "Gradient": msg.printDebug("Booking: Gradient BDT")
        if "Default" in NegativeWeightTreatment and BDT_BoostType == "Gradient":
            msg.printDebug("NegativeWeightTreatment :: Default")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kBDT, 'BDTG_default', "!H:!V:NTrees=2000::BoostType=Grad:Shrinkage=0.1:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=4")
        if "IgnoreNegWeightsInTraining" in NegativeWeightTreatment and BDT_BoostType == "Gradient":
            msg.printDebug("NegativeWeightTreatment :: IgnoreNegWeightsInTraining")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kBDT, 'BDTG_ignoreNegWeight', "!H:!V:NTrees=2000::BoostType=Grad:Shrinkage=0.1:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=4:NegWeightTreatment=IgnoreNegWeightsInTraining")
        if "Pray" in NegativeWeightTreatment and BDT_BoostType == "Gradient":
            msg.printDebug("NegativeWeightTreatment :: Pray")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kBDT, 'BDTG_pray', "!H:!V:NTrees=2000::BoostType=Grad:Shrinkage=0.1:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=4:NegWeightTreatment=Pray")
        if "WeightsInverseBoostNegWeights" in NegativeWeightTreatment and BDT_BoostType == "Gradient":
            msg.printDebug("NegativeWeightTreatment :: WeightsInverseBoostNegWeights")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kBDT, 'BDTG_inverseNegWeight', "!H:!V:NTrees=2000::BoostType=Grad:Shrinkage=0.1:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=4:NegWeightTreatment=InverseBoostNegWeights")
        if "PairNegWeightsGlobal" in NegativeWeightTreatment and BDT_BoostType == "Gradient":
            msg.printDebug("NegativeWeightTreatment :: PairNegWeightsGlobal")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kBDT, 'BDTG_pairNegWeight', "!H:!V:NTrees=2000::BoostType=Grad:Shrinkage=0.1:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=4:NegWeightTreatment=PairNegWeightsGlobal")
    
    if AnalysisType == "Classification":
        if "Gradient" in Classification_algorithm:  # In the end we are using this
            msg.printDebug("Booking: Gradient BDT")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kBDT, "BDTG",
                           "!H:!V:NTrees="+str(ntrees)+":MinNodeSize=2.5%:BoostType=Grad:Shrinkage="+str(shrink)+":UseBaggedBoost:BaggedSampleFraction=0.5:nCuts="+str(ncuts)+":MaxDepth="+str(depth)+":NegWeightTreatment="+str(NegativeWeightTreatment))
        ### Testing other methjodss
        if "Fisher" in Classification_algorithm:
            msg.printDebug("Booking: Fisher discriminant (same as LD)")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kFisher, "Fisher", "H:!V:Fisher:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10")
        if "FisherG" in Classification_algorithm:
            msg.printDebug("Booking: Fisher with Gauss-transformed input variables")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kFisher, "FisherG", "H:!V:VarTransform=Gauss")
        if "BoostedFisher" in Classification_algorithm:
            msg.printDebug("Booking: Composite classifier: ensemble (tree) of boosted Fisher classifiers")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kFisher, "BoostedFisher",
                                "H:!V:Boost_Num=20:Boost_Transform=log:Boost_Type=AdaBoost:Boost_AdaBoostBeta=0.2:!Boost_DetailedMonitoring")
        if "LikelihoodD" in Classification_algorithm:
            msg.printDebug("Booking: Decorrelated likelihood")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kLikelihood, "LikelihoodD",
                           "!H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmooth=5:NAvEvtPerBin=50:VarTransform=Decorrelate")
        if "LD" in Classification_algorithm:
            msg.printDebug("Booking: Linear discriminant (same as Fisher discriminant)")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kLD, "LD", "H:!V:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10")
        if "MLPBNN" in Classification_algorithm:
            msg.printDebug("Booking: Recommended ANN with BFGS training method and bayesian regulators")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kMLP, "MLPBNN", "H:!V:NeuronType=tanh:VarTransform=N:NCycles=60:HiddenLayers=N+5:TestRate=5:TrainingMethod=BFGS:UseRegulator")
        if "FDA_GA" in Classification_algorithm:
            msg.printDebug("Booking: Function Discriminant analysis. Using minimisation of user-defined function using Genetics Algorithm")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kFDA, "FDA_GA",
                           "H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=GA:PopSize=100:Cycles=2:Steps=5:Trim=True:SaveBestGen=1")
            
    # The factory runs the train, test, and evaluate the MVAs
    msg.printDebug("Training")
    factory.TrainAllMethods()       #Train MVAs using the set of training events
    msg.printDebug("Evaluating with test")
    factory.TestAllMethods()        #Evaluate all MVAs using the set of test events
    msg.printDebug("Evaluating different methods")
    factory.EvaluateAllMethods()    #Evaluate and compare performance of all configured MVAs
    
    if AnalysisType == "Classification" and False: # Deactivated
        msg.printDebug("Plot ROC curve")
        c1 = factory.GetROCCurve(dataloader)
        c1.Draw()
    
    
    msg.printDebug("Closing output file")
    outputFile.Close()
    msg.printInfo("Wrote root file: "+str(outputFile.GetName()))
    if AnalysisType == "Regression":msg.printInfo("TMVARegression is done!")
    if AnalysisType == "Classification":msg.printInfo("TMVAClassification is done!")
    #feature_importance =  ROOT.TMVA.Ranking
    #ROOT.TMVA.Ranking.Print()
    
    msg.printDebug("Launch the TMVA graphical interface with the commands:")
    msg.printDebug("\t root")
    msg.printDebug("\t TMVA::TMVAGui(\""+str(outputFile.GetName())+"\")")
    #ROOT.TMVA.TMVARegGui(str(outputFile.GetName()))
    #ROOT.TMVA.TMVAGui(str(outputFile.GetName()))



# ==========
# main
# ========
if __name__ == '__main__':
  main(sys.argv[1:])


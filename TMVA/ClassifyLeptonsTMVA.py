import os,sys
try:
    import ROOT
except:
    print("import ROOT Failed")
    print("Version of Python used:: " +str(sys.version))
    exit()
import numpy as np
import configparser
#from root_numpy import tree2array
#import pandas as pd
#import pickle

def main(argv):
    msg = msgServer('ClassifyLeptonsTMVA.py', 0)
    
    config = configparser.ConfigParser()
    config.read("LepAssignment.config")

    # Load dataset, filter the required events and define the training variables
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
    

    
    #if False:
    #    msg.printDebug("Seting all weights to 1")
    #    dataloader.AddRegressionTree(tree, 1.0)
    if AnalysisType == "Regression":
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
                                        "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V" )
    
    
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
    
    BDT_BoostType = getMethods(config['MVA']['BDT_BoostType'])
    Classification_algorithm = getMethods(config['MVA']['Classification_algorithm'])
    depth = config['MVA']['BDT_depth']
    shrink = config['MVA']['BDT_shrink']
    ntrees = config['MVA']['BDT_ntrees']
                

    
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
        if "Gradient" in Classification_algorithm:  # In the end we are using this
            msg.printDebug("Booking: Gradient BDT")
            factory.BookMethod(dataloader, ROOT.TMVA.Types.kBDT, "BDTG",
                           "!H:!V:NTrees="+str(ntrees)+":MinNodeSize=2.5%:BoostType=Grad:Shrinkage="+str(shrink)+":UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth="+str(depth)+":NegWeightTreatment="+str(NegativeWeightTreatment))
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
    
    if AnalysisType == "Classification" and False:
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
    
    
    # Cross-validation (not used currently)
    '''
    print("--- TMVACrossValidationRegression: Using input file: " + str(filename) + "---")
    
    
    dataloader.PrepareTrainingAndTestTree(selectionCut, "nTest_Regression=1"
                                                        ":SplitMode=Block"
                                                        ":NormMode=NumEvents"
                                                        ":!V")
    # options for cross-validation
    numFolds=2
    analysisType=ROOT.TString("Regression")
    splitExpr = ROOT.TString("")
    
    msg.printDebug("Seting options for the cross validation")
    cvOptions_a = ROOT.TString(":".join(["!V",
                                    ":!Silent"
                                    
                                    ":ModelPersistence"
                                    ":!FoldFileOutput"
                                    ":AnalysisType=%s"
                                    ":NumFolds=%i"
                                    ":SplitExpr=%s"]))
    
    cvOptions = ROOT.TString.Form(cvOptions_a, analysisType.Data(), numFolds, splitExpr.Data())

    msg.printDebug("Cross validating")
    cv = ROOT.TMVA.CrossValidation("TMVACrossValidationRegression", dataloader, outputFile, cvOptions)
    '''


# =====================================================================
#  DrawTrainTest
# =====================================================================
#def DrawTrainTest():
    



# =====================================================================
#  getVars
# =====================================================================
def getVars(varString):
    varlist = varString.split(",")
    varArray = []
    for v in varlist :
        varArray.append(v.strip().split(":"))
    
    return varArray

# =====================================================================
#  getMethods
# =====================================================================
def getMethods(varString):
    varArray = varString.split(",")
    return varArray


# =====================================================================
#  msgServer
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





# ==========
# main
# ========
if __name__ == '__main__':
  main(sys.argv[1:])


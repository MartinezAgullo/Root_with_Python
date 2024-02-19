###########################################################
#       Script to store the BDT score of ROOT TMVA        #
###########################################################

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
    config.read("LepAssignment_Redux.config")
    
    filepath = "/Users/pablo/Desktop/tHq_Analysis/3-LeptonAssigment/Studies/SamplesDir_backup/"
    treeName = "tHqLoop_nominal_Loose"
    #tree, inFile = Loader(options.debugLevel,filepath, treeName) #keep the TFile alive so that the TTree doesn't become "none"
    tree = Loader(options.debugLevel,filepath, treeName)
    
    
    msg.printGreen("Running TMVA_Application()")
    TMVA_Application(options.debugLevel, config, tree) # Explore different TMVA methods



# =====================================================================
#  TMVA_Application:
# =====================================================================
def TMVA_Application(debugLevel, config, tree):
    msg = msgServer('TMVA_Runner', debugLevel)
    
    ROOT.TMVA.Tools.Instance #This loads the library

    msg.printDebug("Reading config for variables")
    variables_tmva = getVars(config['Features']['variables_tmva'])
    variable_target = config['Features']['variable_target']
    
    reader = ROOT.TMVA.Reader("!Color:!Silent")
    
    #for var in variables_tmva:
    #    print("        var_"+str(var[0])+" = array('f',[0])" )
    #for var in variables_tmva:
    #    print("        reader.AddVariable(\""+str(var[0])+"\", var_"+str(var[0])+")" )
    #for var in variables_tmva:
    #    print("        var_"+str(var[0])+" = event."+str(var[0]))
    #exit()
    
    # Define variables, fill the reader informaton #
    # and book the method before the event loop    #
    var_deltaR_tau_LightLep1 = array.array('f',[0])
    var_DeltaRLeadingLeptonClosestBjet = array.array('f',[0])
    var_deltaR_b_LightLep1 = array.array('f',[0])
    var_deltaR_b_LightLep2 = array.array('f',[0])
    var_deltaR_tau_LightLep2 = array.array('f',[0])
    var_m_Hvis_opt1 = array.array('f',[0])
    var_deltaEta_tau_LightLep2 = array.array('f',[0])
    var_deltaEta_tau_LightLep1 = array.array('f',[0])
    var_eventNumber = array.array('f',[0])
    
    msg.printInfo("Adding Variables")
    reader.AddVariable("deltaR_tau_LightLep1", var_deltaR_tau_LightLep1)
    reader.AddVariable("DeltaRLeadingLeptonClosestBjet", var_DeltaRLeadingLeptonClosestBjet)
    reader.AddVariable("deltaR_b_LightLep1", var_deltaR_b_LightLep1)
    reader.AddVariable("deltaR_b_LightLep2", var_deltaR_b_LightLep2)
    reader.AddVariable("deltaR_tau_LightLep2", var_deltaR_tau_LightLep2)
    reader.AddVariable("m_Hvis_opt1", var_m_Hvis_opt1)
    reader.AddVariable("deltaEta_tau_LightLep2", var_deltaEta_tau_LightLep2)
    reader.AddVariable("deltaEta_tau_LightLep1", var_deltaEta_tau_LightLep1)
    reader.AddSpectator("eventNumber", var_eventNumber) # the eventNumber is used for the splitExpr
    
    msg.printInfo("Book the MVA methods")
    weightFileDir = "/Users/pablo/Desktop/Tests for BDRT LepOrigin/mejor/"
    #prefix = "TMVAClassification" <- If kfold not used
    prefix = "TMVACrossValidation"
    methodName = "BDTG"
    #methodName = methodName + str(" method")
    weightfile = weightFileDir + prefix + str("_") + str(methodName) + str(".weights.xml")
    msg.printInfo("weightfile :: " +str(weightfile))
    reader.BookMVA(methodName, weightfile)
    LepAssign_BDTcut = 0
    
    type1_count = 0
    type1_ok = 0
    type2_count = 0
    type2_ok = 0
    
    msg.printGreen("Looping over the events")
    #Loop over events
    for event in tree:
        #if event.eventNumber > 17000000: continue #Test para ver si el problema con el EvaluateMVA depende de cuál es el primer evento o algo
        var_deltaR_tau_LightLep1[0] = event.deltaR_tau_LightLep1
        var_DeltaRLeadingLeptonClosestBjet[0] = event.DeltaRLeadingLeptonClosestBjet
        var_deltaR_b_LightLep1[0] = event.deltaR_b_LightLep1
        var_deltaR_b_LightLep2[0] = event.deltaR_b_LightLep2
        var_deltaR_tau_LightLep2[0] = event.deltaR_tau_LightLep2
        var_m_Hvis_opt1[0] = event.m_Hvis_opt1
        var_deltaEta_tau_LightLep2[0] = event.deltaEta_tau_LightLep2
        var_deltaEta_tau_LightLep1[0] = event.deltaEta_tau_LightLep1
        var_eventNumber[0] = event.eventNumber
        
        #print(reader.EvaluateMVA(methodName))
        
        #Evaluating the method
        LeptAssign_PredictedBDT_val = reader.EvaluateMVA(methodName)
        if event.is_Lep1_from_TruthTop == 0:
            #msg.printInfo("Score for a Type2 event :: " +str(LeptAssign_PredictedBDT_val))
            type2_count = type2_count +1
            if LeptAssign_PredictedBDT_val < 0:
                type2_ok = type2_ok + 1
            #else:
            #    msg.printWarning("Type 2 event had BDT score of " + str(LeptAssign_PredictedBDT_val))
        if event.is_Lep1_from_TruthTop == 1:
            #msg.printInfo("Score for a Type1 event :: " +str(LeptAssign_PredictedBDT_val))
            type1_count = type1_count +1
            if LeptAssign_PredictedBDT_val >= 0:
                type1_ok = type1_ok + 1
            #else:
            #    msg.printWarning("Type 1 event had BDT score of " + str(LeptAssign_PredictedBDT_val))
        else:
            pass
            #msg.printWarning("No truth matching avaiulable")
        
            
    msg.printInfo("Score evaluated")
    msg.printInfo("Type 1 events :: "+str(type1_count))
    msg.printInfo("Type 2 events :: "+str(type2_count))
    msg.printInfo("Type 1 correctly assigned :: "+str(type1_ok) + "("+str(100* type1_ok/type1_count)+"%)")
    msg.printInfo("Type 2 correctly assigned :: "+str(type2_ok) + "("+str(100* type2_ok/type2_count)+"%)")
    msg.printInfo("Fraction of correctly assigned :: " +str(100* (type2_ok+type1_ok)/(type1_count+type2_count))+"%")
    if (type2_ok == 0) or (type1_ok == 0): msg.printFatal("EvaluateMVA() is giving the same score to all events")
    
    print('''(\\                   (\/)''')
    print('''( '')     (\_/)      (.. )   //)''')
    print('''O(")(") (\\'.'/)'  '(")(")O (" )''')
    print('''         (")_(")           ()()o''')

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
    
    return tree
    

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




    #var_deltaR_tau_LightLep1 = array.array('f',[0]) ; reader.AddVariable("deltaR_tau_LightLep1", var_deltaR_tau_LightLep1)
    #var_DeltaRLeadingLeptonClosestBjet = array.array('f',[0]) ; reader.AddVariable("DeltaRLeadingLeptonClosestBjet", var_DeltaRLeadingLeptonClosestBjet)
    #var_deltaR_b_LightLep1 = array.array('f',[0]) ; reader.AddVariable("deltaR_b_LightLep1", var_deltaR_b_LightLep1)
    #var_deltaR_b_LightLep2 = array.array('f',[0]) ; reader.AddVariable("deltaR_b_LightLep1", var_deltaR_b_LightLep1)
    #var_deltaR_tau_LightLep2 = array.array('f',[0]) ; reader.AddVariable("deltaR_b_LightLep2", var_deltaR_b_LightLep2)
    #var_m_Hvis_opt1 = array.array('f',[0]) ; reader.AddVariable("m_Hvis_opt1", var_m_Hvis_opt1)
    #var_deltaEta_tau_LightLep2 = array.array('f',[0]) ; reader.AddVariable("deltaEta_tau_LightLep2", var_deltaEta_tau_LightLep2)
    #var_deltaEta_tau_LightLep1 = array.array('f',[0]) ; reader.AddVariable("deltaEta_tau_LightLep1", var_deltaEta_tau_LightLep1)
    #var_eventNumber = array.array('f',[0]) ; reader.AddSpectator("eventNumber", var_eventNumber) # the eventNumber is used for the splitExpr

# ==========
# main
# ========
if __name__ == '__main__':
  main(sys.argv[1:])


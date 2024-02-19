###################################################################################################################
#       Collecton of tools for the BDT-based method for the light-lepton assginment in the tHq(2lepSS+qtau)       #
###################################################################################################################

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


# =====================================================================
#  Tools for lepton assignment
# =====================================================================
class tools:
        
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
        
        msg.printDebug("Entries used with successfull labeling = %d" % tree.GetEntries("SS_LepHad == 1 && is_Lep1_from_TruthTop > -1"))
        msg.printDebug("Entries used for training = %d" % tree.GetEntries("SS_LepHad == 1 && is_Lep1_from_TruthTop > -1 && isTruthTopWLep ==1 && (isTruthHiggsTauTauLepHad==1 || isTruthHiggsWWLepHad==1)"))
        msg.printDebug("Entries used for training (without negatively weighted events) = %d" % tree.GetEntries("SS_LepHad == 1 && is_Lep1_from_TruthTop > -1 && isTruthTopWLep ==1 && (isTruthHiggsTauTauLepHad==1 || isTruthHiggsWWLepHad==1) && weight_nominal>0"))
    
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
            msg.printDebug("   - Removing negatively weighted events (weight_nominal>0)")
            mycut_type1 = mycut_type1 + ROOT.TCut("weight_nominal>0")
            mycut_type2 = mycut_type2 + ROOT.TCut("weight_nominal>0")
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
     
    def cutCollectionAll(debugLevel,tree):
        msg = msgServer('cutCollection', debugLevel)
        msg.printDebug("Preparing train and test trees for signal (type1) and backgorund (type2)")
        msg.printDebug(" Requirements for training:")
        msg.printDebug("   - Succesfull truth-reco matching (is_Lep1_from_TruthTop > -1)")
        msg.printDebug("   - Security check for truth-reco matching (minDeltaR_lep_2_truthlep < 0.01 && minDeltaR_lep_1_truthlep < 0.01)")
        msg.printDebug("   - Hadronic tau from Higgs (isTruthTopWLep==1)")
        msg.printDebug("   - H-> WW or H->TauTau (isTruthHiggsTauTauLepHad=1 or isTruthHiggsWWLepHad=1)")
        #selectionCut_SS = ROOT.TCut("is_Lep1_from_TruthTop > -1 && SS_LepHad == 1")
        selectionCut_SS = ROOT.TCut("is_Lep1_from_TruthTop > -1")
        selectionCut_Cones = ROOT.TCut("minDeltaR_lep_2_truthlep < 0.01 && minDeltaR_lep_1_truthlep < 0.01")
        selectionCut_Channels = ROOT.TCut("isTruthHiggsTauTauLepHad==1 || isTruthHiggsWWLepHad==1")
        selectionCut_TauFromHiggs = ROOT.TCut("isTruthTopWLep==1")
        mycuts = ROOT.TCut("is_Lep1_from_TruthTop==1") # Type 1: l1 from t and l2 from H
        mycutb = ROOT.TCut("is_Lep1_from_TruthTop==0") # Type 2: l1 from H and l2 from t
        mycut_type1 = mycuts + selectionCut_Cones + selectionCut_Channels + selectionCut_TauFromHiggs + selectionCut_SS #+ selectionCut_Channels
        mycut_type2 = mycutb + selectionCut_Cones + selectionCut_Channels + selectionCut_TauFromHiggs + selectionCut_SS #+ selectionCut_Channels
        removeNegWeight = False
        if removeNegWeight:
            msg.printDebug("   - Removing negatively weighted events (weight_nominal>0)")
            mycut_type1 = mycut_type1 + ROOT.TCut("weight_nominal>0")
            mycut_type2 = mycut_type2 + ROOT.TCut("weight_nominal>0")
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
    #  EvaluateAccuracy: Evaluates the classification accuracy of a model given a cut value
    # =====================================================================
    def EvaluateAccuracy(debugLevel, RecoLevelTree, BDT_cut):
        msg = msgServer('EvaluateAccuracy', debugLevel)
        type1_count = 0
        type1_ok = 0
        type2_count = 0
        type2_ok = 0
        
        tau_type1_count = 0
        tau_type1_ok = 0
        tau_type2_count = 0
        tau_type2_ok = 0

        WW_type1_count = 0
        WW_type1_ok = 0
        WW_type2_count = 0
        WW_type2_ok = 0
        for event in RecoLevelTree:
            if event.SS_LepHad==1 and (event.isTruthHiggsWWLepHad==1 or event.isTruthHiggsTauTauLepHad==1) and event.isTruthTopWLep==1:
                
                LeptAssign_PredictedBDT_val = event.LeptAssign_PredictedBDT_val
                is_Lep1_from_TruthTop = event.is_Lep1_from_TruthTop
                #print("LeptAssign_PredictedBDT_val ::" +str(LeptAssign_PredictedBDT_val))
                #print("is_Lep1_from_TruthTop ::" +str(is_Lep1_from_TruthTop))
        
                #Type2 event
                if event.is_Lep1_from_TruthTop == 0:
                    type2_count = type2_count + event.weight_nominal
                    if event.isTruthHiggsTauTauLepHad == 1: tau_type2_count = tau_type2_count + event.weight_nominal
                    if event.isTruthHiggsWWLepHad==1: WW_type2_count = WW_type2_count + event.weight_nominal
                    if LeptAssign_PredictedBDT_val < BDT_cut:
                        type2_ok = type2_ok + event.weight_nominal
                        if event.isTruthHiggsTauTauLepHad == 1: tau_type2_ok = tau_type2_ok + event.weight_nominal
                        if event.isTruthHiggsWWLepHad==1: WW_type2_ok = WW_type2_ok + event.weight_nominal
                #Type1 event
                if event.is_Lep1_from_TruthTop == 1:
                    type1_count = type1_count + event.weight_nominal
                    if event.isTruthHiggsTauTauLepHad == 1: tau_type1_count = tau_type1_count + event.weight_nominal
                    if event.isTruthHiggsWWLepHad==1: WW_type1_count = WW_type1_count + event.weight_nominal
                    if LeptAssign_PredictedBDT_val >= BDT_cut:
                        type1_ok = type1_ok + event.weight_nominal
                        if event.isTruthHiggsTauTauLepHad == 1: tau_type1_ok = tau_type1_ok + event.weight_nominal
                        if event.isTruthHiggsWWLepHad==1: WW_type1_ok = WW_type1_ok + event.weight_nominal
                else:
                    pass
                    #msg.printWarning("No truth matching avaiulable")
        
        msg.printDebug("Score evaluated")
        msg.printDebug("Type 1 events :: "+str(type1_count))
        msg.printDebug("Type 2 events :: "+str(type2_count))
        msg.printDebug("Type 1 correctly assigned :: "+str(type1_ok) + " ("+str(round(100* type1_ok/type1_count, 2))+"%)")
        msg.printDebug("Type 2 correctly assigned :: "+str(type2_ok) + " ("+str(round(100* type2_ok/type2_count, 2))+"%)")
        
        msg.printDebug("Type 1 events (H-> tau tau):: "+str(tau_type1_count))
        msg.printDebug("Type 2 events (H-> tau tau):: "+str(tau_type2_count))
        msg.printDebug("Type 1 correctly assigned (H-> tau tau):: "+str(tau_type1_ok) + " ("+str(round(100* tau_type1_ok/tau_type1_count, 2))+"%)")
        msg.printDebug("Type 2 correctly assigned (H-> tau tau):: "+str(tau_type2_ok) + " ("+str(round(100* tau_type2_ok/tau_type2_count, 2))+"%)")
        
        msg.printDebug("Type 1 events (H-> WW):: "+str(WW_type1_count))
        msg.printDebug("Type 2 events (H-> WW):: "+str(WW_type2_count))
        msg.printDebug("Type 1 correctly assigned (H-> WW):: "+str(WW_type1_ok) + " ("+str(round(100* WW_type1_ok/WW_type1_count, 2))+"%)")
        msg.printDebug("Type 2 correctly assigned (H-> WW):: "+str(WW_type2_ok) + " ("+str(round(100* WW_type2_ok/WW_type2_count, 2))+"%)")
        
        if debugLevel == 0:msg.printGreen(" General       \t => Accuracy = " + str(round(100*(type1_ok+type2_ok)/(type1_count + type2_count),2)) +"%")
        if debugLevel == 0:msg.printGreen(" (H-> tau tau) \t => Accuracy = " + str(round(100*(tau_type1_ok+tau_type2_ok)/(tau_type1_count + tau_type2_count),2)) +"%")
        if debugLevel == 0:msg.printGreen(" (H-> WW)      \t => Accuracy = " + str(round(100*(WW_type1_ok+WW_type2_ok)/(WW_type1_count + WW_type2_count),2)) +"%")
        
        msg.printDebug("Total H-> tau tau fraction :: "+ str(round(100*(tau_type1_count+tau_type2_count)/(tau_type1_count+tau_type2_count + WW_type1_count + WW_type2_count),2)) + "%")
        msg.printDebug("Total H-> WW      fraction :: "+ str(round(100*(WW_type1_count + WW_type2_count)/(tau_type1_count+tau_type2_count+ WW_type1_count + WW_type2_count),2)) + "%")
        
        #msg.printDebug("Fraction of correctly assigned :: " +str(100* (type2_ok+type1_ok)/(type1_count+type2_count))+"%")
        if debugLevel >0: print(" Cut = "+str(round(float(BDT_cut),3))+"\t => Accuracy = " + str(round(100*(type1_ok+type2_ok)/(type1_count + type2_count),2)) +"%")
        if (type2_ok == 0) or (type1_ok == 0): msg.printFatal("EvaluateMVA() is giving the same score to all events")
        
        
    
        return str(round(100*(type1_ok+type2_ok)/(type1_count + type2_count),2))
        
    # =====================================================================
    #  EvaluateBaselineAccuracy: Evaluates the classification accuracy of the baseline model
    # =====================================================================
    def EvaluateBaselineAccuracy(debugLevel, tree):
        msg = msgServer('EvaluateBaselineAccuracy', debugLevel)
        type1_count = 0
        type1_ok = 0
        type2_count = 0
        type2_ok = 0
        
        tau_type1_count = 0
        tau_type1_ok = 0
        tau_type2_count = 0
        tau_type2_ok = 0

        WW_type1_count = 0
        WW_type1_ok = 0
        WW_type2_count = 0
        WW_type2_ok = 0
        for event in tree:
            if event.SS_LepHad==1 and (event.isTruthHiggsWWLepHad==1 or event.isTruthHiggsTauTauLepHad==1) and event.isTruthTopWLep==1:
                
                LeptAssign_PredictedBDT_val = event.is_Lep1_from_TruthTop_BaseLine
                is_Lep1_from_TruthTop = event.is_Lep1_from_TruthTop
                #print("LeptAssign_PredictedBDT_val ::" +str(LeptAssign_PredictedBDT_val))
                #print("is_Lep1_from_TruthTop ::" +str(is_Lep1_from_TruthTop))
        
                #Type2 event
                if event.is_Lep1_from_TruthTop == 0:
                    if event.isTruthHiggsTauTauLepHad == 1: tau_type2_count = tau_type2_count + event.weight_nominal
                    if event.isTruthHiggsWWLepHad==1: WW_type2_count = WW_type2_count + event.weight_nominal
                    type2_count = type2_count + event.weight_nominal
                    if LeptAssign_PredictedBDT_val == 0:
                        type2_ok = type2_ok + event.weight_nominal
                        if event.isTruthHiggsTauTauLepHad == 1: tau_type2_ok = tau_type2_ok + event.weight_nominal
                        if event.isTruthHiggsWWLepHad==1: WW_type2_ok = WW_type2_ok + event.weight_nominal
                #Type1 event
                if event.is_Lep1_from_TruthTop == 1:
                    type1_count = type1_count + event.weight_nominal
                    if event.isTruthHiggsTauTauLepHad == 1: tau_type1_count = tau_type1_count + event.weight_nominal
                    if event.isTruthHiggsWWLepHad==1: WW_type1_count = WW_type1_count + event.weight_nominal
                    if LeptAssign_PredictedBDT_val == 1:
                        type1_ok = type1_ok + event.weight_nominal
                        if event.isTruthHiggsTauTauLepHad == 1: tau_type1_ok = tau_type1_ok + event.weight_nominal
                        if event.isTruthHiggsWWLepHad==1: WW_type1_ok = WW_type1_ok + event.weight_nominal
                else:
                    pass
                    #msg.printWarning("No truth matching avaiulable")
                    
        msg.printDebug("Type 1 events :: "+str(type1_count))
        msg.printDebug("Type 2 events :: "+str(type2_count))
        msg.printDebug("Type 1 correctly assigned :: "+str(type1_ok) + " ("+str(round(100* type1_ok/type1_count, 2))+"%)")
        msg.printDebug("Type 2 correctly assigned :: "+str(type2_ok) + " ("+str(round(100* type2_ok/type2_count, 2))+"%)")
        
        msg.printDebug("Type 1 events (H-> tau tau):: "+str(tau_type1_count))
        msg.printDebug("Type 2 events (H-> tau tau):: "+str(tau_type2_count))
        msg.printDebug("Type 1 correctly assigned (H-> tau tau):: "+str(tau_type1_ok) + " ("+str(round(100* tau_type1_ok/tau_type1_count, 2))+"%)")
        msg.printDebug("Type 2 correctly assigned (H-> tau tau):: "+str(tau_type2_ok) + " ("+str(round(100* tau_type2_ok/tau_type2_count, 2))+"%)")
        
        
        msg.printDebug("Type 1 events (H-> WW):: "+str(WW_type1_count))
        msg.printDebug("Type 2 events (H-> WW):: "+str(WW_type2_count))
        msg.printDebug("Type 1 correctly assigned (H-> WW):: "+str(WW_type1_ok) + " ("+str(round(100* WW_type1_ok/WW_type1_count, 2))+"%)")
        msg.printDebug("Type 2 correctly assigned (H-> WW):: "+str(WW_type2_ok) + " ("+str(round(100* WW_type2_ok/WW_type2_count, 2))+"%)")
        
        if debugLevel == 0:msg.printGreen(" General       \t => Accuracy = " + str(round(100*(type1_ok+type2_ok)/(type1_count + type2_count),2)) +"%")
        if debugLevel == 0:msg.printGreen(" (H-> tau tau) \t => Accuracy = " + str(round(100*(tau_type1_ok+tau_type2_ok)/(tau_type1_count + tau_type2_count),2)) +"%")
        if debugLevel == 0:msg.printGreen(" (H-> WW)      \t => Accuracy = " + str(round(100*(WW_type1_ok+WW_type2_ok)/(WW_type1_count + WW_type2_count),2)) +"%")
        
        if debugLevel >0: print(" Baseline method \t => Accuracy = " + str(round(100*(type1_ok+type2_ok)/(type1_count + type2_count),2)) +"%")
        

 
    # =====================================================================
    #  giraffe   :)
    # =====================================================================
    def giraffe():
        print("""\
    
                                       ._ o o
                                       \_`-)|_
                                    ,""       \ \n                                  ,"  ## |   ಠ ಠ.
                                ," ##   ,-\__    `.
                              ,"       /     `--._;)
                            ,"     ## /
                          ,"   ##    /


                    """)
        return
        
    # =====================================================================
    #  rabbits: Are these rabbits?
    # =====================================================================
    def rabbits():
        print('''(\\                   (\/)''')
        print('''( '')     (\_/)      (.. )   //)''')
        print('''O(")(") (\\'.'/)'  '(")(")O (" )''')
        print('''         (")_(")           ()()o''')
        return
    
    # =====================================================================
    #
    # =====================================================================
    def computing():
        print('''             | | ''')
        print('''             | |===( )   ////// ''')
        print('''             |_|   |||  | o o|  ''')
        print('''                    ||| ( c  )                  ____  ''')
        print('''                     ||| \= /                  ||   \_    ''')
        print('''                      ||||||                   ||     |   ''')
        print('''                      ||||||                ...||__/|-"   ''')
        print('''                      ||||||             __|________|__   ''')
        print('''                        |||             |______________|  ''')
        print('''                        |||             || ||      || ||  ''')
        print('''                        |||             || ||      || ||  ''')
        print('''------------------------|||-------------||-||------||-||------- ''')
        print('''                        |__>            || ||      || || ''')



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


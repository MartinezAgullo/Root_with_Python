#############################################################
#       Script to read the output of TMVA and produce a     #
#       plots with the BDT_Score of all the folds drawn3    #
#       simultaneosly.                                      #####################
#       To produce these plots, the output of TMVA_LeptonAssignment_Training.py #
#       has to include the "wieghts" and FoldFileOutput = True in the config.   #
#                                                                               #
#################################################################################
import os,sys
from ROOT import TFile, TTree, TChain
from ROOT import TCanvas, TNtuple, TH1F, TH2F, TF1, TLegend, TFile, TTree, THStack
from ROOT import TLatex, TAxis, TPaveText, TGaxis, TStyle
from ROOT import gROOT, gSystem, gStyle, gPad, gEnv
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
    parser.add_option("-f", "--filepath", dest="filepath", help="Path for the BDTG_foldN.root files", default = "/Users/pablo/Desktop/tHq_Analysis/3-LeptonAssigment/Script/")
    parser.add_option("-k", "--kFolds", dest="kFolds", help="Number of folds", default=5)
    parser.add_option("-n", "--name", dest="name", help="Add a label to the plot name", default = "")
    try:
        (options, args) = parser.parse_args()
    except:
        parser.print_help()
        exit()
    msg = msgServer('CompareFolds.py', options.debugLevel)

    if not os.path.exists(str(options.filepath)):
        msg.printFatal("The path " + str(filepath) + " does not exist.")
        msg.printInfo("Exiting")
        exit()

    PlotsFolder = "BDT_score_distributions"
    if not os.path.isdir(PlotsFolder):
        os.makedirs(PlotsFolder)
        msg.printInfo("Creating folder :" + str(PlotsFolder))
    name = options.name


    BDT_Score_Fold_1_Test = TH1F("BDTScore 1 test", "BDT 1", 20, -1, 1)
    BDT_Score_Fold_2_Test = TH1F("BDTScore 2 test", "BDT 2", 20, -1, 1)
    BDT_Score_Fold_3_Test = TH1F("BDTScore 3 test", "BDT 3", 20, -1, 1)
    BDT_Score_Fold_4_Test = TH1F("BDTScore 4 test", "BDT 4", 20, -1, 1)
    BDT_Score_Fold_5_Test = TH1F("BDTScore 5 test", "BDT 5", 20, -1, 1)
    BDT_Score_Fold_1_Train = TH1F("BDTScore 1 train", "BDT 1", 20, -1, 1)
    BDT_Score_Fold_2_Train = TH1F("BDTScore 2 train", "BDT 2", 20, -1, 1)
    BDT_Score_Fold_3_Train = TH1F("BDTScore 3 train", "BDT 3", 20, -1, 1)
    BDT_Score_Fold_4_Train = TH1F("BDTScore 4 train", "BDT 4", 20, -1, 1)
    BDT_Score_Fold_5_Train = TH1F("BDTScore 5 train", "BDT 5", 20, -1, 1)
    
    BDT_Score_Fold_1_Test_sig = TH1F("Type1 BDTScore 1 test ", "BDT 1", 20, -1, 1)
    BDT_Score_Fold_2_Test_sig = TH1F("Type1 BDTScore 2 test", "BDT 2", 20, -1, 1)
    BDT_Score_Fold_3_Test_sig = TH1F("Type1 BDTScore 3 test", "BDT 3", 20, -1, 1)
    BDT_Score_Fold_4_Test_sig = TH1F("Type1 BDTScore 4 test", "BDT 4", 20, -1, 1)
    BDT_Score_Fold_5_Test_sig = TH1F("Type1 BDTScore 5 test", "BDT 5", 20, -1, 1)
    BDT_Score_Fold_1_Train_sig = TH1F("Type1 BDTScore 1 train", "BDT 1", 20, -1, 1)
    BDT_Score_Fold_2_Train_sig = TH1F("Type1 BDTScore 2 train", "BDT 2", 20, -1, 1)
    BDT_Score_Fold_3_Train_sig = TH1F("Type1 BDTScore 3 train", "BDT 3", 20, -1, 1)
    BDT_Score_Fold_4_Train_sig = TH1F("Type1 BDTScore 4 train", "BDT 4", 20, -1, 1)
    BDT_Score_Fold_5_Train_sig = TH1F("Type1 BDTScore 5 train", "BDT 5", 20, -1, 1)
    
    BDT_Score_Fold_1_Test_bkg = TH1F("Type2 BDTScore 1 test ", "BDT 1", 20, -1, 1)
    BDT_Score_Fold_2_Test_bkg = TH1F("Type2 BDTScore 2 test", "BDT 2", 20, -1, 1)
    BDT_Score_Fold_3_Test_bkg = TH1F("Type2 BDTScore 3 test", "BDT 3", 20, -1, 1)
    BDT_Score_Fold_4_Test_bkg = TH1F("Type2 BDTScore 4 test", "BDT 4", 20, -1, 1)
    BDT_Score_Fold_5_Test_bkg = TH1F("Type2 BDTScore 5 test", "BDT 5", 20, -1, 1)
    BDT_Score_Fold_1_Train_bkg = TH1F("Type2 BDTScore 1 train", "BDT 1", 20, -1, 1)
    BDT_Score_Fold_2_Train_bkg = TH1F("Type2 BDTScore 2 train", "BDT 2", 20, -1, 1)
    BDT_Score_Fold_3_Train_bkg = TH1F("Type2 BDTScore 3 train", "BDT 3", 20, -1, 1)
    BDT_Score_Fold_4_Train_bkg = TH1F("Type2 BDTScore 4 train", "BDT 4", 20, -1, 1)
    BDT_Score_Fold_5_Train_bkg = TH1F("Type2 BDTScore 5 train", "BDT 5", 20, -1, 1)

    i = 0
    while i < options.kFolds:
        i =i+1
        file = options.filepath + "BDTG_fold" + str(i) +".root"
        if os.path.isfile(file): pass #msg.printInfo("Reading :: " + str(file))
        else: msg.printFatal("The file "+ str(file) + " does not exist")
        
       
    
    BDT_Score_Fold_1_Test = ReadFile_FillHisto_1(options.filepath + "BDTG_fold1.root", "TestTree", BDT_Score_Fold_1_Test, "BDTG_fold1", 0)
    BDT_Score_Fold_2_Test = ReadFile_FillHisto_2(options.filepath + "BDTG_fold2.root", "TestTree", BDT_Score_Fold_2_Test, "BDTG_fold2", 0)
    BDT_Score_Fold_3_Test = ReadFile_FillHisto_3(options.filepath + "BDTG_fold3.root", "TestTree", BDT_Score_Fold_3_Test, "BDTG_fold3", 0)
    BDT_Score_Fold_4_Test = ReadFile_FillHisto_4(options.filepath + "BDTG_fold4.root", "TestTree", BDT_Score_Fold_4_Test, "BDTG_fold4", 0)
    BDT_Score_Fold_5_Test = ReadFile_FillHisto_5(options.filepath + "BDTG_fold5.root", "TestTree", BDT_Score_Fold_5_Test, "BDTG_fold5", 0)
    BDT_Score_Fold_1_Train = ReadFile_FillHisto_1(options.filepath + "BDTG_fold1.root", "TrainTree", BDT_Score_Fold_1_Train, "BDTG_fold1", 0)
    BDT_Score_Fold_2_Train = ReadFile_FillHisto_2(options.filepath + "BDTG_fold2.root", "TrainTree", BDT_Score_Fold_2_Train, "BDTG_fold2", 0)
    BDT_Score_Fold_3_Train = ReadFile_FillHisto_3(options.filepath + "BDTG_fold3.root", "TrainTree", BDT_Score_Fold_3_Train, "BDTG_fold3", 0)
    BDT_Score_Fold_4_Train = ReadFile_FillHisto_4(options.filepath + "BDTG_fold4.root", "TrainTree", BDT_Score_Fold_4_Train, "BDTG_fold4", 0)
    BDT_Score_Fold_5_Train = ReadFile_FillHisto_5(options.filepath + "BDTG_fold5.root", "TrainTree", BDT_Score_Fold_5_Train, "BDTG_fold5", 0)
    
    
    BDT_Score_Fold_1_Test_sig = ReadFile_FillHisto_1(options.filepath + "BDTG_fold1.root", "TestTree", BDT_Score_Fold_1_Test, "BDTG_fold1", 1)
    BDT_Score_Fold_2_Test_sig = ReadFile_FillHisto_2(options.filepath + "BDTG_fold2.root", "TestTree", BDT_Score_Fold_2_Test, "BDTG_fold2", 1)
    BDT_Score_Fold_3_Test_sig = ReadFile_FillHisto_3(options.filepath + "BDTG_fold3.root", "TestTree", BDT_Score_Fold_3_Test, "BDTG_fold3", 1)
    BDT_Score_Fold_4_Test_sig = ReadFile_FillHisto_4(options.filepath + "BDTG_fold4.root", "TestTree", BDT_Score_Fold_4_Test, "BDTG_fold4", 1)
    BDT_Score_Fold_5_Test_sig = ReadFile_FillHisto_5(options.filepath + "BDTG_fold5.root", "TestTree", BDT_Score_Fold_5_Test, "BDTG_fold5", 1)
    BDT_Score_Fold_1_Train_sig = ReadFile_FillHisto_1(options.filepath + "BDTG_fold1.root", "TrainTree", BDT_Score_Fold_1_Train, "BDTG_fold1", 1)
    BDT_Score_Fold_2_Train_sig = ReadFile_FillHisto_2(options.filepath + "BDTG_fold2.root", "TrainTree", BDT_Score_Fold_2_Train, "BDTG_fold2", 1)
    BDT_Score_Fold_3_Train_sig = ReadFile_FillHisto_3(options.filepath + "BDTG_fold3.root", "TrainTree", BDT_Score_Fold_3_Train, "BDTG_fold3", 1)
    BDT_Score_Fold_4_Train_sig = ReadFile_FillHisto_4(options.filepath + "BDTG_fold4.root", "TrainTree", BDT_Score_Fold_4_Train, "BDTG_fold4", 1)
    BDT_Score_Fold_5_Train_sig = ReadFile_FillHisto_5(options.filepath + "BDTG_fold5.root", "TrainTree", BDT_Score_Fold_5_Train, "BDTG_fold5", 1)
    
    BDT_Score_Fold_1_Test_bkg = ReadFile_FillHisto_1(options.filepath + "BDTG_fold1.root", "TestTree", BDT_Score_Fold_1_Test, "BDTG_fold1", 2)
    BDT_Score_Fold_2_Test_bkg = ReadFile_FillHisto_2(options.filepath + "BDTG_fold2.root", "TestTree", BDT_Score_Fold_2_Test, "BDTG_fold2", 2)
    BDT_Score_Fold_3_Test_bkg = ReadFile_FillHisto_3(options.filepath + "BDTG_fold3.root", "TestTree", BDT_Score_Fold_3_Test, "BDTG_fold3", 2)
    BDT_Score_Fold_4_Test_bkg = ReadFile_FillHisto_4(options.filepath + "BDTG_fold4.root", "TestTree", BDT_Score_Fold_4_Test, "BDTG_fold4", 2)
    BDT_Score_Fold_5_Test_bkg = ReadFile_FillHisto_5(options.filepath + "BDTG_fold5.root", "TestTree", BDT_Score_Fold_5_Test, "BDTG_fold5", 2)
    BDT_Score_Fold_1_Train_bkg = ReadFile_FillHisto_1(options.filepath + "BDTG_fold1.root", "TrainTree", BDT_Score_Fold_1_Train, "BDTG_fold1", 2)
    BDT_Score_Fold_2_Train_bkg = ReadFile_FillHisto_2(options.filepath + "BDTG_fold2.root", "TrainTree", BDT_Score_Fold_2_Train, "BDTG_fold2", 2)
    BDT_Score_Fold_3_Train_bkg = ReadFile_FillHisto_3(options.filepath + "BDTG_fold3.root", "TrainTree", BDT_Score_Fold_3_Train, "BDTG_fold3", 2)
    BDT_Score_Fold_4_Train_bkg = ReadFile_FillHisto_4(options.filepath + "BDTG_fold4.root", "TrainTree", BDT_Score_Fold_4_Train, "BDTG_fold4", 2)
    BDT_Score_Fold_5_Train_bkg = ReadFile_FillHisto_5(options.filepath + "BDTG_fold5.root", "TrainTree", BDT_Score_Fold_5_Train, "BDTG_fold5", 2)
    
    gStyle.SetOptStat(0)
    Draw1Histo("BDT_Score_Fold1_test.pdf", "BDT score (BDT 1 - test)", BDT_Score_Fold_1_Test, name)
    Draw1Histo("BDT_Score_Fold2_test.pdf", "BDT score (BDT 2 - test)", BDT_Score_Fold_2_Test, name)
    Draw1Histo("BDT_Score_Fold3_test.pdf", "BDT score (BDT 3 - test)", BDT_Score_Fold_3_Test, name)
    Draw1Histo("BDT_Score_Fold4_test.pdf", "BDT score (BDT 4 - test)", BDT_Score_Fold_4_Test, name)
    Draw1Histo("BDT_Score_Fold5_test.pdf", "BDT score (BDT 5 - test)", BDT_Score_Fold_5_Test, name)
    Draw1Histo("BDT_Score_Fold1_train.pdf", "BDT score (BDT 1 - train)", BDT_Score_Fold_1_Train, name)
    Draw1Histo("BDT_Score_Fold2_train.pdf", "BDT score (BDT 2 - test)", BDT_Score_Fold_2_Train, name)
    Draw1Histo("BDT_Score_Fold3_train.pdf", "BDT score (BDT 3 - test)", BDT_Score_Fold_3_Train, name)
    Draw1Histo("BDT_Score_Fold4_train.pdf", "BDT score (BDT 4 - test)", BDT_Score_Fold_4_Train, name)
    Draw1Histo("BDT_Score_Fold5_train.pdf", "BDT score (BDT 5 - test)", BDT_Score_Fold_5_Train, name)
    
    if False:
        Draw1Histo("Z_Type1_BDT_Score_Fold1_test.pdf", "BDT score (type1 - BDT 1 - test)", BDT_Score_Fold_1_Test_sig, name)
        Draw1Histo("Z_Type1_BDT_Score_Fold2_test.pdf", "BDT score (type1 - BDT 2 - test)", BDT_Score_Fold_2_Test_sig, name)
        Draw1Histo("Z_Type1_BDT_Score_Fold3_test.pdf", "BDT score (type1 - BDT 3 - test)", BDT_Score_Fold_3_Test_sig, name)
        Draw1Histo("Z_Type1_BDT_Score_Fold4_test.pdf", "BDT score (type1 - BDT 4 - test)", BDT_Score_Fold_4_Test_sig, name)
        Draw1Histo("Z_Type1_BDT_Score_Fold5_test.pdf", "BDT score (type1 - BDT 5 - test)", BDT_Score_Fold_5_Test_sig, name)
        Draw1Histo("Z_Type1_BDT_Score_Fold1_train.pdf", "BDT score (type1 - BDT 1 - train)", BDT_Score_Fold_1_Train_sig, name)
        Draw1Histo("Z_Type1_BDT_Score_Fold2_train.pdf", "BDT score (type1 - BDT 2 - test)", BDT_Score_Fold_2_Train_sig, name)
        Draw1Histo("Z_Type1_BDT_Score_Fold3_train.pdf", "BDT score (type1 - BDT 3 - test)", BDT_Score_Fold_3_Train_sig, name)
        Draw1Histo("Z_Type1_BDT_Score_Fold4_train.pdf", "BDT score (type1 - BDT 4 - test)", BDT_Score_Fold_4_Train_sig, name)
        Draw1Histo("Z_Type1_BDT_Score_Fold5_train.pdf", "BDT score (type1 - BDT 5 - test)", BDT_Score_Fold_5_Train_sig, name)
    
        Draw1Histo("Z_Type2_BDT_Score_Fold1_test.pdf", "BDT score (type2 - BDT 1 - test)", BDT_Score_Fold_1_Test_bkg, name)
        Draw1Histo("Z_Type2_BDT_Score_Fold2_test.pdf", "BDT score (type2 - BDT 2 - test)", BDT_Score_Fold_2_Test_bkg, name)
        Draw1Histo("Z_Type2_BDT_Score_Fold3_test.pdf", "BDT score (type2 - BDT 3 - test)", BDT_Score_Fold_3_Test_bkg, name)
        Draw1Histo("Z_Type2_BDT_Score_Fold4_test.pdf", "BDT score (type2 - BDT 4 - test)", BDT_Score_Fold_4_Test_bkg, name)
        Draw1Histo("Z_Type2_BDT_Score_Fold5_test.pdf", "BDT score (type2 - BDT 5 - test)", BDT_Score_Fold_5_Test_bkg, name)
        Draw1Histo("Z_Type2_BDT_Score_Fold1_train.pdf", "BDT score (type2 - BDT 1 - train)", BDT_Score_Fold_1_Train_bkg, name)
        Draw1Histo("Z_Type2_BDT_Score_Fold2_train.pdf", "BDT score (type2 - BDT 2 - test)", BDT_Score_Fold_2_Train_bkg, name)
        Draw1Histo("Z_Type2_BDT_Score_Fold3_train.pdf", "BDT score (type2 - BDT 3 - test)", BDT_Score_Fold_3_Train_bkg, name)
        Draw1Histo("Z_Type2_BDT_Score_Fold4_train.pdf", "BDT score (type2 - BDT 4 - test)", BDT_Score_Fold_4_Train_bkg, name)
        Draw1Histo("Z_Type2_BDT_Score_Fold5_train.pdf", "BDT score (type2 - BDT 5 - test)", BDT_Score_Fold_5_Train_bkg, name)
    

    Draw5Histos("0_BDT_Score_ALL_test.pdf", "Test samples","BDT score", BDT_Score_Fold_1_Test, BDT_Score_Fold_2_Test, BDT_Score_Fold_3_Test, BDT_Score_Fold_4_Test, BDT_Score_Fold_5_Test, name)
    
    Draw5Histos("0_BDT_Score_ALL_train.pdf", "Train samples","BDT score", BDT_Score_Fold_1_Train, BDT_Score_Fold_2_Train, BDT_Score_Fold_3_Train, BDT_Score_Fold_4_Train, BDT_Score_Fold_5_Train, name)
    
    if False:
        Draw5Histos("1_BDT_Score_ALL_test_Type1.pdf", "Test samples","BDT score", BDT_Score_Fold_1_Test_sig, BDT_Score_Fold_2_Test_sig, BDT_Score_Fold_3_Test_sig, BDT_Score_Fold_4_Test_sig, BDT_Score_Fold_5_Test_sig, name)
        Draw5Histos("1_BDT_Score_ALL_test_Type2.pdf", "Test samples","BDT score", BDT_Score_Fold_1_Test_bkg, BDT_Score_Fold_2_Test_bkg, BDT_Score_Fold_3_Test_bkg, BDT_Score_Fold_4_Test_bkg, BDT_Score_Fold_5_Test_bkg, name)
        Draw5Histos("1_BDT_Score_ALL_train_Type1.pdf", "Train samples","BDT score", BDT_Score_Fold_1_Train_sig, BDT_Score_Fold_2_Train_sig, BDT_Score_Fold_3_Train_sig, BDT_Score_Fold_4_Train_sig, BDT_Score_Fold_5_Train_sig, name)
        Draw5Histos("1_BDT_Score_ALL_train_Type2.pdf", "Train samples","BDT score", BDT_Score_Fold_1_Train_bkg, BDT_Score_Fold_2_Train_bkg, BDT_Score_Fold_3_Train_bkg, BDT_Score_Fold_4_Train_bkg, BDT_Score_Fold_5_Train_bkg, name)
   

        
    
    
# =====================================================================
# Draw5Histograms
# =====================================================================
def Draw5Histos(name,tittle,X_axis, h1, h2, h3, h4, h5, label):
    c = TCanvas(name, name, 800, 600)
    c.cd()
    h1.GetXaxis().SetTitle(X_axis)
    h1.Scale(1/h1.GetSumOfWeights())
    h2.Scale(1/h2.GetSumOfWeights())
    h3.Scale(1/h3.GetSumOfWeights())
    h4.Scale(1/h4.GetSumOfWeights())
    h5.Scale(1/h5.GetSumOfWeights())
    h1.SetLineColor(1)
    h2.SetLineColor(2)
    h3.SetLineColor(3)
    h4.SetLineColor(4)
    h5.SetLineColor(5)
    h1.Draw()
    h2.Draw("SAME")
    h3.Draw("SAME")
    h4.Draw("SAME")
    h5.Draw("SAME")
    c.BuildLegend()
    h1.SetTitle(tittle)
    c.Update()
    if label == "" : c.SaveAs("BDT_score_distributions/"+name)
    else: c.SaveAs("BDT_score_distributions/"+label+"_"+name)
  
def Draw1Histo(name, X_axis, histo, label):
    c = TCanvas(name, name, 800, 600)
    c.cd()
    histo.GetXaxis().SetTitle(X_axis)
    histo.Scale(1/histo.GetSumOfWeights())
    histo.SetLineColor(1)
    histo.SetLineWidth(1)
    histo.Draw("B E C")
    #c.BuildLegend()
    c.Update()
    if label == "" : c.SaveAs("BDT_score_distributions/"+name)
    else: c.SaveAs("BDT_score_distributions/"+label+"_"+name)
    c.Close()
    
# =====================================================================
# ReadFile_FillHisto
# =====================================================================
def ReadFile_FillHisto(file, treeName, histogram, branch, debugLevel):
    msg = msgServer('ReadFile_FillHisto',debugLevel)
    inFile = TFile.Open(file, 'read') #TFile *_file0 = TFile::Open("BDTG_fold1.root")
    msg.printInfo("Reading :: " + str(file))
    directory = inFile.Get("dataset;1")
    tree = directory.Get(treeName)  # In this case the root file contains a folder
                                    # where the trees are. Access this dir first.
    #tree.Print()
    for event in tree:
        histogram.Fill(event.BDTG_fold1)
        # histogram.Fill(event.BDTG_fold1, event.weight_nominal) Not storing the weights
    inFile.Close()
        
    return histogram
    
def ReadFile_FillHisto_1(file, treeName, histogram, branch, type = 0):
    inFile = TFile.Open(file, 'read')
    directory = inFile.Get("dataset;1")
    tree = directory.Get(treeName)
    for event in tree:
        if type == 0: histogram.Fill(event.BDTG_fold1, event.weight_nominal)
        elif type == 1 and event.is_Lep1_from_TruthTop == 1: histogram.Fill(event.BDTG_fold1, event.weight_nominal)
        elif type == 2 and event.is_Lep1_from_TruthTop == 0: histogram.Fill(event.BDTG_fold1, event.weight_nominal)
    if type not in [0, 1, 2]: prin("Error with 'Event type'")
    inFile.Close()
    return histogram
    
def ReadFile_FillHisto_2(file, treeName, histogram, branch, type = 0):
    inFile = TFile.Open(file, 'read')
    directory = inFile.Get("dataset;1")
    tree = directory.Get(treeName)
    for event in tree:
        if type == 0: histogram.Fill(event.BDTG_fold2, event.weight_nominal)
        elif type == 1 and event.is_Lep1_from_TruthTop == 1: histogram.Fill(event.BDTG_fold2, event.weight_nominal)
        elif type == 2 and event.is_Lep1_from_TruthTop == 0: histogram.Fill(event.BDTG_fold2, event.weight_nominal)
    if type not in [0, 1, 2]: prin("Error with 'Event type'")
    inFile.Close()
    return histogram
    
def ReadFile_FillHisto_3(file, treeName, histogram, branch, type = 0):
    inFile = TFile.Open(file, 'read')
    directory = inFile.Get("dataset;1")
    tree = directory.Get(treeName)
    for event in tree:
        if type == 0: histogram.Fill(event.BDTG_fold3, event.weight_nominal)
        elif type == 1 and event.is_Lep1_from_TruthTop == 1: histogram.Fill(event.BDTG_fold3, event.weight_nominal)
        elif type == 2 and event.is_Lep1_from_TruthTop == 0: histogram.Fill(event.BDTG_fold3, event.weight_nominal)
    if type not in [0, 1, 2]: prin("Error with 'Event type'")
    inFile.Close()
    return histogram
    
def ReadFile_FillHisto_4(file, treeName, histogram, branch, type = 0):
    inFile = TFile.Open(file, 'read')
    directory = inFile.Get("dataset;1")
    tree = directory.Get(treeName)
    for event in tree:
        if type == 0: histogram.Fill(event.BDTG_fold4, event.weight_nominal)
        elif type == 1 and event.is_Lep1_from_TruthTop == 1: histogram.Fill(event.BDTG_fold4, event.weight_nominal)
        elif type == 2 and event.is_Lep1_from_TruthTop == 0: histogram.Fill(event.BDTG_fold4, event.weight_nominal)
    if type not in [0, 1, 2]: prin("Error with 'Event type'")
    inFile.Close()
    return histogram
    
def ReadFile_FillHisto_5(file, treeName, histogram, branch, type = 0):
    inFile = TFile.Open(file, 'read')
    directory = inFile.Get("dataset;1")
    tree = directory.Get(treeName)
    for event in tree:
        if type == 0: histogram.Fill(event.BDTG_fold5, event.weight_nominal)
        elif type == 1 and event.is_Lep1_from_TruthTop == 1: histogram.Fill(event.BDTG_fold5, event.weight_nominal)
        elif type == 2 and event.is_Lep1_from_TruthTop == 0: histogram.Fill(event.BDTG_fold5, event.weight_nominal)
    if type not in [0, 1, 2]: prin("Error with 'Event type'")
    inFile.Close()
    return histogram


# ==========
# main
# ========
if __name__ == '__main__':
  main(sys.argv[1:])


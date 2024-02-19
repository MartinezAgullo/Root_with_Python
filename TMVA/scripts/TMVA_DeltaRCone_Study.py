#########################################################################
#       Script to study the Delta R cones in the truth-reco matching    #
#                                                                       #
#################################################################################
import os,sys
from ROOT import TFile, TTree, TChain, TCut
from ROOT import TCanvas, TNtuple, TH1F, TH2F, TF1, TLegend, TFile, TTree, THStack
from ROOT import TLatex, TAxis, TPaveText, TGaxis, TStyle
from ROOT import gROOT, gSystem, gStyle, gPad, gEnv
import ROOT
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
    parser.add_option("-f", "--filepath", dest="filepath", help="Path for the samples", default = "/Users/pablo/Desktop/tHq_Analysis/2-LeptonAssigment/Studies/samples_2024/")
    parser.add_option("-n", "--name", dest="name", help="Add a label to the plot name", default = "")
    try:
        (options, args) = parser.parse_args()
    except:
        parser.print_help()
        exit()
    msg = msgServer('CompareFolds.py', options.debugLevel)

    PlotsFolder = "DeltaR_Study"
    if not os.path.isdir(PlotsFolder):
        os.makedirs(PlotsFolder)
        msg.printInfo("Creating folder :" + str(PlotsFolder))

    name = options.name
    filepath = options.filepath
    treeName = "tHqLoop_nominal_Loose"
    tree = tools.Loader(options.debugLevel,filepath, treeName)
    
    
    tools.Stats(tree)
    
    # Conditions for LeptonAssignment
    #match_condition = TCut("minDeltaR_lep_1_truthlep","SS_LepHad == 1 && isTruthTopWLep==1 && ( isTruthHiggsWWLepHad==1 || isTruthHiggsTauTauLepHad==1) && minDeltaR_lep_1_truthlep < 0.1 && minDeltaR_lep_2_truthlep < 0.1 ")
    
        
    TH1_minDeltaR_lep_1_A = TH1F("minDeltaR_lep_1_truthlep_A", "", 35, 0, 0.1)
    TH1_minDeltaR_lep_1_B = TH1F("minDeltaR_lep_1_truthlep_B", "", 35, 0, 0.007)
    TH1_minDeltaR_lep_1_C = TH1F("minDeltaR_lep_1_truthlep_C", "", 35, 0, 0.002)
    
    TH1_minDeltaR_lep_2_A = TH1F("minDeltaR_lep_2_truthlep_A", "", 35, 0, 0.1)
    TH1_minDeltaR_lep_2_B = TH1F("minDeltaR_lep_2_truthlep_B", "", 35, 0, 0.007)
    TH1_minDeltaR_lep_2_C = TH1F("minDeltaR_lep_2_truthlep_C", "", 35, 0, 0.002)

    #print(tree)
    for event in tree:
        #print(event.minDeltaR_lep_1_truthlep)
        if event.minDeltaR_lep_1_truthlep < 0.2 and event.isTruthTopWLep==1 and event.SS_LepHad == 1:
            TH1_minDeltaR_lep_1_A.Fill(event.minDeltaR_lep_1_truthlep)
            TH1_minDeltaR_lep_1_B.Fill(event.minDeltaR_lep_1_truthlep)
            TH1_minDeltaR_lep_1_C.Fill(event.minDeltaR_lep_1_truthlep)
            TH1_minDeltaR_lep_2_A.Fill(event.minDeltaR_lep_2_truthlep)
            TH1_minDeltaR_lep_2_B.Fill(event.minDeltaR_lep_2_truthlep)
            TH1_minDeltaR_lep_2_C.Fill(event.minDeltaR_lep_2_truthlep)
            
    Draw1Histo("Lep_1_Zoom_0", "\DeltaR(lep^{reco}_{1}, lep^{truth}_{clossest})", TH1_minDeltaR_lep_1_A, "SS_only_TruthTopWLep_better", PlotsFolder)
    Draw1Histo("Lep_1_Zoom_1", "\DeltaR(lep^{reco}_{1}, lep^{truth}_{clossest})", TH1_minDeltaR_lep_1_B, "SS_only_TruthTopWLep_better", PlotsFolder)
    Draw1Histo("Lep_1_Zoom_2", "\\DeltaR(lep^{reco}_{1}, lep^{truth}_{clossest})", TH1_minDeltaR_lep_1_C, "SS_only_TruthTopWLep_better", PlotsFolder)

    Draw1Histo("Lep_2_Zoom_0", "\DeltaR(lep^{reco}_{2}, lep^{truth}_{clossest})", TH1_minDeltaR_lep_2_A, "SS_only_TruthTopWLep_better", PlotsFolder)
    Draw1Histo("Lep_2_Zoom_1", "\DeltaR(lep^{reco}_{2}, lep^{truth}_{clossest})", TH1_minDeltaR_lep_2_B, "SS_only_TruthTopWLep_better", PlotsFolder)
    Draw1Histo("Lep_2_Zoom_2", "\DeltaR(lep^{reco}_{2}, lep^{truth}_{clossest})", TH1_minDeltaR_lep_2_C, "SS_only_TruthTopWLep_better", PlotsFolder)

        
  
  
def Draw1Histo(name, X_axis, histo, label, PlotsFolder):
    c = TCanvas(name, name, 650, 500)
    c.cd()
    histo.GetXaxis().SetTitle(X_axis)
    histo.GetYaxis().SetTitle("Normalised raw entries")
    histo.Scale(1/histo.GetSumOfWeights())
    histo.GetXaxis().SetNdivisions(508)
    histo.GetXaxis().SetTitleOffset(1.2)
    histo.SetLineColor(1)
    histo.SetLineWidth(1)
    histo.SetFillColor(38)
    histo.Draw("HIST F")
    gStyle.SetOptStat(0)
    latex = ROOT.TLatex()
    latex.SetNDC(True)  # Ensure we're using normalized coordinates
    latex.SetTextAlign(13)  # Align text to the top and left
    latex.SetTextSize(0.04)  # Adjust text size as needed
    
    # Position inside the canvas, adjust these values as needed
    x_pos = 0.65  # Horizontal position, left side
    y_pos = 0.85  # Vertical position, near the top but inside
    latex.DrawLatex(x_pos, y_pos, "#it{tHq} 2l(SS)+1#tau_{had}")
    latex.DrawLatex(x_pos, 0.80, "\sqrt{s}=13TeV")
    latex.DrawLatex(x_pos, 0.75, "140 fb^{-1}")
    latex.DrawLatex(x_pos, 0.75, "140 fb^{-1}")
    #latex.DrawLatex(x_pos, 0.80, "#splitline{\sqrt{s}=13TeV}{140 fb^{-1}}")
    #c.BuildLegend()
    c.Update()
    if label == "" : c.SaveAs(PlotsFolder+"/"+name+".pdf")
    else: c.SaveAs(PlotsFolder+"/"+label+"_"+name+".pdf")
    c.Close()
    




# ==========
# main
# ========
if __name__ == '__main__':
  main(sys.argv[1:])


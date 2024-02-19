###########################################################
#       Plot pt_lep1 y pt_lep2 in a single histo          #
#       separating type1 and type2                        #
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
    
    filepath = "/Users/pablo/Desktop/tHq_Analysis/3-LeptonAssigment/Studies/SamplesDir_backup/"
    treeName = "tHqLoop_nominal_Loose"
    tree = tools.Loader(options.debugLevel,filepath, treeName)
    
    tree_type1, tree_type2 = tools.cutCollection(options.debugLevel, tree)
    
    h1_ptLep1_type1 = ROOT.TH1F("Lep1 type1", "Type 1 l1", 40, 0, 300)
    h1_ptLep2_type1 = ROOT.TH1F("Lep2 type1", "Type 1 l2", 40, 0, 300)
    h1_ptLep1_type2 = ROOT.TH1F("Lep1 type2", "Type 2 l1", 40, 0, 300)
    h1_ptLep2_type2 = ROOT.TH1F("Lep2 type2", "Type 2 l2", 40, 0, 300)
    
    #Stack histograms
    hs_pt_type1 = ROOT.THStack("Type 1 :: Lep1 and Lep2 stacked", "Type 1")
    hs_pt_type2 = ROOT.THStack("Type 2 :: Lep2 and Lep2 stacked", "Type 2")
    
    for event in tree_type1:
        h1_ptLep1_type1.Fill(event.pt_lep1,event.weight_nominal)
        h1_ptLep2_type1.Fill(event.pt_lep2,event.weight_nominal)
    for event in tree_type2:
        h1_ptLep1_type2.Fill(event.pt_lep1,event.weight_nominal)
        h1_ptLep2_type2.Fill(event.pt_lep2,event.weight_nominal)

    
    
    c = ROOT.TCanvas("pT_L1andL2", "pT_L1andL2", 700, 500)
    c.cd()
    h1_ptLep1_type1.GetXaxis().SetTitle("p_{T} [GeV]")
    h1_ptLep1_type1.SetLineColor(4)
    h1_ptLep2_type1.SetLineColor(4)
    h1_ptLep1_type2.SetLineColor(2)
    h1_ptLep2_type2.SetLineColor(2)
    #h1_ptLep1_type1.Draw("H")
    #h1_ptLep1_type2.Draw("H SAME")
    #h1_ptLep2_type1.Draw("H SAME")
    #h1_ptLep2_type2.Draw("H SAME")
    print("h1_ptLep1_type1.GetSumOfWeights() :: "+str(h1_ptLep1_type1.GetSumOfWeights()))
    print("h1_ptLep2_type1.GetSumOfWeights() :: "+str(h1_ptLep2_type1.GetSumOfWeights()))
    print("h1_ptLep1_type2.GetSumOfWeights() :: "+str(h1_ptLep1_type2.GetSumOfWeights()))
    print("h1_ptLep2_type2.GetSumOfWeights() :: "+str(h1_ptLep2_type2.GetSumOfWeights()))
    print(h1_ptLep1_type1.GetSumOfWeights()+h1_ptLep2_type1.GetSumOfWeights()) # = 01463925382591924
    print(h1_ptLep1_type2.GetSumOfWeights()+h1_ptLep2_type2.GetSumOfWeights()) # = 0.004793500396090167
    h1_ptLep1_type1.Scale(1/0.01463925382591924)
    h1_ptLep2_type1.Scale(1/0.01463925382591924)
    h1_ptLep1_type2.Scale(1/0.004793500396090167)
    h1_ptLep2_type2.Scale(1/0.004793500396090167)
    
    hs_pt_type1.Add(h1_ptLep1_type1)
    hs_pt_type1.Add(h1_ptLep2_type1)
    hs_pt_type2.Add(h1_ptLep1_type2)
    hs_pt_type2.Add(h1_ptLep2_type2)
    hs_pt_type2.Draw("H nostack")
    
    hs_pt_type2.GetXaxis().SetTitle("p_{T} (type2) [GeV]")
    hs_pt_type2.SetTitle("p_{T} distributions of the light leptons in type2 events")
    #hs_pt_type1.SetTitle("p_{T} distributions of the light leptons")
    #c.BuildLegend()
    c.Update()
    c.SaveAs("pT_ofLightLeptons_Type2.pdf")
    
    hs_pt_type1.Draw("H nostack")
    hs_pt_type1.GetXaxis().SetTitle("p_{T} (type1) [GeV]")
    hs_pt_type1.SetTitle("p_{T} distributions of the light leptons in type1 events")
    c.Update()
    c.SaveAs("pT_ofLightLeptons_Type1.pdf")
    
    hs_pt_type2.Draw("H nostack SAME")
    c.Update()
    c.SaveAs("pT_ofLightLeptons_bothTypes.pdf")

# ==========
# main
# ========
if __name__ == '__main__':
  main(sys.argv[1:])


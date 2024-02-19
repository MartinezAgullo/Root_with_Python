import os,sys
from ROOT import TFile, TTree, TChain
from ROOT import TCanvas, TNtuple, TH1F, TH2F, TF1, TLegend, TFile, TTree, THStack
from ROOT import TLatex, TAxis, TPaveText, TGaxis, TStyle
from ROOT import gROOT, gSystem, gStyle, gPad, gEnv, gRandom
from optparse import OptionParser

#########################################################################################################
##                  Script to compare the distributions for two different samples                      ##
#########################################################################################################


# =================================================================================
#  main
# =================================================================================
def main(argv):
    parser = OptionParser()
    parser.add_option("-t", "--tree-name", dest="treeName",  help="set the tree name to process (default: %default)")
    parser.add_option("-a", "--dir1", dest="inputdir", help= "Directory of the sample 1")
    parser.add_option("-b", "--dir2", dest= "output",  help= "Directory of the sample 2")

    parser.set_defaults(treeName = 'tHqLoop_nominal_Loose', directory1 = '/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/v34_2l1HadTau_PLVTight_PreBDT_Selection/nominal_Loose/', directory2 = '/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/v34_2l1HadTau_PLVTight_PreBDT_Selection_ReScaledWeights/nominal_Loose/')
    
    try:
        (options, args) = parser.parse_args()
    except:
        parser.print_help()
        exit()

    tree = options.treeName
    dir1Name = options.directory1
    dir2Name = options.directory2


    if not os.path.exists(dir1Name): print("WARNING: The directory '" + str(dir1Name) + "' does not exist")
    if not os.path.exists(dir2Name): print("WARNING: The directory '" + str(dir2Name) + "' does not exist")

    #showStats = False
    #style_name = StyleATLAS(0, showStats)
    #gROOT.SetStyle("Plain")
    #gROOT.SetStyle("style_name")
    gStyle.SetOptStat(0)



    #Fill the chains
    Chain1 = TChain("tHqLoop_nominal_Loose","")
    Chain2 = TChain("tHqLoop_nominal_Loose","")
    for file in os.listdir(dir1Name):
        file_path1 = dir1Name + str(file) + str("/") + tree
        Chain1.Add(file_path1)

    for file in os.listdir(dir2Name):
        file_path2 = dir2Name + str(file) + str("/") + tree
        Chain2.Add(file_path2)

    #Fill histos
    MET1_h1 = TH1F("MET", "MET", 50,0,250)
    MET2_h1 = TH1F("MET_ReWeighted", "MET_ReWeighted", 50,0,250)
    Weight1_h1 = TH1F("Weight_original", "Weight_original", 50, -0.0001, 0.0001)
    Weight2_h1 = TH1F("Weight_ReScaled", "Weight_ReScaled", 50, -0.0001, 0.0001)
    if not Chain1.GetEntries() == Chain2.GetEntries():
        print("WARNING: Different amount of events between folders")
        print("Entries in " + str(dir1Name)  + ": " + str(Chain1.GetEntries()))
        print("Entries in " + str(dir2Name)  + ": " + str(Chain2.GetEntries()))

    print("Filling histograms")
    for event in Chain1:
        MET1_h1.Fill(event.m_met, event.weight_nominal)
        Weight1_h1.Fill(event.weight_nominal)

    for event in Chain2:
        MET2_h1.Fill(event.m_met, event.weight_nominal)
        Weight2_h1.Fill(event.weight_nominal)

    #Draw    
    print("Drawing")
    Draw2Hists(MET1_h1, MET2_h1, "MET", "MET_ScaleComparison.pdf", 3, 5)
    Draw2Hists(Weight1_h1, Weight2_h1, "Weight_nominal", "Weight_ScaleComparison.pdf", 3, 5)

    
# =====================================================================
# Draw2Hists 
# =====================================================================
def Draw2Hists(Hist1,Hist2, X_axis, name, color1, color2):
    c = TCanvas(name, name, 800, 600)
    c.cd()
    Hist1.GetXaxis().SetTitle(X_axis)
    Hist1.Scale(1/Hist1.GetSumOfWeights())
    Hist2.Scale(1/Hist2.GetSumOfWeights())
    Hist1.SetLineColor(color1)
    Hist1.SetLineWidth(1)
    Hist2.SetLineColor(color2)
    Hist2.SetLineWidth(1)
    Hist1.Draw()
    Hist2.Draw("SAME")
    c.BuildLegend()
    c.Update()
    c.SaveAs(name)
    c.Close()




# =================================================================================
#  __main__
# =================================================================================
if __name__ == '__main__':
  main(sys.argv[1:])

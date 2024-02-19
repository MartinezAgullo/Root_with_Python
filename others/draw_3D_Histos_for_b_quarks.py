import os, sys
from ROOT import gROOT
from ROOT import TFile, TChain, TTree, TBranch, TLorentzVector, Math, TCut, TCanvas, gROOT, TH1F, TH1, TH2F, TPie, TEllipse, TPad, TMath, TLegend, TColor, THStack, TLine
from ROOT import TLatex, TStyle, gStyle, gPad
from ROOT import kBlack, kWhite, kGray, kBlue, kAzure, kCyan, kTeal, kGreen, kSpring, kYellow, kOrange, kRed, kPink, kMagenta, kViolet
import time

#########################################################################################################
##   Script to draw 3D histograms pt vs eta simultaneusly for MC_spectator_b_quark and  MC_b_from_T    ##
######################################################################################################### 



# =====================================================================
#  main
# ====================================================================
def main(name):
    gROOT.Reset()
    gROOT.SetBatch(0)
    #gROOT.SetBatch(1)

    inFileName = name
    inFile = TFile.Open (inFileName," READ ")
    tree = inFile.Get ("truth")
    #inFile.Print()

    style_name = StyleATLAS(0, True)
    gROOT.SetStyle("Plain")
    gROOT.SetStyle("style_name")

    
    h2_b_from_t_eta_pt = TH2F("b_from_t_eta_pt", "b_from_t_eta_pt", 20, -6., 6., 20, 0., 200.)
    h2_secondb_afterFSR_eta_pt = TH2F("secondb_afterFSR_eta_pt", "secondb_afterFSR_eta_pt", 20, -6., 6., 20, 0., 200.)
    h2_test = TH2F("secondb_afterFSR_eta_pt", "secondb_afterFSR_eta_pt", 20, -6., 6., 20, 0., 200.)
    
    h2_b_from_t_pt_eta = TH2F("b_from_t_pt_eta", "b_from_t_pt_eta",  20, 0., 200.,  20, -6., 6.)
    h2_secondb_afterFSR_pt_eta = TH2F("secondb_afterFSR_pt_eta","secondb_afterFSR_pt_eta",  20, 0., 200.,  20, -6., 6.)
    #for event in range (0 , tree.GetEntries ()):
        #tree.GetEntry(event)
    for event in tree:
        h2_b_from_t_eta_pt.Fill(event.MC_b_from_t_eta, event.MC_b_from_t_pt/1000.)
        h2_secondb_afterFSR_eta_pt.Fill(event.MC_secondb_afterFSR_eta, event.MC_secondb_afterFSR_pt/1000.)
        #print str(event.MC_secondb_afterFSR_pt/1000.)
        h2_test.Fill(event.MC_secondb_afterFSR_eta, event.MC_secondb_afterFSR_pt/1000.)
        h2_b_from_t_pt_eta.Fill(event.MC_b_from_t_pt/1000., event.MC_b_from_t_eta)
        h2_secondb_afterFSR_pt_eta.Fill(event.MC_secondb_afterFSR_pt/1000., event.MC_secondb_afterFSR_eta)

    
    #h1_b_from_t_eta = h2_b_from_t_eta_pt.ProjectionX()
    #h1_b_from_t_pt = h2_b_from_t_eta_pt.ProjectionY()
    #h1_b_from_t_pt.Draw()
    #h1_b_from_t_eta.Draw()

    l1 = TLine(-2.5, 20., -2.5, 200.)
    l2 = TLine(2.5, 20., 2.5, 200.)
    l3 = TLine(-2.5, 20., 2.5, 20.)
    
    l = TLine()

    h2_b_from_t_eta_pt.GetYaxis().SetTitle("p_{T} (GeV)")
    h2_b_from_t_eta_pt.GetXaxis().SetTitle("#eta")
    h2_secondb_afterFSR_eta_pt.GetYaxis().SetTitle("p_{T} (GeV)")
    h2_secondb_afterFSR_eta_pt.GetXaxis().SetTitle("#eta")
    h2_b_from_t_pt_eta.GetXaxis().SetTitle("p_{T} (GeV)")
    h2_b_from_t_pt_eta.GetYaxis().SetTitle("#eta")
    h2_secondb_afterFSR_pt_eta.GetXaxis().SetTitle("p_{T} (GeV)")
    h2_secondb_afterFSR_pt_eta.GetYaxis().SetTitle("#eta")



    c1_a = TCanvas("atlas-square_B", "b_from_t", 800, 600)
    c1_a.cd()
    h2_b_from_t_eta_pt.Draw("COLZ")
    l.DrawLine(-2.5, 20., -2.5, 200.)
    l.DrawLine(2.5, 20., 2.5, 200.)
    l.DrawLine(-2.5, 20., 2.5, 20.)
    c1_a.Update()
    c1_a.SaveAs("plots/h2_b_from_t_eta_pt.png")
    


    c1_b = TCanvas("atlas-square_A", "secondb_afterFSR",  800, 600)
    c1_b.cd()
    h2_secondb_afterFSR_eta_pt.Draw("COLZ")
    l.DrawLine(-2.5, 20., -2.5, 200.)
    l.DrawLine(2.5, 20., 2.5, 200.)
    l.DrawLine(-2.5, 20., 2.5, 20.)
    c1_b.Update()
    c1_b.SaveAs("plots/h2_secondb_afterFSR_eta_pt.png")

    style_name = StyleATLAS(0, False)
    gROOT.SetStyle("Plain")
    gROOT.SetStyle("style_name")
    
    
    c_comb = TCanvas("atlas-square_c", "Comparision",  800, 600)
    c_comb.cd()
    h2_b_from_t_eta_pt.SetMarkerColor(kRed)
    h2_b_from_t_eta_pt.Draw("SCAT")
    c_comb.Update()
    h2_secondb_afterFSR_eta_pt.SetMarkerColor(kBlue)
    h2_secondb_afterFSR_eta_pt.Draw("SCAT")
    h2_secondb_afterFSR_eta_pt.Draw("SAME")
    c_comb.Update()
    c_comb.SaveAs("plots/b_quark_Comb.png")

    c_comb2 = TCanvas("atlas-square_Comb", "Comparision_",  800, 600)
    c_comb2.cd()
    h2_b_from_t_eta_pt.SetMarkerColor(kRed)
    h2_b_from_t_eta_pt.Draw("LEGO")
    c_comb2.Update()
    h2_secondb_afterFSR_eta_pt.SetMarkerColor(kBlue)
    h2_secondb_afterFSR_eta_pt.Draw("LEGOSAME")
    #h2_secondb_afterFSR_eta_pt.Draw("SAME")
    c_comb2.Update()
    c_comb2.SaveAs("plots/b_quark_Comb_Lego.png")
    
    hs = THStack("hs","");
    c_comb3 = TCanvas("atlas-square_c", "Comparision_Stack",  800, 600)
    c_comb3.cd()
    h2_b_from_t_eta_pt.SetFillColor(kRed);
    hs.Add(h2_b_from_t_eta_pt)
    h2_secondb_afterFSR_eta_pt.SetMarkerColor(kBlue)    
    hs.Add(h2_secondb_afterFSR_eta_pt)
    hs.Draw()
    c_comb3.Update()
    c_comb3.SaveAs("plots/b_quark_Stack_Default.png")
    hs.Draw("nostack")
    c_comb3.Update()
    c_comb3.SaveAs("plots/b_quark_Stack_NonStack.png")
    hs.Draw("nostackb")
    c_comb2.Update()
    c_comb3.SaveAs("plots/b_quark_Stack_NonStackB.png")
    hs.Draw("lego1")
    c_comb2.Update()
    c_comb3.SaveAs("plots/b_quark_Stack_Lego.png")


    legend = TLegend()
    legend.AddEntry(h2_test,"MC_spectator_b","f")
    legend.AddEntry(h2_b_from_t_eta_pt,"MC_b_from_t","f")

    
    c_comb4 = TCanvas("atlas-square_c", "Comparision_2D_Stack_new",  800, 600)
    c_comb4.cd()
    gPad.SetFrameFillColor(17)
    a = THStack("a","Stacked 2D histograms")
    h2_test.SetFillColor(38)
    h2_b_from_t_eta_pt.SetFillColor(46)
    a.Add(h2_test)
    a.Add(h2_b_from_t_eta_pt)
    a.Draw()
    legend.Draw()
    c_comb4.SaveAs("plots/b_quark_Comb_Stack.png")
    l.DrawLine(-2.5, 20., -2.5, 200.)
    l.DrawLine(2.5, 20., 2.5, 200.)
    l.DrawLine(-2.5, 20., 2.5, 20.)
    c_comb4.Update()
    c_comb4.SaveAs("plots/b_quark_Comb_Stack_Lines.png")
    out_file = TFile("plots/b_quark_Comb_Stack.root", 'recreate')
    a.Write()
    out_file.Close()


    legend_1 = TLegend()
    legend_1.AddEntry(h2_secondb_afterFSR_pt_eta,"MC_spectator_b","f")
    legend_1.AddEntry(h2_b_from_t_pt_eta,"MC_b_from_t","f")
    c_comb5 =  TCanvas("atlas-square_inv", "Comparision_2D_Stack_inv",  800, 600)
    c_comb5.cd()
    b = THStack("b","Stacked 2D histograms_new")
    h2_secondb_afterFSR_pt_eta.SetFillColor(38)
    h2_b_from_t_pt_eta.SetFillColor(46)
    b.Add(h2_b_from_t_pt_eta)
    b.Add(h2_secondb_afterFSR_pt_eta)
    b.Draw()
    legend_1.Draw()
    c_comb5.SaveAs("plots/b_quark_Comb_Stack_inverted.png")





# =====================================================================
#  StyleATLAS()
# =====================================================================
def StyleATLAS(icol, showStats):
       
    atlasStyle = TStyle("style_name","Atlas style")
    
    # use plain black on white colors
    atlasStyle.SetFrameBorderMode(icol)
    atlasStyle.SetCanvasBorderMode(icol)
    atlasStyle.SetPadBorderMode(icol)
    atlasStyle.SetPadColor(icol)
    atlasStyle.SetCanvasColor(icol)
    atlasStyle.SetStatColor(icol)
    #atlasStyle.SetFillColor(icol)

    # set the paper & margin sizes
    atlasStyle.SetPaperSize(20,26)
    atlasStyle.SetPadTopMargin(0.05)
    atlasStyle.SetPadRightMargin(0.05)
    atlasStyle.SetPadBottomMargin(0.16)
    atlasStyle.SetPadLeftMargin(0.14)
    
    # use large fonts
    font=42
    tsize=0.04
    atlasStyle.SetTextFont(font)
    atlasStyle.SetTextSize(tsize)
    atlasStyle.SetLabelFont(font,"x")
    atlasStyle.SetTitleFont(font,"x")
    atlasStyle.SetLabelFont(font,"y")
    atlasStyle.SetTitleFont(font,"y")
    atlasStyle.SetLabelFont(font,"z")
    atlasStyle.SetTitleFont(font,"z")

    atlasStyle.SetLabelSize(tsize,"x")
    atlasStyle.SetTitleSize(tsize,"x")
    atlasStyle.SetLabelSize(tsize,"y")
    atlasStyle.SetTitleSize(tsize,"y")
    atlasStyle.SetLabelSize(tsize,"z")
    atlasStyle.SetTitleSize(tsize,"z")

    #use bold lines and markers
    atlasStyle.SetMarkerStyle(20)
    atlasStyle.SetMarkerSize(1.2)
    atlasStyle.SetHistLineWidth(2)
    atlasStyle.SetLineStyleString(2,"[12 12]") # postscript dashes

    #get rid of X error bars and y error bar caps
    #atlasStyle.SetErrorX(0.001)

    #do not display any of the standard histogram decorations
    atlasStyle.SetOptTitle(0)
    if showStats: atlasStyle.SetOptStat(11111111)
    else: atlasStyle.SetOptStat(0)
    #atlasStyle.SetOptFit(0)
    #atlasStyle.SetOptFit(1111)
        
    # put tick marks on top and RHS of plots
    atlasStyle.SetPadTickX(1)
    atlasStyle.SetPadTickY(1)
    
    # this is to ensure that all histograms are created with the sum of weights
    TH1F.SetDefaultSumw2()
    
    return atlasStyle






# =================================================================================
#  __main__
# =================================================================================
if __name__ == '__main__':
  main(sys.argv[1])

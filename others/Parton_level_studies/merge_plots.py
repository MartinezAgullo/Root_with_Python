#!/usr/bin/env python

import os, sys, commands, glob
import math, ROOT
from optparse import OptionParser
from ROOT import gROOT, gStyle, gPad
from ROOT import TStyle, TCanvas, TH1F, TLatex, TLegend
from ROOT import kWhite, kBlue, kGray

# https://twiki.cern.ch/twiki/bin/view/AtlasProtected/PubComPlotStyle#ROOT_Style_for_official_ATLAS_pl
#sys.path.append('../../AtlasStyle')
#ROOT.gROOT.LoadMacro("figures/AtlasStyle/AtlasStyle.C")
#ROOT.gROOT.LoadMacro("figures/AtlasStyle/AtlasUtils.C")
ROOT.gROOT.SetStyle("ATLAS")

# =================================================================================
#  getAllObjects
# =================================================================================
def getAllObjects(f):
    "Generator function to recurse into a ROOT file/dir and yield (path, obj) pairs"
    for key in f.GetListOfKeys():
        kname = key.GetName()
        yield '/'+kname, f.Get(kname)

# =================================================================================
#  getMaximumYaxis
# =================================================================================
def getMaximumYaxis(i):
    maxYvalue = 0.0
    for SR in SRs:
      fname = './'+outputdir+'/root/1D_'+SR+'_'+i
      rootFile = ROOT.TFile.Open(fname, 'read')
      hlist = []
      for k, o in getAllObjects(rootFile):
        # print o.ClassName(), k
        hlist += [k[1:]]

        if len(hlist) == 1:           
          # print hlist[0]
          h = rootFile.Get(hlist[0])
          maxYvalue = h.GetBinContent(h.GetMaximumBin())
          # print maxYvalue
      rootFile.Close()
    return maxYvalue
            
# =================================================================================
#  main
# =================================================================================
def main(argv):   
    parser = OptionParser()
    parser.add_option("--interactive", action="store_true", dest="interactive",
                          help="run 4TruthHistos interactively")
    parser.add_option("-y", "--yields", action="store_true", dest="yields",
                          help="show yields in the legend")
    try: (options, args) = parser.parse_args()
    except:
        parser.print_help()
        exit()
        
    gROOT.Reset()
    if options.interactive: gROOT.SetBatch(0)
    else: gROOT.SetBatch(1)

    style_name = StyleATLAS(0)
    gROOT.SetStyle("Plain")
    gROOT.SetStyle("style_name")
    gROOT.ForceStyle()

    global outputdir
    outputdir = "./parton_truth_plots"
    
    # signal regions
    global SRs
    SRs = ['3L', '3L1HadTau']
    
    common_histos = []
    for SR in SRs:
        for ifile in glob.iglob(r'./'+outputdir+'/root/1D_%s_*.root' % SR):
            #print(ifile)
            common_histos += [(ifile.split('/')[-1]).replace('1D_'+SR+'_', '')]

    for x in set(common_histos): common_histos.remove(x)
    duplicates = list(set(common_histos))
    # print duplicates
    for i in sorted(duplicates):
        
        # define canvas
        c = TCanvas(i, i, 800, 600)
        c.cd()

        # legend
        if options.yields: legend = TLegend(0.58,0.65,0.95,0.91)
        else: legend = TLegend(0.67,0.73,0.93,0.91)
        # legend.SetTextSize(0.035)
        legend.SetMargin(0.22)
        legend.SetTextFont(42)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        # legend.SetHeader("The Legend Title","C"); // option "C" allows to center the header

        # get maximum value for the Y axis
        maxYvalue = getMaximumYaxis(i)
      
        for idx,SR in enumerate(SRs):
          fname = './'+outputdir+'/root/1D_'+SR+'_'+i
          # print "%01d :: " % idx + fname
          rootFile = ROOT.TFile.Open(fname, 'read')
          #rootFile.ls()
          hlist = []

          for k, o in getAllObjects(rootFile):
            #print o.ClassName(), k
            hlist += [k[1:]]

          if len(hlist) == 1:           
            #print hlist[0]
            h = rootFile.Get(hlist[0])
            #print h.GetEntries()
            h.SetMarkerSize(0)
            h.SetLineWidth(1)
            if idx == 0:
              h.GetYaxis().SetRangeUser(0, 1.5*maxYvalue)
              h.SetLineColor(1)
              #print "->",h.GetName()
              h.DrawCopy('HISTO')
            else:
              h.SetLineColor(2)
              h.SetLineStyle(2)
              #print "->",h.GetName()
              h.DrawCopy('HISTO SAME')

            # uncertainty band
            h_uncertainty = h.Clone("h_"+i+"_"+SR+"_uncertainty")
            h_uncertainty.SetMarkerSize(0)
            h_uncertainty.SetLineColor(0)
            if idx == 0: h_uncertainty.SetFillColor(1)
            else: h_uncertainty.SetFillColor(2)
            h_uncertainty.SetFillStyle(3256)
            h_uncertainty.DrawCopy("E2 SAME")

            #if options.yields: legend.AddEntry(h, "tHq ("+SR+")  ::  " + str(h.GetEntries()), "l")
            if options.yields: legend.AddEntry(h, "tHq ("+SR+")  ::  " + str(h.GetSumOfWeights()), "l")
            else: legend.AddEntry(h, "tHq ("+SR+")", "l")

          legend.AddEntry(h_uncertainty, "MC uncertainty", "f")
          legend.Draw()

          # labels
          labelPos = [ 0.20, 0.88 ]
          ATLASLabel(labelPos[0], labelPos[1], "Simulation Internal")
          customLabel(labelPos[0], labelPos[1]-0.05, "#sqrt{s} = 13 TeV")
          
          c.Update()
          if idx+1 == len(SRs):
            # update and save canvas
            # c.GetListOfPrimitives().Print()
            c.Update()
            c.SaveAs(outputdir+'/pdf/'+'comb_'+i.replace('.root','')+'.pdf')
          
          if options.interactive:
            try: input("Press enter to continue")
            except SyntaxError: pass

        rootFile.Close()

        #print
        #break

# =====================================================================
#  ATLASLabel()
# =====================================================================
def ATLASLabel(x, y, text, size=0.04, color=1):
    # customLabel(x, y, "#bf{#it{ATLAS}} %s" % text, size, color)
    customLabel(x, y, "#bf{#it{aMC@NLO}} %s" % text, size, color)
        
# =====================================================================
#  customLabelWithAngle()
# =====================================================================
def customLabelWithAngle(x, y, text, angle, size=0.04, color=1):
    l = TLatex()
    l.SetTextAngle(angle);
    l.SetTextFont(42)
    l.SetTextSize(size)
    l.SetTextColor(color)
    l.SetNDC()
    l.DrawLatex(x,y,text)

# =====================================================================
#  customLabel()
# =====================================================================
def customLabel(x, y, text, size=0.04, color=1):
    l = TLatex()
    l.SetTextFont(42)
    l.SetTextSize(size)
    l.SetTextColor(color)
    l.SetNDC()
    l.DrawLatex(x,y,str(text))

# =====================================================================
#  StyleATLAS()
# =====================================================================
def StyleATLAS(icol):
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
    atlasStyle.SetOptStat(0)
    #atlasStyle.SetOptStat(11111111)
    atlasStyle.SetOptFit(0)
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
  main(sys.argv[1:])

from ROOT import TFile, TChain, TTree, TBranch, TLorentzVector, Math, TCut, TCanvas, gROOT, TH1F, TH1, TH2F, TPie, TEllipse, TPad, TMath, TLegend, TColor
from ROOT import TLatex, TStyle, gStyle
from ROOT import kBlack, kWhite, kGray, kBlue, kAzure, kCyan, kTeal, kGreen, kSpring, kYellow, kOrange, kRed, kPink, kMagenta, kViolet
from MsgHelper import msgServer
import math, sys, time, operator
from os import path, makedirs
from array import array

import warnings
warnings.filterwarnings( action='ignore', category=RuntimeWarning, message='creating converter.*' )

# =====================================================================
#  Tools for Truth
# =====================================================================
class tools:
    def __init__(self, options, config):
        self.msg = msgServer('ToolsForTruth', options.debugLevel)
        self.maxevents = options.maxevents

        self.config = config
        self.interactive = options.interactive

        self.normalize = 'entries'
        if options.normlumi: self.normalize = 'lumi'
        elif options.nonorm: self.normalize = 'nonorm'

        self.titleAxisY = "Events"
        if self.normalize == 'entries': self.titleAxisY = "Fraction of events"
            
        self.outputformat = []
        if 'all' in options.outputformat: self.outputformat = [ 'png', 'pdf', 'root' ]
        else:
            for out in options.outputformat.split(','): self.outputformat += [ out ]

        self.channel = 'Unknown'

    # =====================================================================                                     
    #  getParticlePairName
    # =====================================================================      
    def getParticlePairName(self, pdgNum):
        # particle pairs
        if pdgNum == 6.5: return "ss"
        elif pdgNum == 8.5: return "cc"
        elif pdgNum == 10.5: return "bb"            
        elif pdgNum == 26.5: return "#mu#mu"
        elif pdgNum == 30.5: return "#tau#tau"
        elif pdgNum == 42.5: return "gg"
        elif pdgNum == 44.5: return "#gamma#gamma"
        elif pdgNum == 45.5: return "Z#gamma"
        elif pdgNum == 46.5: return "ZZ*"
        elif pdgNum == 48.5: return "WW*"
        else: return "Unknown"
            
    # =====================================================================                                     
    #  getParticleName
    # =====================================================================      
    def getParticleName(self, pdgNum):
        #print 'pdgNum',pdgNum

        # particles
        if pdgNum == 1.5: return "d"
        elif pdgNum == 2.5: return "u"
        elif pdgNum == 3.5: return "s"
        elif pdgNum == 4.5: return "c"
        elif pdgNum == 5.5: return "b"
        elif pdgNum == 6.5: return "t"
        elif pdgNum == 11.5: return "e^{-}"
        elif pdgNum == 13.5: return "#mu^{-}"
        elif pdgNum == 15.5: return "#tau^{-}"
        elif pdgNum == 12.5: return "#nu_{e}"
        elif pdgNum == 14.5: return "#nu_{#mu}"
        elif pdgNum == 16.5: return "#nu_{#tau}"
        elif pdgNum == 23.5: return "Z"
        elif pdgNum == 24.5: return "W^{+}"

        # anti particles
        elif pdgNum == -0.5: return "#bar{d}"
        elif pdgNum == -1.5: return "#bar{u}"
        elif pdgNum == -2.5: return "#bar{s}"
        elif pdgNum == -3.5: return "#bar{c}"
        elif pdgNum == -4.5: return "#bar{b}"
        elif pdgNum == -5.5: return "#bar{t}"
        elif pdgNum == -10.5: return "e^{+}"
        elif pdgNum == -12.5: return "#mu^{+}"
        elif pdgNum == -14.5: return "#tau^{+}"
        elif pdgNum == -11.5: return "#bar{#nu}_{e}"
        elif pdgNum == -13.5: return "#bar{#nu}_{#mu}"
        elif pdgNum == -15.5: return "#bar{#nu}_{#tau}"
        elif pdgNum == -22.5: return "Z"
        elif pdgNum == -23.5: return "W^{-}"

        else: return "Unknown"

    # =====================================================================                                     
    #  getColor
    # =====================================================================      
    def getColor(self, key):
        colordict = {}

        colordict["u"] = kYellow
        colordict["#bar{u}"] = kYellow+1
        colordict["c"] = kOrange+5
        colordict["#bar{c}"] = kOrange+6
        colordict["t"] = 920
        colordict["#bar{t}"] = 921
        
        colordict["d"] = kMagenta
        colordict["#bar{d}"] = kMagenta+1
        colordict["s"] = kPink+9
        colordict["#bar{s}"] = kPink+10
        colordict["b"] = kRed
        colordict["#bar{b}"] = kRed+1
        
        colordict["e^{-}"] = kCyan
        colordict["#mu^{-}"] = kAzure+10
        colordict["#tau^{-}"] = kBlue
        colordict["e^{+}"] = colordict["e^{-}"]+1
        colordict["#mu^{+}"] = colordict["#mu^{-}"]-4
        colordict["#tau^{+}"] = colordict["#tau^{-}"]+2
        
        colordict["#nu_{e}"] = colordict["e^{-}"]-10
        colordict["#nu_{#mu}"] = colordict["#mu^{-}"]-19
        colordict["#nu_{#tau}"] = colordict["#tau^{-}"]-9
        colordict["#bar{#nu}_{e}"] = colordict["e^{-}"]-8
        colordict["#bar{#nu}_{#mu}"] = colordict["#mu^{-}"]-18
        colordict["#bar{#nu}_{#tau}"] = colordict["#tau^{-}"]-10
        
        colordict["W^{+}"] = kGreen+1
        colordict["W^{-}"] = colordict["W^{+}"]+2
        colordict["Z"] = 95

        # particle pair
        colordict["ss"] = colordict["s"]
        colordict["cc"] = colordict["c"]
        colordict["bb"] = colordict["b"]
        colordict["#mu#mu"] = colordict["#mu^{-}"]
        colordict["#tau#tau"] = colordict["#tau^{-}"]
        colordict["gg"] = 920
        colordict["#gamma#gamma"] = 923
        colordict["Z#gamma"] = colordict["Z"]-3
        colordict["ZZ*"] = colordict["Z"]
        colordict["WW*"] = colordict["W^{+}"]
        
        # unknown
        colordict["Unknown"] = 0

        return colordict[key]
        
    # =====================================================================                                     
    #  DeltaPhi between two particles
    # =====================================================================      
    def DeltaPhi(self,l1,l2):
        delta_phi = l1.Phi() - l2.Phi()
        while delta_phi >= math.pi: delta_phi = delta_phi - math.pi
        while delta_phi < -math.pi: delta_phi = delta_phi + math.pi
        return delta_phi
        
    # =====================================================================                                                               
    #  DeltaR between two particles                                      
    # ===================================================================== 
    def DeltaR(self,l1,l2):
        delta_phi = self.DeltaPhi(l1,l2)
        delta_eta = l1.Eta()-l2.Eta()
        deltaR = math.sqrt(delta_eta*delta_eta + delta_phi*delta_phi)
        return deltaR

    # =====================================================================
    #  DeltaDecayBjet: Returns a list where each element has [TLorentz,pdgID,parentPdgID,DeltaR,DeltaPhi,DeltaEta]
    # ===================================================================== 
    def DeltaDecayBjet(self, l1,l2,l3,l4):
        particles = [l1,l2,l3,l4]
        particles = sorted(particles,key = lambda particles: particles[-1])
        if particles[0][-1] == 5:
            b_jet = particles[0]
        eta_b = b_jet[0].Eta()
        phi_b = b_jet[0].Phi()
        particles = particles[1:]
        for p in particles:
            delta_eta = eta_b - p[0].Eta()
            delta_phi = self.DeltaPhi(b_jet[0],p[0])
            deltaR = self.DeltaR(b_jet[0],p[0])
            p.append(deltaR)
            p.append(delta_phi)
            p.append(delta_eta)
        return particles
        
    # =====================================================================
    #  Draw2DHisto()
    # =====================================================================
    def Draw2DHisto(self, h2, SR, DrawOption, value):
        start_drawOne = time.time()
        h2.GetXaxis().SetTitle(str(value[1]))
        h2.GetYaxis().SetTitle(str(value[2]))
        self.msg.printDebug("Drawing 2D_"+str(SR)+"_"+str(value[0]))

        # define canvas
        c = TCanvas("atlas-square", str(value[0]), 600, 600)
        h2.Draw(DrawOption)
        # Let's comment this by now because its not displayed properly (TO DO: review)
        #self.ATLASLabel(0.03, 0.9, "Simulation Internal", 0.08, 1)
        #self.customLabel(0.03, 0.9, "#sqrt{s} = 13 TeV, 139 fb^{#minus1}", 0.08, 1)
        #self.customLabel(0.03, 0.9, str(value[3]), 0.08, 1)

        # update and save canvas
        c.Update()
        self.Save("2D_"+str(SR)+"_"+str(value[0]), self.config.save_directory, c, h2)
                      
        end_drawOne = time.time()
        self.msg.printDebug("2D_"+str(SR)+"_"+str(value[0])+" saved. Time: " + str((end_drawOne - start_drawOne)/60) + " min")

        if self.interactive:
            try: input("Press enter to continue")
            except SyntaxError: pass

    # =====================================================================
    #  getBinWidth()
    # =====================================================================
    def getBinWidth(self, binWidth):
        binWidthText = "%2.2f" % binWidth
        if float(binWidthText.split('.')[1]) == 0: return "%2.0f" % binWidth
        elif (binWidthText.split('.')[1]).endswith('0'): return "%2.1f" % binWidth
        return binWidthText
        
    # =====================================================================
    #  DrawOneBasic()
    # =====================================================================
    def DrawOneBasic(self, h, SR, value, name):
        start_drawOne = time.time()
        units = str(value[5])
        if value[5] == "MeV":
            units = "GeV"
            h.GetXaxis().SetTitle(value[0] + " ["+units+"]")
            h.GetYaxis().SetTitle(self.titleAxisY + " / "+ self.getBinWidth((value[3]-value[2])/(1000 *value[1])) + " " + units)
        elif value[5] == "" or value[5] == " ":
            h.GetXaxis().SetTitle(value[0])
            h.GetYaxis().SetTitle(self.titleAxisY + " / "+ self.getBinWidth((value[3]-value[2])/value[1]))
        else:
            h.GetXaxis().SetTitle(value[0] + " ["+units+"]")
            h.GetYaxis().SetTitle(self.titleAxisY + " / "+ self.getBinWidth((value[3]-value[2])/value[1]) + " " + units)

        # define canvas
        c = TCanvas(str(name)+str(SR), str(name)+str(SR), 800, 600)
        c.cd()

        if self.normalize == 'lumi':
            # this needs to be fixed!!!!!
            xsec = 73 #fb
            totalLumi_mc16a = 140 #fb-1
            denom = h.GetEntries()
            if denom == 0:
                self.msg.printWarning("The histogram " + str(name) +" in " + str(SR) + " is empty!")
                denom = 1
            norm = xsec * totalLumi_mc16a / denom
            h.Scale(norm)
        elif self.normalize == 'entries':
            #print 'h.GetSumOfWeights()',h.GetSumOfWeights()
            #print 'h.GetEntries()',h.GetEntries()
            #print 'h.GetSumw2N()',h.GetSumw2N()
            #print 'h.Integral()',h.Integral()
            if h.GetSumOfWeights() > 0: h.Scale(1/h.GetSumOfWeights())
            #if h.GetEntries() > 0: h.Scale(1/h.GetEntries())

        #h.GetYaxis().SetRangeUser(0, 1.5*h.GetBinContent(h.GetMaximumBin()))
        h.SetMarkerSize(0)
        h.SetLineColor(1)
        h.SetLineWidth(1)
        h.Draw('HISTO')

        # print again the histogram in order to see below the Stats panel
        if gROOT.GetStyle("style_name").GetOptStat() > 0: h.Draw('HISTO SAME')

        # uncertainty band
        h_uncertainty = h.Clone("h_uncertainty")
        h_uncertainty.SetMarkerSize(0)
        h_uncertainty.SetLineColor(0)
        h_uncertainty.SetFillColor(1)
        h_uncertainty.SetFillStyle(3256)
        h_uncertainty.Draw("E2 SAME")

        # labels
        labelPos = [ 0.19, 0.88 ]
        self.ATLASLabel(labelPos[0], labelPos[1], "Simulation Internal")
        if self.normalize == 'lumi': self.customLabel(labelPos[0], labelPos[1]-0.05, "#sqrt{s} = 13 TeV, 139 fb^{#minus1}")
        elif self.normalize == 'entries': self.customLabel(labelPos[0], labelPos[1]-0.05, "#sqrt{s} = 13 TeV")
        else:
            self.customLabel(labelPos[0], labelPos[1]-0.05, "#sqrt{s} = 13 TeV")
            self.customLabelWithAngle(0.96, 0.95, "Not normalised", 270, 0.04, 2)
        self.customLabel(labelPos[0], labelPos[1]-0.10, str(SR))

        # legend
        legend = TLegend(0.67,0.78,0.92,0.93)
        # legend.SetTextSize(0.035)
        legend.SetMargin(0.22)
        legend.SetTextFont(42)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        # legend.SetHeader("The Legend Title","C"); // option "C" allows to center the header
        legend.AddEntry(h, "tHq", "l")
        legend.AddEntry(h_uncertainty, "MC uncertainty", "f")
        legend.Draw()
        
        # update and save canvas
        c.Update()
        self.Save("1D_"+str(SR)+"_"+str(name), self.config.save_directory, c, h)

        end_drawOne = time.time()
        self.msg.printDebug("1D_"+str(SR)+"_"+str(name)+" saved. Time: " + str((end_drawOne - start_drawOne)/60) + " min")

        if self.interactive:
            try: input("Press enter to continue")
            except SyntaxError: pass

        c.Close()

    # =====================================================================
    #  DrawDonutsForHiggsDecay()
    # =====================================================================
    def DrawDonutsForHiggsDecay(self, histosInSR):
        for SR, histolist in histosInSR.iteritems():
            # print 'SR',SR
            if SR != 'common': continue
            i = 0
            for key, value in sorted(self.config.HistogramDetails_common.iteritems()):
                #print str(i) + ". " + key
                
                if key != "MC_H_decay" and key != "MC_H_decay_weights":
                    #print 'key',key
                    i = i+1
                    continue

                info = {}
                # print 'histolist[i].GetName()',histolist[i].GetName()
                for ibin in range(1, histolist[i].GetXaxis().GetNbins()+1):
                    if histolist[i].GetBinContent(ibin) > 0:
                            info[self.getParticlePairName(histolist[i].GetXaxis().GetBinCenter(ibin))] = histolist[i].GetBinContent(ibin)
                            #print histolist[i].GetXaxis().GetBinCenter(ibin)
                            #print self.getParticlePairName(histolist[i].GetXaxis().GetBinCenter(ibin))

                # prepare donut chart
                if len(info) > 0:

                    names = []
                    vals = []
                    cols = []
                
                    total = 0.0
                
                    for key1 in sorted(info, key=info.get, reverse=True):
                         #print(key1, '->', info[key1])
                         total += float(info[key1])

                    #print ' -------------------'
                    #print ' - total',total
                    #print ' -------------------'

                    if total == 0.0:
                        i = i+1
                        continue
                    
                    for key2 in sorted(info, key=info.get, reverse=True):
                        #print " - name ->",key2
                        #print "->",float(info[key2])
                        #print "-> (%)",(100*float(info[key2])/total)
                        #print "->",getColor(key2)
                        names.append(key2)
                        vals.append(100*float(info[key2])/float(total))
                        cols.append(self.getColor(key2))
                        
                    values = array('d', vals)
                    colors = array('i', cols)

                    histoname = "%s" % (key)

                    # define canvas
                    c_donut = TCanvas("donut_%s" % histoname, "donut_%s" % histoname, 800, 450)
                    c_donut.cd()

                    # preaparing the TPads
                    fPad1 = TPad('fPad1_%s' % histoname, 'fPad1_%s' % histoname,  0.0, 0.0, 0.55, 1.0, 0)
                    fPad1.SetTopMargin(0.08)
                    fPad1.SetBottomMargin(0.025)
                    fPad1.SetRightMargin(0.05)
                    fPad1.SetLeftMargin(0.15)
        
                    fPad2 = TPad('fPad2_%s' % histoname, 'fPad2_%s' % histoname, 0.55, 0.0, 1.0, 1.00, 0)
                    fPad2.SetTopMargin(0.04)
                    fPad2.SetBottomMargin(0.40)
                    fPad2.SetRightMargin(0.05)
                    fPad2.SetLeftMargin(0.15)
                
                    fPad1.Draw()
                    fPad2.Draw()
                
                    fPad1.cd()

                    donut1 = TPie(histoname, histoname, len(values), values)
                    donut1.SetCircle(0.5,0.5,0.35)
                    for x, color in enumerate(colors):
                        # print i,color
                        donut1.SetEntryFillColor(x,colors[x])
                        donut1.SetEntryLineColor(x, 0)
                        if vals[x] < 0.9: donut1.SetEntryLabel(x,names[x]+" (<1%)")
                        else: donut1.SetEntryLabel(x,names[x]+" (%.1f"%(vals[x])+"%)")
                    donut1.SetTextSize(0.02)
                    donut1.SetTextColor(0)
                    donut1.SetRadius(.38)
                    donut1.Draw("T")
                
                    el3 = TEllipse(0.5,0.5,0.15,0.15)
                    el3.SetFillColor(0)
                    el3.SetLineColor(0)
                    el3.Draw()
                
                    fPad2.cd()
                    donutleg = donut1.MakeLegend()
                    donutleg.SetBorderSize(0)
                    donutleg.SetX1(0.01)
                    donutleg.SetX2(0.60)
                    print 'len(info)',len(info)
                    if len(info) == 3: donutleg.SetY1(0.50)
                    elif len(info) == 8: donutleg.SetY1(0.30)
                    elif len(info) == 10: donutleg.SetY1(0.18)
                    elif len(info) == 1: donutleg.SetY1(0.65)
                    else: donutleg.SetY1(0.40)
                    donutleg.SetY2(0.76)
                    donutleg.SetTextSize(0.065)
                    donutleg.SetTextFont(42)
                    
                    # labels
                    labelPos = [ 0.035, 0.88 ]
                    self.ATLASLabel(labelPos[0], labelPos[1], "Simulation Internal", 0.06)
                    if self.normalize == 'lumi': self.customLabel(labelPos[0], labelPos[1]-0.06, "#sqrt{s} = 13 TeV, 139 fb^{#minus1}", 0.06)
                    elif self.normalize == 'entries': self.customLabel(labelPos[0], labelPos[1]-0.06, "#sqrt{s} = 13 TeV", 0.06)
                    else:
                        self.customLabel(labelPos[0], labelPos[1]-0.06, "#sqrt{s} = 13 TeV", 0.06)
                        self.customLabelWithAngle(0.96, 0.95, "Not normalised", 270, 0.04, 2)
                    #self.customLabel(labelPos[0], labelPos[1]-0.12, str(SR), 0.06)
                    
                    # update and save canvas
                    #c_donut.Modified()
                    c_donut.Update()
                    self.Save("Donut_"+str(SR)+"_"+str(key), self.config.save_directory, c_donut, histolist[i])

                    if self.interactive:
                        try: input("Press enter to continue")
                        except SyntaxError: pass

                    c_donut.Close()

                i = i+1

    # =====================================================================
    #  DrawDonutsForPDGIds()
    # =====================================================================
    def DrawDonutsForPDGIds(self, histosInSR):
        for SR, histolist in histosInSR.iteritems():
            print 'SR',SR
            if SR == 'common': continue            
            i = 0
            for key, value in sorted(self.config.HistogramDetails_commonForSRs.iteritems()):
                # print str(i) + ". " + key

                if self.normalize == 'entries':
                    if histolist[i].GetSumOfWeights() > 0: histolist[i].Scale(1/histolist[i].GetSumOfWeights())
                        
                if 'pdgId' not in key:
                #if 'MC_W_decay1_from_Tau1_pdgId' not in key:
                    i = i+1
                    continue
                
                info = {}
                #print " - Key:",key
                #print " - Name:",histolist[i].GetName()
                #print " - Nbins:",histolist[i].GetXaxis().GetNbins()
                for ibin in range(1, histolist[i].GetXaxis().GetNbins()+1):
                    #print '   - bin:',ibin
                    #print '   - bin content:',histolist[i].GetBinContent(ibin)
                    #print '   - bin center:',histolist[i].GetXaxis().GetBinCenter(ibin)
                    #print '   - name:',self.getParticleName(histolist[i].GetXaxis().GetBinCenter(ibin))
                    if histolist[i].GetBinContent(ibin) > 0:
                        #print '   -*- bin:',ibin
                        #print '   -*- bin content:',histolist[i].GetBinContent(ibin)
                        #print '   -*- name:',self.getParticleName(histolist[i].GetXaxis().GetBinCenter(ibin))
                        #print '   -*- bin center:',histolist[i].GetXaxis().GetBinCenter(ibin)
                        info[self.getParticleName(histolist[i].GetXaxis().GetBinCenter(ibin))] = histolist[i].GetBinContent(ibin)

                       
                # prepare donut chart
                if len(info) > 0:
                    #print 'info',info

                    #for key0 in sorted(info, key=info.get, reverse=True):
                    #    print(key0, info[key0])
                    #print

                    names = []
                    vals = []
                    cols = []

                    total = 0.0

                    for key1 in sorted(info, key=info.get, reverse=True):
                        #print(key1, '->', info[key1])
                        total += float(info[key1])

                    #print ' -------------------'
                    #print ' - total',total
                    #print ' -------------------'

                    if total == 0.0:
                        i = i+1
                        continue
                    
                    for key2 in sorted(info, key=info.get, reverse=True):
                        #print " - name ->",key2
                        #print "->",float(info[key2])
                        #print "-> (%)",(100*float(info[key2])/total)
                        #print "->",self.getColor(key2)
                        names.append(key2)
                        vals.append(100*float(info[key2])/float(total))
                        cols.append(self.getColor(key2))

                    values = array('d', vals)
                    colors = array('i', cols)

                    #histoname = "%s" % histolist[i].GetName()
                    histoname = "%s_%s" % (SR, key)
                     
                    # define canvas
                    c_donut = TCanvas("donut_%s" % histoname, "donut_%s" % histoname, 800, 450)
                    c_donut.cd()

                    # preaparing the TPads
                    fPad1 = TPad('fPad1_%s' % histoname, 'fPad1_%s' % histoname,  0.0, 0.0, 0.55, 1.0, 0)
                    fPad1.SetTopMargin(0.08)
                    fPad1.SetBottomMargin(0.025)
                    fPad1.SetRightMargin(0.05)
                    fPad1.SetLeftMargin(0.15)
    
                    fPad2 = TPad('fPad2_%s' % histoname, 'fPad2_%s' % histoname, 0.55, 0.0, 1.0, 1.00, 0)
                    fPad2.SetTopMargin(0.04)
                    fPad2.SetBottomMargin(0.40)
                    fPad2.SetRightMargin(0.05)
                    fPad2.SetLeftMargin(0.15)

                    fPad1.Draw()
                    fPad2.Draw()

                    fPad1.cd()

                    # donut1 = TPie("donut", "PDG", len(values), values)
                    #donut1 = TPie("donut_"+"hola", "PDG_Id_"+"hola", len(values), values)
                    donut1 = TPie(histoname, histoname, len(values), values)
                    donut1.SetCircle(0.5,0.5,0.35)
                    for x, color in enumerate(colors):
                        # print i,color
                        donut1.SetEntryFillColor(x,colors[x])
                        donut1.SetEntryLineColor(x, 0)
                        if vals[x] < 0.9: donut1.SetEntryLabel(x,names[x]+" (<1%)")
                        else: donut1.SetEntryLabel(x,names[x]+" (%.1f"%(vals[x])+"%)")
                    donut1.SetTextSize(0.02)
                    donut1.SetTextColor(0)
                    donut1.SetRadius(.38)
                    donut1.Draw("T")

                    el3 = TEllipse(0.5,0.5,0.15,0.15)
                    el3.SetFillColor(0)
                    el3.SetLineColor(0)
                    el3.Draw()

                    fPad2.cd()
                    donutleg = donut1.MakeLegend()
                    donutleg.SetBorderSize(0)
                    donutleg.SetX1(0.01)
                    donutleg.SetX2(0.60)
                    print 'len(info)',len(info)
                    if len(info) == 3: donutleg.SetY1(0.40)
                    elif len(info) == 8: donutleg.SetY1(0.20)
                    elif len(info) == 1: donutleg.SetY1(0.55)
                    else: donutleg.SetY1(0.40)
                    donutleg.SetY2(0.66)
                    donutleg.SetTextSize(0.065)
                    donutleg.SetTextFont(42)
                    
                    # labels
                    labelPos = [ 0.035, 0.88 ]
                    self.ATLASLabel(labelPos[0], labelPos[1], "Simulation Internal", 0.06)
                    if self.normalize == 'lumi': self.customLabel(labelPos[0], labelPos[1]-0.06, "#sqrt{s} = 13 TeV, 139 fb^{#minus1}", 0.06)
                    elif self.normalize == 'entries': self.customLabel(labelPos[0], labelPos[1]-0.06, "#sqrt{s} = 13 TeV", 0.06)
                    else:
                        self.customLabel(labelPos[0], labelPos[1]-0.06, "#sqrt{s} = 13 TeV", 0.06)
                        self.customLabelWithAngle(0.96, 0.95, "Not normalised", 270, 0.04, 2)
                    self.customLabel(labelPos[0], labelPos[1]-0.12, str(SR), 0.06)
                    
                    # update and save canvas
                    #c_donut.Modified()
                    c_donut.Update()
                    self.Save("Donut_"+str(SR)+"_"+str(key), self.config.save_directory, c_donut, histolist[i])

                    if self.interactive:
                        try: input("Press enter to continue")
                        except SyntaxError: pass

                    c_donut.Close()
                    
                i = i+1
        
    # =====================================================================
    #  DrawBasic1DHistos()
    # =====================================================================
    def DrawBasic1DHistos(self, histosInSR):

        for SR, histolist in histosInSR.iteritems():
            if SR != 'common': continue
            #print histolist
            i = 0
            for key, value in sorted(self.config.HistogramDetails_common.iteritems()): #Draw common histos
                self.msg.printDebug("Drawing " + str(key))
                h = histolist[i]
                self.DrawOneBasic(h, 'common', value, key)
                i = i+1
                
        for SR, histolist in histosInSR.iteritems():
            if SR == 'common': continue
            i = 0
            for key, value in sorted(self.config.HistogramDetails_commonForSRs.iteritems()): #Draw histos for all channels
                self.msg.printDebug("Drawing " + str(key) + " for " +str(SR))
                h = histolist[i]
                self.DrawOneBasic(h, SR, value, key)
                i = i+1
                
            for key, value in sorted(self.config.HistogramDetails_specific[str(SR)].iteritems()): #Draw specific histos
                h = histolist[i]
                self.DrawOneBasic(h, SR, value, key)
                i = i+1

    # =====================================================================                                                                              
    #  DrawPie()
    # ===================================================================== 
    def DrawPie(self,name,SR,vals):
        channel = '0'
        region = str(SR)
        c_pie= TCanvas(str(name)+str(SR), str(name)+str(SR), 800, 450)
        fPad1 = TPad('fPad1_%s_%s' % (region, channel), 'fPad1_%s_%s' % (region, channel),  0.0, 0.0, 0.45, 1.0, 0)
        fPad1.SetTopMargin(0.08)
        fPad1.SetBottomMargin(0.025)
        fPad1.SetRightMargin(0.05)
        fPad1.SetLeftMargin(0.15)
    
        fPad2 = TPad('fPad2_%s_%s' % (region, channel), 'fPad2_%s_%s' % (region, channel), 0.45, 0.0, 1.0, 1.00, 0)
        fPad2.SetTopMargin(0.04)
        fPad2.SetBottomMargin(0.40)
        fPad2.SetRightMargin(0.05)
        fPad2.SetLeftMargin(0.15)

        fPad1.Draw()
        fPad2.Draw()

        fPad2.cd()
        nvals =len(vals)
        colors = range(1, nvals+1)
        h = TH1F(str(name)+str(SR),str(name)+str(SR),nvals,0,1)
        n = 1
        for val in vals:
            h.SetBinContent(n,val)
            n = n + 1
        pie = TPie(h)
        pie.SetTitle(str(SR)+"_"+str(name))
        pie.SetEntryFillColor(0,5)
        pie.SetEntryFillColor(1,2)
        pie.SetEntryLabel(0,'Top')
        pie.SetEntryLabel(1,'Higgs')
        pie.SetLabelFormat("#splitline{%val (%perc)}{%txt}");
        pie.SetCircle(0.5,0.5,0.35)
        pie.Draw("nol <")

        el3 = TEllipse(0.5,0.5,0.15,0.15)
        el3.SetFillColor(0)
        el3.SetLineColor(0)
        el3.Draw()

        fPad1.cd()
        donutleg = pie.MakeLegend()
        donutleg.SetX1(0.2) 
        donutleg.SetX2(0.9)
        donutleg.SetY1(0.20) 
        donutleg.SetY2(0.82)
        donutleg.SetTextSize(0.05)
        donutleg.SetTextFont(42)
        donutleg.SetFillColor(0)
        donutleg.SetBorderSize(0)
        labelPos = [ 0.19, 0.88 ]
        self.ATLASLabel(labelPos[0], labelPos[1], "Simulation Internal")
        if self.normalize == 'lumi': self.customLabel(labelPos[0], labelPos[1]-0.05, "#sqrt{s} = 13 TeV, 139 fb^{#minus1}")
        elif self.normalize == 'entries': self.customLabel(labelPos[0], labelPos[1]-0.05, "#sqrt{s} = 13 TeV")
        else: self.customLabel(labelPos[0], labelPos[1]-0.05, "#sqrt{s} = 13 TeV, Not normalized")
        self.customLabel(labelPos[0], labelPos[1]-0.10, str(SR))
        self.Save("Pie_"+str(SR)+"_"+str(name), self.config.save_directory, c_pie, h)

    # =====================================================================
    #  FillBasic1DCommonHistos()
    # =====================================================================
    def FillBasic1DCommonHistos(self, event, histosInSR):
        for SR, histolist in histosInSR.iteritems():
            if SR != 'common': continue
            #print histolist
            i = 0
            for key, value in sorted(self.config.HistogramDetails_common.iteritems()): #Fill common histos
                #print 'key ',key
                if key in ['MC_H_decay_weights',  'MC_H_decay']:
                    key = 'MC_H_decay'
                    continue
                aux = event.GetListOfLeaves().FindObject(str(key)).GetValue(0)
                #print 'histolist[i].GetName()',histolist[i].GetName()
                #print aux
                if histolist[i].GetName() == "MC_H_decay_weights": histolist[i].Fill(aux, event.weight_mc) 
                else: histolist[i].Fill(aux)

                #histolist[i].Sumw2()
                i = i+1
        
    # =====================================================================
    #  FillBasic1DHistos()
    # =====================================================================
    def FillBasic1DHistos(self, event, histosInSR):
        for SR, histolist in histosInSR.iteritems():
            
            if not self.Region(event, str(SR)) == True: continue
            i = 0
            for key, value in sorted(self.config.HistogramDetails_commonForSRs.iteritems()): #Fill histos for all channels
                #print key
                aux = event.GetListOfLeaves().FindObject(str(key)).GetValue(0)
                if aux == -999.0 or aux == -1000.0 : #In 3L1HadTau we have H->TauTau and H->WW at the same time, leading to these default vaulues in valid events.
                    i = i +1
                    continue
                if value[5] == "MeV":
                    aux = aux/1000 #Convert to GeV
                if key == "weight_mc": histolist[i].Fill(aux)
                else: histolist[i].Fill(aux, event.weight_mc)
                histolist[i].Sumw2()
                i = i+1
            for key, value in sorted(self.config.HistogramDetails_specific[str(SR)].iteritems()): #Fill the specific histos
                #print key
                aux = event.GetListOfLeaves().FindObject(str(key)).GetValue(0)
                if aux == -999.0 or aux == -1000.0 : #In 3L1HadTau we have H->TauTau and H->WW at the same time, leading to these default vaulues in valid events.
                    i = i +1
                    continue	
                if value[5] == "MeV":
                    aux = aux/1000 #Convert to GeV
                histolist[i].Fill(aux, event.weight_mc)
                histolist[i].Sumw2()
                i = i+1

    # =====================    
    # Charge and MT Histograms
    # =======================
    def DrawChargeAndMtHistos(self, chargehistos, MThistos):
        for key, value in chargehistos.iteritems():
            i = 0
            for particle in self.config.particles:
                self.DrawOneBasic(value[i], key, ["Charge ("+str(particle)+")", 3, -1.5, 1.5, str(particle)+"_charge", "" ], "MC_"+str(particle)+"_charge")
                if particle == "Wdecay1_from_t":
                    self.DrawOneBasic(value[i], key, ["Charge (top)", 3, -1.5, 1.5, "t_charge", "" ], "MC_t_charge")
                    self.DrawOneBasic(value[i], key, ["Charge (W from t)", 3, -1.5, 1.5, "W_from_t_charge", "" ], "MC_W_from_t_charge")
                i = i+1

        for key, value in MThistos.iteritems():
            i = 0
            for particle in self.config.particles:
                self.DrawOneBasic(value[i], key, ["M_{T} ("+str(particle)+")", 20, 0., 400., str(particle)+"_MT", "GeV" ], "MC_"+str(particle)+"_MT")
                i = i+1

        return
                
    def charge(self, pdgId):
        positive = [-1, 2, -3, 4, -5, 6, -7, 8, -11, -13, -15, 17, 24, 37]
        negative = [1, -2, 3, -4, 5, -6, 7, -8, 11, 13, 15, -17, -24, -37]
        neutre = [23, 21, 25, 35, 22, 32, 33, 12, 14, 16, 18, -12, -14, -16, -18]
        if pdgId in positive:
            chargeS = 1.
        elif pdgId in negative:
            chargeS =  -1.
        elif pdgId in neutre:
            chargeS =  0.
        elif pdgId < -100 or pdgId == 0: # particle not present                                                                                             
            chargeS = 100.
        self.msg.printDebug("pdgID = " + str(pdgId) + " --> charge = " + str(chargeS))
        return chargeS

    # =====================================================================
    #  FillChargeAndMtHistos()
    # =====================================================================
    def FillChargeAndMtHistos(self, event, chargehistos, MThistos):       
        for key, value in chargehistos.iteritems():
            if not self.Region(event, key): continue
                
            i = -1
            for particle in self.config.particles:
                i = i+1
                if "tau" in str(particle):
                    aux_charge = event.GetListOfLeaves().FindObject("MC_"+str(particle)+"_isHadronic").GetValue(0)
                else:
                    aux_charge = event.GetListOfLeaves().FindObject("MC_"+str(particle)+"_pdgId").GetValue(0)
                self.msg.printDebug("particle = "+str(particle)+ "  --> pdgID = " + str(aux_charge)) 
                aux_charge = self.charge(aux_charge)
                if aux_charge == 100. : continue #for non present particles
                #print(i)
                #print(value[i])
                self.msg.printDebug("particle = "+str(particle)  + " --> charge = " + str(aux_charge))
                value[i].Fill(aux_charge, event.weight_mc)

        for key, value in MThistos.iteritems():
            if not self.Region(event, key): continue
            i = -1
            for particle in self.config.particles:
                i = i+1
                if "tau" in str(particle):
                    aux_MT = event.GetListOfLeaves().FindObject("MC_"+str(particle)+"_isHadronic").GetValue(0)
                else:
                    aux_MT = event.GetListOfLeaves().FindObject("MC_"+str(particle)+"_pdgId").GetValue(0)
                if aux_MT < -100 or aux_MT ==0: continue
                aux_MT = self.TLorentz("MC_"+str(particle), event)
                aux_MT = aux_MT.Mt()
                self.msg.printDebug("particle = "+str(particle)  + " -->  Transverse mass = " + str(aux_MT) )
                value[i].Fill(aux_MT/1000, event.weight_mc)
        return        

    # =====================================================================
    #  DefChargeAndMtHistos()
    # =====================================================================
    def DefChargeAndMtHistos(self, SRs):
        chargehistos = {}
        MThistos = {}
        for SR in SRs:
            chargehistos[SR] = []
            MThistos[SR] = []
            for particle in self.config.particles:
                chargehistos[SR].append(TH1F(str(SR)+"_"+str(particle)+"_charge",str(SR)+"_"+str(particle)+"_charge" , 3, -1.5, 1.5))
                MThistos[SR].append(TH1F(str(SR)+"_"+str(particle)+"_MT",str(SR)+"_"+str(particle)+"_MT" , 20, 0., 400.))
        return chargehistos, MThistos


    # =====================================================================
    #  DefBasic1DHistos()
    # =====================================================================
    def DefBasic1DHistos(self, histosInSR, SRs):
        histosInSR['common'] = []
        i = 0
        self.defbasic_common(i, self.config.HistogramDetails_common, histosInSR['common'])
        self.msg.printInfo("Common histos defined!")
        for SR in SRs:
            histosInSR[SR] = []
            # print("Defining histos for " + str(SR))
            i = 0
            i = self.defbasic(i, self.config.HistogramDetails_commonForSRs, SR, histosInSR[SR])
            i = self.defbasic(i, self.config.HistogramDetails_specific[SR], SR, histosInSR[SR])
            self.msg.printInfo("Histos for " + str(SR) + " defined!")

    # =====================================================================
    #  defbasic()
    # =====================================================================
    def defbasic_common(self, i, histo_details, SRhistolist):
        for key in range(len(histo_details)): SRhistolist.append("0")
        for key, value in sorted(histo_details.iteritems()):
            #print key
            self.msg.printDebug("  ---> Defining histogram for " + str(key))
            min = value[2]
            max = value[3]
            SRhistolist[i] = TH1F(str(key), str(key), value[1], min,max)
            #print SRhistolist[i]
            #print(i)
            i = i+1
        return i
    
    # =====================================================================
    #  defbasic()
    # =====================================================================
    def defbasic(self, i, histo_details, SR, SRhistolist):
        for key in range(len(histo_details)): SRhistolist.append("0")
        for key, value in sorted(histo_details.iteritems()):
            self.msg.printDebug("  ---> Defining histogram for " + str(key) + " in " + str(SR))
            min = value[2]
            max = value[3]
            if value[5] == "MeV": #Convert to GeV if it is MeV
                min = min/1000
                max = max/1000
            SRhistolist[i] = TH1F(str(key)+'_'+str(SR), str(key)+'_'+str(SR), value[1], min,max)
            #print SRhistolist[i]
            #print(i)
            i = i+1
        return i

    # =====================================================================
    #  SpeedBranches()
    # =====================================================================
    def SpeedBranches(self, Tree):
        self.msg.printGreen("Enabling just the necessary branches...")
        Tree.SetBranchStatus('*',0)
        Tree.SetBranchStatus("runNumber",1)
        for key in self.config.HistogramDetails_commonForSRs.keys():
            Tree.SetBranchStatus(key,1) #activating branches
        for SR in self.config.HistogramDetails_specific.keys():
            for key in self.config.HistogramDetails_specific[SR]:
                Tree.SetBranchStatus(key,1) #activating branches
        self.msg.printInfo("- Branches read successfully!")
   
    # =====================================================================
    #  Save()
    # =====================================================================
    def Save(self, name, directory, myCanvas, hist):
        if not path.exists(directory): makedirs(directory)
        for out in self.outputformat:
            if not path.exists(directory+"/"+out+"/"): makedirs(directory+"/"+out+"/")
            if out == 'root':
                out_file = TFile(str(directory)+"/"+out+"/"+str(name)+"."+out, 'recreate')
                hist.Write()
                out_file.Close()
            else:
                myCanvas.SaveAs(str(directory)+"/"+out+"/"+str(name)+"."+out)           

    # =====================================================================
    #  P_z()   Having TLorentz function, this one can be deprecated
    # =====================================================================
    def P_z(self, particle,event):
        Vec_particle_PtEtaPhiM = self.TLorentz(particle, event)
        Vec_particle_Pz = Vec_particle_PtEtaPhiM.Pz()
        return Vec_particle_Pz
        
    # =====================================================================
    #  ChildsToParent()
    # =====================================================================
    def ChildsToParent(self, event, nChilds, particle1, particle2, particle3):
        # particle1 = MC_H_decay1
        # particle2 = MC_H_decay2
        Vec_child1_PtEtaPhiM = self.TLorentz(particle1, event)
        Vec_child2_PtEtaPhiM = self.TLorentz(particle2, event)
        if nChilds == 2:
            Vec_Parent_PtEtaPhiM = Vec_child1_PtEtaPhiM + Vec_child2_PtEtaPhiM
        if nChilds ==3:
            Vec_child3_PtEtaPhiM = self.TLorentz(particle3, event)
            Vec_Parent_PtEtaPhiM = Vec_child1_PtEtaPhiM + Vec_child2_PtEtaPhiM + Vec_child3_PtEtaPhiM
        #Higgs_m = Vec_Higgs_PtEtaPhiM.M()
        self.msg.printDebug("For the parent particle we obtain:")
        self.msg.printDebug("  - m  : " +str(Vec_Parent_PtEtaPhiM.M()/1000) + " GeV")
        self.msg.printDebug("  - pt : " +str(Vec_Parent_PtEtaPhiM.Pt()/1000)+ " GeV")
        self.msg.printDebug("  - pz : " +str(Vec_Parent_PtEtaPhiM.Pz()/1000)+ " GeV")
        self.msg.printDebug("  - eta: " +str(Vec_Parent_PtEtaPhiM.Eta()))
        self.msg.printDebug("  - phi: " +str(Vec_Parent_PtEtaPhiM.Phi())+ " rad")
        return Vec_Parent_PtEtaPhiM
        

    # =====================================================================      
    # TLorentz = get the TLorentz vector of a particle)
    # =====================================================================                                                                                                      
    def TLorentz(self, particle, event):
        aux_pt = getattr(event, particle+"_pt")    # init at -1000.0
        aux_eta = getattr(event, particle+"_eta")  # init at - 999.0
        aux_phi = getattr(event, particle+"_phi")  # init at -1000.0
        aux_m = getattr(event, particle+"_m")      # init at -1000.0

        if aux_pt != -1000.0 and aux_eta != -999.0 and aux_phi != -1000.0 and aux_m != -1000.0:
            self.msg.printDebug(event)
            self.msg.printDebug("pt = " + str(aux_pt))
            self.msg.printDebug("eta = " + str(aux_eta))
            self.msg.printDebug("phi = " + str(aux_phi))
            self.msg.printDebug("m = " + str(aux_m))

            Vec_particle_PtEtaPhiM = Math.LorentzVector('ROOT::Math::PtEtaPhiMVector')(aux_pt, aux_eta, aux_phi, aux_m)
            
            return Vec_particle_PtEtaPhiM
        
        else:
            self.msg.printWarning("Event not valid")
            return -1000.0
        

    # =====================================================================
    #  Region() :: Defines the signal region
    # =====================================================================
    def Region(self, entry,  region):        
        cuts = self.config.cuts
        #print(cuts.keys())
        #exit()

        #if abs(entry.MC_W_decay2_from_W1_pdgId) == 16:
        #    self.msg.printWarning("Tenemos un nutrino tau en entry.MC_W_decay2_from_W1_pdgId")

        Store = False
        Channel = 'Unknown'
        self.msg.printDebug("Filtering for region " + str(region))
        #Region definitions
        aux = abs(entry.MC_Higgs_decay1_pdgId) + abs(entry.MC_Higgs_decay2_pdgId)
        if aux == 48: Channel = "HWW"			# H- > W W
        if aux == 30: Channel = "Htautau"       # H- > Tau Tau     
        if aux == 46: Channel = "HZZ"			# H- > Z Z									
        if aux == 44: Channel = "Hgammagamma"	# H- > gamma gamma
        if aux == 10: Channel = "Hbb"			# H- > b b
        if aux == 42: Channel = "Hgg"			# H- > g g
        if aux == 8:  Channel = "Hcc"			# H- > c c
        if aux == 45: Channel = "HZgamma"		# H- > Z gamma
        if aux == 6:  Channel = "Hss"           # H- > s s                                        
        if aux == 26: Channel = "Hmumu"         # H- > mu mu                                                
        
        if region == "3L1HadTau":
            Store = True
                
	elif region == "3L":
        # The different cHWW and HZZ still have to be included
	    # self.msg.printWarning("The conditions for 3L signal region have not been added")
            Store = True
				
		
        else: 
            self.msg.printError("Signal region " + str(region) + " not defined")
            Store = False
        

        
        if Store: self.msg.printDebug("- Event passing cuts for region %s" % region)
        self.channel = Channel
        return Store

    # =====================================================================
    #  StyleATLAS()
    # =====================================================================
    def StyleATLAS(self, icol, showStats):
       
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

    # =====================================================================
    #  ATLASLabel()
    # =====================================================================
    def ATLASLabel(self, x, y, text, size=0.04, color=1):
        # self.customLabel(x, y, "#bf{#it{ATLAS}} %s" % text, size, color)
        self.customLabel(x, y, "#bf{#it{aMC@NLO}} %s" % text, size, color)

    # =====================================================================
    #  customLabelWithAngle()
    # =====================================================================
    def customLabelWithAngle(self, x, y, text, angle, size=0.04, color=1):
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
    def customLabel(self, x, y, text, size=0.04, color=1):
        l = TLatex()
        l.SetTextFont(42)
        l.SetTextSize(size)
        l.SetTextColor(color)
        l.SetNDC()
        l.DrawLatex(x,y,str(text))

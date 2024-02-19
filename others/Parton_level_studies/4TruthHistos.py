#!/usr/bin/env python

###########################################################
#   Script to produce parton-level truth distributions    #
###########################################################

# -*- coding: utf-8 -*-
import os, sys
from ROOT import gROOT, TFile, TTree, TBranch, TLorentzVector, Math, TCanvas, TCut, TH1F, TH2F, gROOT, TChain, TMath
import time
#from array import array
#from matplotlib import pyplot as plt
import numpy as np
import math
from optparse import OptionParser

from ToolsForTruth import tools
from MsgHelper import msgServer
from ConfigFile import configFile

# =================================================================================
#  main
# =================================================================================
def main(argv):
    parser = OptionParser()
    parser.add_option("-d", "--debugLevel", dest="debugLevel", default=1, type="int",
                      help="set debug level (DEBUG=0, INFO=1, WARNING=2, ERROR=3, FATAL=4) [default: %default]", metavar="LEVEL")  
    parser.add_option("-i", "--input", dest="myinput", default="",
                      help="set input file or directory or dataset [default: %default]", metavar="FILE or DIR or DATASET")
    parser.add_option("-c", "--configuration", dest="myconfig", default="./config.yaml",
                      help="set input yaml configuration file [default: %default]", metavar="FILE")
    parser.add_option("-f", "--maxfiles", dest="maxfiles", default=-1,
                      help="set number of maximum files to be processed", metavar="MAXFILES", type="int")
    parser.add_option("-e", "--maxevents", dest="maxevents", default=-1,
                      help="set number of maximum events to be processed", metavar="MAXEVENTS", type="int")
    parser.add_option("-s","--stats", action="store_true", dest="showStats",
                          help="show stats box")
    parser.add_option("--interactive", action="store_true", dest="interactive",
                          help="run 4TruthHistos interactively")
    parser.add_option("--normlumi", action="store_true", dest="normlumi",
                          help="normalize histograms to the Run 2 luminosity (i.e. 139 fb-1)")
    parser.add_option("--nonorm", action="store_true", dest="nonorm",
                          help="No normalize histograms at all")
    parser.add_option("--outputformat", dest="outputformat", default="all",
                        help="set output format of plots [default: %default] [options: png, pdf, root, all]", metavar="FORMAT")

    # Convertir channel en lo de e/mu
    #parser.add_option("-c", "--channel", dest="channel", default="",
    #                  help="Select the channel", metavar="CHANNEL")

    try:
        (options, args) = parser.parse_args()
    except:
        parser.print_help()
        exit()

    global msg
    msg = msgServer('4TruthHistos', options.debugLevel)
    msg.printBold('Running 4TruthHistos.py')

    global config
    config = configFile(options)

    global tool
    tool = tools(options, config)

    gROOT.Reset()
    if options.interactive: gROOT.SetBatch(0)
    else: gROOT.SetBatch(1)
    
    start_time = time.time()

    # Selecting the root file(s)
    # Merge chains from all input ROOT files 
    Truth = TChain(config.TreeName)
    for ifile in config.rootFile: Truth.Add(ifile)
    msg.printInfo('- Total entries = %d' % Truth.GetEntries())
    
    #print tree (for debug purposes only)
    #Truth.Print()
    #exit()
   
    style_name = tool.StyleATLAS(0, options.showStats)
    gROOT.SetStyle("Plain")
    gROOT.SetStyle("style_name")


    #########   JUST FOR TEST ::::    DETELE FROM HERE ####
    """ debugSample = True
    if debugSample == True:
        H_Channels = TH1F('Hdecay', 'Hdecay', 60, -30., 30.)
        W_Channels = TH1F('Wchild1', 'Wchild1', 60, -30., 30.)
        tau_Channels = TH1F('Tau_child1', 'Tau_child1', 60, -30., 30.)
        Z_Channels = TH1F('Zchild1', 'Zchild1', 60, -30., 30.)
        top_lp_decay = TH1F('Top_decay', 'Top_decay' , 60, -30., 30.)
        top_nu_decay = TH1F('Top_nu_decay', 'Top_nu_decay' , 60, -30., 30.)
        ww = 0
        tt = 0
        zz = 0
        gammagamma = 0
        bb = 0
        gg = 0
        cc = 0
        Zgamma = 0
        ss = 0
        mumu = 0
        
        ww_e = 0
        ww_mu = 0
        ww_tau_e = 0
        ww_tau_mu = 0
        ww_tauhad = 0
        ww_had = 0
        ww_9999 = 0
        ww_1845523456 = 0
        ww_1627419749 = 0
        ww_else = 0
        tt_e = 0
        tt_mu = 0
        tt_had = 0
        tt_else = 0
        tt_9999 = 0
        zz_ee = 0
        zz_mumu = 0
        zz_tautau = 0
        zz_et = 0
        zz_mt = 0
        zz_em = 0
        zz_nunu = 0
        zz_hadhad = 0
        zz_9999 = 0
        zz_else = 0
        top_e = 0
        top_mu = 0
        top_TauHad = 0
        top_had = 0
        top_else = 0
        _3L1HadTau_tt = 0
        _3L1HadTau_ww = 0
        _3L1HadTau_zz = 0
        _3L_tt = 0
        _3L_ww = 0
        _3L_zz = 0
 
        n_events = 0
        for event in Truth:
            n_events = n_events + 1
            aux = abs(event.MC_Higgs_decay1_pdgId) + abs(event.MC_Higgs_decay1_pdgId)
            if aux == 48:  # WW channel
                ww = ww + event.weight_mc
            if aux == 30:  # tautau channel
                tt = tt + event.weight_mc         
            if aux == 46:  # ZZ channel                                                                 
                zz = zz + event.weight_mc
            if aux == 44:  # gammagamma
                gammagamma = gammagamma + event.weight_mc
            if aux == 10:  # bb
                bb = bb + event.weight_mc
            if aux == 42:  # gg
                gg = gg + event.weight_mc
            if aux == 8:  # gcc
                cc = cc + event.weight_mc
            if aux == 45:  # Zgamma
                Zgamma = Zgamma + event.weight_mc
            if aux == 6:  # ss channel                                                                 
                ss = ss + event.weight_mc
            if aux == 26:  # mumu channel                                                                 
                mumu = mumu + event.weight_mc   
                

            if tool.Region(event, '3L1HadTau'):
                if tool.channel == 'Htautau':
                    _3L1HadTau_tt = _3L1HadTau_tt + event.weight_mc
                if tool.channel == 'HWW':
                    _3L1HadTau_ww = _3L1HadTau_ww + event.weight_mc
                if str(tool.channel) in  ['HZZ', 'HZZ1', 'HZZ2']:
                    _3L1HadTau_zz = _3L1HadTau_zz  + event.weight_mc

            if aux == 30: # study of tau decay
                if abs(event.MC_Higgs_tau_decay1_isHadronic) == 11:
                    tt_e = tt_e + event.weight_mc
                if abs(event.MC_Higgs_tau_decay2_isHadronic) == 11:
                    tt_e = tt_e+ event.weight_mc
                if abs(event.MC_Higgs_tau_decay1_isHadronic) == 13:
                    tt_mu = tt_mu + event.weight_mc
                if abs(event.MC_Higgs_tau_decay2_isHadronic) == 13:
                    tt_mu = tt_mu + event.weight_mc
                if abs(event.MC_Higgs_tau_decay1_isHadronic) == 24:
                    tt_had = tt_had + event.weight_mc
                if abs(event.MC_Higgs_tau_decay2_isHadronic) == 24:
                    tt_had = tt_had + event.weight_mc

            if aux == 48:
                if abs(event.MC_Higgs_decay1_from_decay1_pdgId) == 11:
                    ww_e = ww_e + event.weight_mc
                if abs(event.MC_Higgs_decay1_from_decay2_pdgId) == 11:
                    ww_e = ww_e + event.weight_mc
                if abs(event.MC_Higgs_decay1_from_decay1_pdgId) == 13:
                    ww_mu = ww_mu + event.weight_mc
                if abs(event.MC_Higgs_decay1_from_decay2_pdgId) == 13:
                    ww_mu = ww_mu + event.weight_mc
                if abs(event.MC_Higgs_decay1_from_decay1_pdgId) == 15:
                    if abs(event.MC_Higgs_tau_decay1_from_decay1_isHadronic) == 11:
                        ww_tau_e = ww_tau_e + event.weight_mc
                    if abs(event.MC_Higgs_tau_decay1_from_decay1_isHadronic) == 13:
                        ww_tau_mu = ww_tau_mu + event.weight_mc
                    if abs(event.MC_Higgs_tau_decay1_from_decay1_isHadronic) == 24:
                        ww_tauhad = ww_tauhad + event.weight_mc
                if abs(event.MC_Higgs_decay1_from_decay2_pdgId) == 15:
                    if abs(event.MC_Higgs_tau_decay1_from_decay2_isHadronic) == 11:
                        ww_tau_e = ww_tau_e + event.weight_mc
                    if abs(event.MC_Higgs_tau_decay1_from_decay2_isHadronic) ==13:
                        ww_tau_mu = ww_tau_mu + event.weight_mc
                    if abs(event.MC_Higgs_tau_decay1_from_decay2_isHadronic) ==24:
                        ww_tauhad = ww_tauhad +event.weight_mc
                if abs(event.MC_Higgs_decay1_from_decay1_pdgId) not in [11, 13, 15]:
                    ww_had = ww_had + event.weight_mc
                if abs(event.MC_Higgs_decay1_from_decay2_pdgId)not in [11, 13, 15]:
                    ww_had = ww_had + event.weight_mc

        msg.printInfo("Higgs decay channels")
        tot1 = ww + tt + zz
        tot = ww + tt + zz + gammagamma + bb + gg + cc + Zgamma + ss + mumu
        msg.printInfo(" H -> WW            ::  " + str(ww) + "  ("+ str(100.0*ww/tot) +"%)")
        msg.printInfo(" H -> tau tau       ::  " + str(tt) + "  ("+ str(100.0*tt/tot) +"%)")
        msg.printInfo(" H -> ZZ            ::  " + str(zz) + "  ("+ str(100.0*zz/tot) +"%)")
        msg.printInfo(" H -> Gamma Gamma   ::  " + str(gammagamma) + "  ("+ str(100.0*gammagamma/tot) +"%)")
        msg.printInfo(" H -> bb            ::  " + str(bb) + "  ("+ str(100.0*bb/tot) +"%)")
        msg.printInfo(" H -> gg            ::  " + str(gg) + "  ("+ str(100.0*gg/tot) +"%)")
        msg.printInfo(" H -> cc            ::  " + str(cc) + "  ("+ str(100.0*cc/tot) +"%)")
        msg.printInfo(" H -> Z Gamma       ::  " + str(Zgamma) + "  ("+ str(100.0*Zgamma/tot) +"%)")
        msg.printInfo(" H -> ss            ::  " + str(ss) + "  ("+ str(100.0*ss/tot) +"%)")
        msg.printInfo(" H -> mu mu         ::  " + str(mumu) + "  ("+ str(100.0*mumu/tot) +"%)")


        msg.printInfo("Tau decay channels in H-> TauTau")
        tt_total =  tt_e + tt_mu + tt_had
        msg.printInfo(" Tau -> e        :: " + str(tt_e)  + "  ("+ str(100.0*tt_e/tt_total) +"%)")
        msg.printInfo(" Tau -> mu       :: " + str(tt_mu) + "  ("+ str(100.0*tt_mu/tt_total) +"%)")
        #msg.printInfo(" Tau -> tau_e    :: " + str(tt_tau_e)   + "  ("+ str(100.0*tt_tau_e/tt_total) +"%)")
        #msg.printInfo(" Tau -> tau_mu   :: " + str(tt_tau_mu)  + "  ("+ str(100.0*tt_tau_mu/tt_total) +"%)")
        #msg.printInfo(" Tau -> tau_had  :: " + str(tt_tau_had) + "  ("+ str(100.0*tt_tau_had/tt_total) +"%)")
        msg.printInfo(" Tau -> had      :: " + str(tt_had)+ "  ("+ str(100.0*tt_had/tt_total) +"%)")

        msg.printInfo("W decay channels in H->WW")
        ww_total = ww_e + ww_mu + ww_tau_e + ww_tau_mu + ww_had + ww_tauhad
        msg.printInfo(" W -> e         :: " + str(ww_e)  + "  ("+ str(100.0*ww_e/ww_total) +"%)")
        msg.printInfo(" W -> mu        :: " + str(ww_mu) + "  ("+ str(100.0*ww_mu/ww_total) +"%)")
        msg.printInfo(" W -> tau -> e  :: " + str(ww_tau_e)  + "  ("+ str(100.0*ww_tau_e/ww_total) +"%)")
        msg.printInfo(" W -> tau -> mu :: " + str(ww_tau_mu)  + "  ("+ str(100.0*ww_tau_mu/ww_total) +"%)")
        msg.printInfo(" W -> tau - had :: " + str(ww_tauhad)  + "  ("+ str(100.0*ww_tauhad/ww_total) +"%)")
        msg.printInfo(" W -> hads      :: " + str(ww_had)  + "  ("+ str(100.0*ww_had/ww_total) +"%)")

        msg.printInfo("")
        msg.printInfo("Region 2Lep + 1HadTau")
        tot_3L1HadTau = _3L1HadTau_tt + _3L1HadTau_ww + _3L1HadTau_zz
        msg.printInfo(" 2L+1HadTau: H -> tau tau  :: " + str(_3L1HadTau_tt) + "  ("+ str(100.0*_3L1HadTau_tt/tot_3L1HadTau) +"%)")
        msg.printInfo(" 2L+1HadTau: H -> WW       :: " + str(_3L1HadTau_ww) + "  ("+ str(100.0*_3L1HadTau_ww/tot_3L1HadTau) +"%)")
        msg.printInfo(" 2L+1HadTau: H -> ZZ       :: " + str(_3L1HadTau_zz) + "  ("+ str(100.0*_3L1HadTau_zz/tot_3L1HadTau) +"%)")

        msg.printInfo("Signal events in channel VS Total events in same channel")
        msg.printInfo( "H->TauTau(2L+1HadTau) / H->TauTau(Total) = " + str(_3L1HadTau_tt/tt))
        msg.printInfo( "H-> W W (2L+1HadTau)  / H-> W W (Total)  = " + str(_3L1HadTau_ww/ww))
        msg.printInfo(" H-> Z Z (2L+1HadTau)  / H-> Z Z (Total)  = " + str(_3L1HadTau_zz/zz))


        exit() """
	#########   JUST FOR TEST ::::    DETELE UNTIL HERE ####



    # Activate only the necessary branches
    tool.SpeedBranches(Truth)
	    
    # signal regions
    SRs = ['3L1HadTau', '3L']
    histosInSR = {}
    


    # Step 1 - Declaration
    msg.printGreen("Step 1 - Defining the histograms")
    msg.printInfo("- Defining basic histos...")    
    tool.DefBasic1DHistos(histosInSR, SRs)

    # additional 1D histos
    msg.printInfo("- Defining additional 1D histos...")
    ChargeHistos, MtHistos = tool.DefChargeAndMtHistos(SRs)
    h1_nu_from_t_pz = TH1F('pz_nu', 'W_decay2_from_t_pz', 50, -1000., 1000.)  
    h1_lp_from_t_pz = TH1F('pz_lp', 'W_decay1_from_t_pz', 50, -800., 800.)
    h1_pz_ratio = TH1F('alpha', 'nu_pz / l_pz', 20, 0., 1.)
    h1_Higgs_m = TH1F("Higgs_m", "Higgs_m", 20, 124., 126.)
    h1_Higgs_pt = TH1F("Higgs_pt", "Higgs_pt", 50, 0., 500.)
    h1_Higgs_eta = TH1F("Higgs_eta", "Higgs_eta", 20, -4.5, 4.5)
    h1_Higgs_phi = TH1F("Higgs_phi", "Higgs_phi", 20, -TMath.Pi(), TMath.Pi())
    h1_Higgs_pz = TH1F("Higgs_pz", "Higgs_pz", 50, 0., 500.)
    h1_top_m = TH1F("top_m", "top_m", 20, 100., 200.)
    h1_top_pt = TH1F("top_pt", "top_pt", 35, 0., 350.)
    h1_top_pz = TH1F("top_pz", "top_pz", 35, 0., 350.)
    h1_top_eta = TH1F("top_eta", "top_eta", 20, -4.5, 4.5)
    h1_top_phi = TH1F("top_phi", "top_phi", 20, -TMath.Pi(), TMath.Pi())
    h1_HT = TH1F("H_{T}", "H_{T}", 20, 100., 750.)
    h1_DeltaEta_bl_from_t_3L1HadTau = TH1F("DeltaEta_bl_from_t_3L1HadTau", "DeltaEta_bl_from_t_3L1HadTau", 20, -4.5, 4.5)
    h1_DeltaPhi_bl_from_t_3L1HadTau = TH1F("DeltaPhi_bl_from_t_3L1HadTau", "DeltaPhi_bl_from_t_3L1HadTau", 20, -TMath.Pi(), TMath.Pi())
    h1_DeltaR_bl_from_t_3L1HadTau = TH1F("DeltaR_bl_from_t_3L1HadTau", "DeltaR_bl_from_t_3L1HadTau", 20, 0., 6.)
    h1_DeltaEta_bl_from_t_3L = TH1F("DeltaEta_bl_from_t_3L", "DeltaEta_bl_from_t_3L", 20, -4.5, 4.5)
    h1_DeltaPhi_bl_from_t_3L = TH1F("DeltaPhi_bl_from_t_3L", "DeltaPhi_bl_from_t_3L", 20, -TMath.Pi(), TMath.Pi())
    h1_DeltaR_bl_from_t_3L = TH1F("DeltaR_bl_from_t_3L", "DeltaR_bl_from_t_3L", 20, 0., 6.)

    h1_DeltaEta_Hdecay1and2_3L1HadTau = TH1F("DeltaEta_Hdecay1and2_3L1HadTau", "DeltaEta_Hdecay1and2_3L1HadTau", 20, -4.5, 4.5)
    h1_DeltaEta_Hdecay1and2_3L = TH1F("DeltaEta_Hdecay1and2_3L", "DeltaEta_Hdecay1and2_3L", 20, -4.5, 4.5)
    h1_DeltaPhi_Hdecay1and2_3L1HadTau = TH1F("DeltaPhi_Hdecay1and2_3L1HadTau", "DeltaPhi_Hdecay1and2_3L1HadTau", 20, -TMath.Pi(), TMath.Pi())
    h1_DeltaPhi_Hdecay1and2_3L = TH1F("DeltaPhi_Hdecay1and2_3L", "DeltaPhi_Hdecay1and2_3L", 20, -TMath.Pi(), TMath.Pi())
    h1_DeltaR_Hdecay1and2_3L1HadTau = TH1F("DeltaR_Hdecay1and2_3L1HadTau", "DeltaR_Hdecay1and2_3L1HadTau", 20, 0., 6.)
    h1_DeltaR_Hdecay1and2_3L = TH1F("DeltaR_Hdecay1and2_3L", "DeltaR_Hdecay1and2_3L", 20, 0., 6.)

    h1_DeltaEta_W1_from_Hdecay1and2_3L1HadTau = TH1F("DeltaEta_W1_from_Hdecay1and2_3L1HadTau", "DeltaEta_W1_from_Hdecay1and2_3L1HadTau", 20, -4.5, 4.5)
    h1_DeltaEta_W1_from_Hdecay1and2_3L = TH1F("DeltaEta_W1_from_Hdecay1and2_3L", "DeltaEta_W1_from_Hdecay1and2_3L", 20, -4.5, 4.5)
    h1_DeltaR_W1_from_Hdecay1and2_3L1HadTau = TH1F("DeltaR_W1_from_Hdecay1and2_3L1HadTau", "DeltaR_W1_from_Hdecay1and2_3L1HadTau", 20, 0., 6.)
    h1_DeltaR_W1_from_Hdecay1and2_3L = TH1F("DeltaR_W1_from_Hdecay1and2_3L", "DeltaR_W1_from_Hdecay1and2_3L", 20, 0., 6.)
    h1_DeltaPhi_W1_from_Hdecay1and2_3L1HadTau = TH1F("DeltaPhi_W1_from_Hdecay1and2_3L1HadTau", "DeltaPhi_W1_from_Hdecay1and2_3L1HadTau", 20, -TMath.Pi(), TMath.Pi())
    h1_DeltaPhi_W1_from_Hdecay1and2_3L = TH1F("DeltaPhi_W1_from_Hdecay1and2_3L", "DeltaPhi_W1_from_Hdecay1and2_3L", 20, -TMath.Pi(), TMath.Pi())

    h1_MET_3L1HadTau = TH1F("MET_3L1HadTau", "MET_3L1HadTau", 40, 0, 500.)
    h1_MET_3L = TH1F("MET_3L", "MET_3L", 40, 0, 500.)

    h1_t_MT_3L1HadTau = TH1F("MT_t_3LHadTau", "MT_t_3LHadTau", 20, 0., 400.)
    h1_t_MT_3L = TH1F("MT_t_3L", "MT_t_3L", 20, 0., 400.)
    h1_W_from_t_MT_3L1HadTau = TH1F("MT_Wfromt_3LHadTau", "MT_Wfromt_3LHadTau", 20, 0., 400.)
    h1_W_from_t_MT_3L = TH1F("MT_Wfromt_3L", "MT_Wfromt_3L", 20, 0., 400.)

    h1_mlb_3L1HadTau = TH1F("mlb_3L1HadTau", "mlb_3L1HadTau", 25, 0., 250.)
    h1_mlb_3L = TH1F("mlb_3L", "mlb_3L", 25, 0., 250.)

    h1_mlb_l_fromHdec1_3L1HadTau = TH1F("mlb_1_3L1HadTau", "mlb_1_3L1HadTau", 20, 0., 400.)
    h1_mlb_l_fromHdec2_3L1HadTau = TH1F("mlb_2_3L1HadTau", "mlb_2_3L1HadTau", 20, 0., 400.)
    h1_mlb_l_fromHdec1_3L = TH1F("mlb_1_3L", "mlb_1_3L", 20, 0., 400.)
    h1_mlb_l_fromHdec2_3L = TH1F("mlb_2_3L", "mlb_2_3L", 20, 0., 400.)    

    #Simple histograms
    h1_Wdecay1_AllEvent_m = TH1F("Mass_decay1_AllEvent","Mass_decay1_AllEvent",  40, -3.5, 3.5)
    h1_Wdecay1_AllEvent_phi = TH1F('Phi_decay1_AllEvent','Phi_decay1_AllEvent',15, TMath.Pi(), TMath.Pi())
    h1_Wdecay1_AllEvent_eta =TH1F('Eta_decay1_AllEvent','Eta_decay1_AllEvent', 15,-4.5,4.5)
    h1_Wdecay1_AllEvent_pt =TH1F('Pt_decay1_AllEvent','Pt_decay1_AllEvent', 75,0.,400.)

    h1_Wdecay2_AllEvent_m = TH1F("Mass_decay2_AllEvent","Mass_deca2_AllEvent",  40, -3.5, 3.5)
    h1_Wdecay2_AllEvent_phi = TH1F('Phi_decay2_AllEvent','Phi_decay2_AllEvent',15, TMath.Pi(), TMath.Pi())
    h1_Wdecay2_AllEvent_eta =TH1F('Eta_decay2_AllEvent','Eta_decay2_AllEvent', 15,-4.5,4.5)
    h1_Wdecay2_AllEvent_pt =TH1F('Pt_decay2_AllEvent','Pt_decay2_AllEvent', 75,0.,400.)

    # 2D histos
    msg.printInfo("- Defining 2D histos...")
    h2_Wdecay_from_tau1_pdgidVSeta = TH2F("eta", "", 80, -5., 5., 80, -30., 30.)
    h2_Wdecay_from_tau1_pdgidVSpt = TH2F("pt", "W_decay1_from_Tau1", 80, 0., 80., 80, -30., 30.)
    h2_3L1HadTau_secondb_beforeFSR_pt_vs_eta = TH2F("b_from_gluon_pt_eta_3L1HadTau", "b_from_gluon_pt_eta_3L1HadTau", 20, 0., 300., 15, -4.5, 4.5)
    h2_3L1HadTau_b_from_t_pt_vs_eta = TH2F("b_from_top_pt_eta_3L1HadTau", "b_from_top_pt_eta_3L1HadTau", 20, 0., 300., 15, -4.5, 4.5)
    h2_3L_secondb_beforeFSR_pt_vs_eta = TH2F("b_from_gluon_pt_eta_3L", "b_from_gluon_pt_eta_3L", 20, 0., 300., 15, -4.5, 4.5)
    h2_3L_b_from_t_pt_vs_eta = TH2F("b_from_top_pt_eta_3L", "b_from_top_pt_eta_3L", 20, 0., 300., 15, -4.5, 4.5)
    
    # Step 2 - Filling
    msg.printGreen("Step 2 - Loop over events to fill the histograms...")
    start_fillAll = time.time()

    # initialize counter for all processed events
    j1 = 0

    # initialize counter for events passing each region
    j2 = {}
    j2["all"] = 0
    for region in SRs: j2[region] = 0

    # set maximum for the progress bar
    progressBarMaxEvents = Truth.GetEntries()
    if options.maxevents > 0: progressBarMaxEvents = options.maxevents

    #Top/Higgs ratio
    TopTopbar_DeltaRMin = {}
    TopTopbar_DeltaPhiMin = {}
    TopTopbar_DeltaEtaMin = {}
    TopTopbar_PtMax = {}
    Number_of_top = {}
    Number_of_topbar = {}
    Top_DeltaRMin = {}
    Top_DeltaPhiMin = {}
    Top_DeltaEtaMin = {}
    Top_PtMax = {}
    Topbar_DeltaRMin = {}
    Topbar_DeltaPhiMin = {}
    Topbar_DeltaEtaMin = {}
    Topbar_PtMax = {}
    Top_DeltaRMinLep = {}
    Top_DeltaPhiMinLep = {}
    Top_DeltaEtaMinLep = {}
    Topbar_DeltaRMinLep = {}
    Topbar_DeltaPhiMinLep = {}
    Topbar_DeltaEtaMinLep = {}
    for region in SRs:
        Number_of_top[region] = 0
        Number_of_topbar[region] = 0
        TopTopbar_DeltaRMin[region] = 0
        TopTopbar_DeltaPhiMin[region] = 0
        TopTopbar_DeltaEtaMin[region] = 0
        TopTopbar_PtMax[region] = 0
        Top_DeltaRMin[region] = 0
        Top_DeltaPhiMin[region] = 0
        Top_DeltaEtaMin[region] = 0
        Top_PtMax[region] = 0
        Top_DeltaRMinLep[region] = 0
        Top_DeltaPhiMinLep[region] = 0
        Top_DeltaEtaMinLep[region] = 0
        Topbar_DeltaRMin[region] = 0
        Topbar_DeltaPhiMin[region] = 0
        Topbar_DeltaEtaMin[region] = 0
        Topbar_PtMax[region] = 0
        Topbar_DeltaRMinLep[region] = 0
        Topbar_DeltaPhiMinLep[region] = 0
        Topbar_DeltaEtaMinLep[region] = 0

    # event loop
    for event in Truth:
        if options.maxevents > 0 and j1 == options.maxevents: break
        j1 = j1+1

        # Progress bar
        if msg.debugLevel > 0:
            sys.stdout.flush()
            sys.stdout.write("\r- Events : {0:.1f} ".format(float(j1)/float(progressBarMaxEvents)*100.)+"%")
            sys.stdout.flush()
        else:
            msg.printDebug("===============================================")
            msg.printDebug(" Event %d" % j1)
            msg.printDebug("===============================================")
            
        if tool.normalize == 'lumi': self.customLabel(labelPos[0], labelPos[1]-0.05, "#sqrt{s} = 13 TeV, 139 fb^{#minus1}")
        elif tool.normalize == 'entries': sum_step ='event.weight_mc'
        elif tool.normalize == 'nonorm': sum_step = '1'
        else: sum_step = 1

        # Fill common histos (all events)
        tool.FillBasic1DCommonHistos(event, histosInSR)
            
        # selection
        selectionPerRegion = []
        for region in SRs:
            #print 'region',region
            selectionPerRegion += [ tool.Region(event, region) ]
            #if tool.Region(event, region): j2[region] = j2[region] + eval(sum_step)
        if not any(selectionPerRegion): continue
            
        msg.printDebug("- Event accepted!!!")

        # Fill basic histos per signal region
        tool.FillBasic1DHistos(event, histosInSR)                  # appear explicitly in the tree
        tool.FillChargeAndMtHistos(event, ChargeHistos, MtHistos)  # M_T and charge for particles with pdgId info in Tree 

        j2["all"] = j2["all"] + eval(sum_step)

        # TO DO: cada evento tiene un factor para normalizacion differente (normalizar event by event)
          
        #########################################################################
        #Plots for 3L1HadTau Region
        #########################################################################
        if tool.Region(event, '3L1HadTau'):
            j2['3L1HadTau'] = j2['3L1HadTau'] + eval(sum_step)
            if tool.channel == 'Htautau':
                decay_1 = [tool.TLorentz('MC_W_decay1_from_Tau1',event),event.MC_W_decay1_from_Tau1_pdgId,15]
                decay_2 = [tool.TLorentz('MC_W_decay1_from_Tau2',event),event.MC_W_decay1_from_Tau2_pdgId,15]
                decay_1_nu = [tool.TLorentz('MC_W_decay2_from_Tau1',event),event.MC_W_decay2_from_Tau1_pdgId,15]
                decay_2_nu = [tool.TLorentz('MC_W_decay2_from_Tau2',event),event.MC_W_decay2_from_Tau2_pdgId,15]
                tau1_nu_pt = event.MC_H_decay1_pt - decay_1[0].Pt() - decay_1_nu[0].Pt()# <- The first chidren of H have netrino decay
                tau2_nu_pt = event.MC_H_decay2_pt - decay_2[0].Pt() - decay_2_nu[0].Pt() # Pt(neutrino of tau) = Pt(Tau) - Pt(W_from_tau)
            elif tool.channel == 'HWW':
                decay_1 = [tool.TLorentz('MC_W_decay1_from_W1',event),event.MC_W_decay1_from_W1_pdgId,15]
                decay_2 = [tool.TLorentz('MC_W_decay1_from_W2',event),event.MC_W_decay1_from_W2_pdgId,15]
                decay_1_nu = [tool.TLorentz('MC_W_decay2_from_W1',event),event.MC_W_decay2_from_W1_pdgId,15]
                decay_2_nu = [tool.TLorentz('MC_W_decay2_from_W2',event),event.MC_W_decay2_from_W2_pdgId,15]
                tau1_nu_pt = 0 # <- The first chidren of H do not have netrino decay
                tau2_nu_pt = 0
            elif tool.channel == 'HZZ1':
                decay_1 = [tool.TLorentz('MC_Z_Lepton1_from_Z1',event),event.MC_Z_Lepton1_from_Z1_pdgId,23]
                decay_2 = [tool.TLorentz('MC_Z_Lepton2_from_Z1',event),event.MC_Z_Lepton2_from_Z1_pdgId,23]
                decay_1_nu, decay_2_nu, tau1_nu_pt, tau2_nu_pt = 0., 0., 0., 0.
            elif tool.channel == 'HZZ2':
                decay_1 = [tool.TLorentz('MC_Z_Lepton1_from_Z2',event),event.MC_Z_Lepton1_from_Z2_pdgId,23]
                decay_2 = [tool.TLorentz('MC_Z_Lepton2_from_Z2',event),event.MC_Z_Lepton2_from_Z2_pdgId,23]
                decay_1_nu, decay_2_nu, tau1_nu_pt, tau2_nu_pt = 0., 0., 0., 0.
            decay_1_top = [tool.TLorentz('MC_Wdecay1_from_t',event),event.MC_Wdecay1_from_t_pdgId,6]
            b_jet =[tool.TLorentz('MC_b_from_t',event),5,5]
            MC_top_Lorentz = tool.ChildsToParent(event, 3,"MC_Wdecay1_from_t", "MC_Wdecay2_from_t","MC_b_from_t")
            MC_W_from_t_Lorentz = tool.ChildsToParent(event, 2, "MC_Wdecay1_from_t", "MC_Wdecay2_from_t", "")
            #Calculate DeltaR, DeltaPhi, DeltaEta decay_*-b_jet                                                                                                                  
            # Particles is a list where each element has [TLorentz,pdgID,parentPdgID,DeltaR,DeltaPhi,DeltaEta]                                                                   
            Particles = tool.DeltaDecayBjet(decay_1,decay_2,decay_1_top,b_jet)
            if tool.channel == 'HZZ1' or tool.channel == 'HZZ2':
                MET = decay_1_nu + decay_2_nu + event.MC_Wdecay2_from_t_pt + tau1_nu_pt + tau2_nu_pt #+ el otro Z se puede ir a neutrinos :/
            else:
                MET = decay_1_nu[0].Pt() + decay_2_nu[0].Pt() + event.MC_Wdecay2_from_t_pt + tau1_nu_pt + tau2_nu_pt

            #Check if minimun DeltaR is top-b_jet (inclusive top)                                                                                    
            sort_particle_deltaR =sorted(Particles, key = lambda Particles: Particles[3])
            sort_particle_deltaPhi = sorted(Particles, key = lambda Particles: Particles[4])
            if sort_particle_deltaR[0][2]==6:
                TopTopbar_DeltaRMin['3L1HadTau'] = TopTopbar_DeltaRMin['3L1HadTau'] + 1
            #Check if minimun DeltaPhi is top-b_jet (inclusive top)
            if sort_particle_deltaPhi[0][2]==6:
                TopTopbar_DeltaPhiMin['3L1HadTau'] = TopTopbar_DeltaPhiMin['3L1HadTau'] + 1
            #Check if maximun Pt comming from  top (inclusive top)                                                                                                                                         
            if decay_1_top[0].Pt() > decay_1[0].Pt() and decay_1_top[0].Pt() > decay_2[0].Pt():
                TopTopbar_PtMax['3L1HadTau'] = TopTopbar_PtMax['3L1HadTau']  + 1
            #Check same variableas as before but for top and top bar
            if sort_particle_deltaR[0][2]==6 and (sort_particle_deltaR[0][1]==-11 or sort_particle_deltaR[0][1]==-13 or sort_particle_deltaR[0][1]==24):
                Top_DeltaRMin['3L1HadTau'] = Top_DeltaRMin['3L1HadTau'] + 1
            if sort_particle_deltaPhi[0][2]==6 and (sort_particle_deltaPhi[0][1]==-11 or sort_particle_deltaPhi[0][1]==-13 or sort_particle_deltaPhi[0][1]==24):
                Top_DeltaPhiMin['3L1HadTau'] = Top_DeltaPhiMin['3L1HadTau'] + 1
            if sort_particle_deltaR[0][2]==6 and (sort_particle_deltaR[0][1]==11 or sort_particle_deltaR[0][1]==13 or sort_particle_deltaR[0][1]==-24):
                Topbar_DeltaRMin['3L1HadTau'] = Topbar_DeltaRMin['3L1HadTau'] + 1
            if sort_particle_deltaPhi[0][2]==6 and (sort_particle_deltaPhi[0][1]==11 or sort_particle_deltaPhi[0][1]==13 or sort_particle_deltaPhi[0][1]==-24):
                Topbar_DeltaPhiMin['3L1HadTau'] = Topbar_DeltaPhiMin['3L1HadTau'] + 1
            #Same variables as before for the pair of leptons with the same charge
            if decay_1_top[1]==-11 or decay_1_top[1]==-13 or decay_1_top[1]==24:
                Number_of_top['3L1HadTau'] = Number_of_top['3L1HadTau'] + 1
                if (np.sign(decay_1[1])>0 or decay_1[1]==-24) and decay_1[1]!=24:
                    neg_child = decay_1
                else:
                    pos_child = decay_1
                if (np.sign(decay_2[1])>0 or decay_2[1]==-24) and decay_2[1]!=24:
                    neg_child = decay_2
                else:
                    pos_child = decay_2                    
                if  tool.DeltaR(neg_child[0],decay_1_top[0])<tool.DeltaR(neg_child[0],pos_child[0]):
                    Top_DeltaRMinLep['3L1HadTau'] = Top_DeltaRMinLep['3L1HadTau'] + 1
                if  tool.DeltaPhi(neg_child[0],decay_1_top[0])<tool.DeltaPhi(neg_child[0],pos_child[0]):
                    Top_DeltaPhiMinLep['3L1HadTau'] = Top_DeltaPhiMinLep['3L1HadTau'] + 1
                if decay_1_top[0].Pt() > pos_child[0].Pt():
                    Top_PtMax['3L1HadTau'] = Top_PtMax['3L1HadTau'] + 1
            else:
                Number_of_topbar['3L1HadTau'] = Number_of_topbar['3L1HadTau'] + 1
                if (np.sign(decay_1[1])>0 or decay_1[1]==-24) and decay_1[1]!=24:
                    neg_child = decay_1
                else:
                    pos_child = decay_1
                if (np.sign(decay_2[1])>0 or decay_2[1]==-24) and decay_2[1]!=24:
                    neg_child = decay_2
                else:
                    pos_child = decay_2
                if  tool.DeltaR(pos_child[0],decay_1_top[0])<tool.DeltaR(neg_child[0],pos_child[0]):
                    Topbar_DeltaRMinLep['3L1HadTau'] = Topbar_DeltaRMinLep['3L1HadTau'] + 1
                if  tool.DeltaPhi(pos_child[0],decay_1_top[0])<tool.DeltaPhi(neg_child[0],pos_child[0]):
                    Topbar_DeltaPhiMinLep['3L1HadTau'] = Topbar_DeltaPhiMinLep['3L1HadTau'] + 1
                if decay_1_top[0].Pt() > neg_child[0].Pt():
                    Topbar_PtMax['3L1HadTau'] = Topbar_PtMax['3L1HadTau']  + 1


            #Simple histograms
            h1_Wdecay1_AllEvent_m.Fill(decay_1[0].M()/1000.,event.weight_mc)
            h1_Wdecay1_AllEvent_phi.Fill(decay_1[0].Phi(),event.weight_mc)
            h1_Wdecay1_AllEvent_eta.Fill(decay_1[0].Eta(),event.weight_mc)
            h1_Wdecay1_AllEvent_pt.Fill(decay_1[0].Pt()/1000.,event.weight_mc)

            h1_Wdecay2_AllEvent_m.Fill(decay_2[0].M()/1000.,event.weight_mc)
            h1_Wdecay2_AllEvent_phi.Fill(decay_2[0].Phi(),event.weight_mc)
            h1_Wdecay2_AllEvent_eta.Fill(decay_2[0].Eta(),event.weight_mc)
            h1_Wdecay2_AllEvent_pt.Fill(decay_2[0].Pt()/1000.,event.weight_mc)

            # Combined plots
            h1_nu_from_t_pz.Fill((tool.P_z("MC_Wdecay2_from_t",event))/1000, event.weight_mc) #pz in GeV
            h1_lp_from_t_pz.Fill((tool.P_z("MC_Wdecay1_from_t",event))/1000, event.weight_mc)
            h1_pz_ratio.Fill((tool.P_z("MC_Wdecay2_from_t",event)/tool.P_z("MC_Wdecay1_from_t",event)), event.weight_mc)
            aux_H = tool.ChildsToParent(event, 2, "MC_H_decay1", "MC_H_decay2", " ") # We create a TLorentzVector for the Higgs boson
            h1_Higgs_m.Fill((aux_H.M())/1000, event.weight_mc)
            h1_Higgs_pt.Fill((aux_H.Pt())/1000, event.weight_mc)
            h1_Higgs_pz.Fill((aux_H.Pz())/1000, event.weight_mc)
            h1_Higgs_eta.Fill(aux_H.Eta(), event.weight_mc)
            h1_Higgs_phi.Fill(aux_H.Phi(), event.weight_mc)
            aux_t = tool.ChildsToParent(event,3, "MC_Wdecay1_from_t", "MC_Wdecay2_from_t", "MC_b_from_t")
            h1_top_m.Fill((aux_t.M())/1000, event.weight_mc)
            h1_top_pt.Fill((aux_t.Pt())/1000, event.weight_mc)
            h1_top_pz.Fill((aux_t.Pz())/1000, event.weight_mc)
            h1_top_eta.Fill(aux_t.Eta(), event.weight_mc)
            h1_top_phi.Fill(aux_t.Phi(), event.weight_mc)
            if abs(event.MC_Higgs_decay1_pdgId) == 15:
                HT = event.MC_secondb_afterFSR_pt + event.MC_b_from_t_pt + event.MC_Wdecay1_from_t_pt + event.MC_Wdecay2_from_t_pt + event.MC_W_decay1_from_Tau1_pt +\
                  event.MC_W_decay2_from_Tau1_pt + event.MC_W_decay1_from_Tau2_pt +event.MC_W_decay2_from_Tau2_pt # + event.MC_q_pt
            if abs(event.MC_Higgs_decay1_pdgId) == 24:
                HT = event.MC_secondb_afterFSR_pt + event.MC_b_from_t_pt + event.MC_Wdecay1_from_t_pt + event.MC_Wdecay2_from_t_pt + event.MC_W_decay1_from_W1_pt +event.MC_W_decay2_from_W1_pt +\
                  event.MC_W_decay1_from_W2_pt +event.MC_W_decay2_from_W2_pt # + event.MC_q_pt 
            if tool.channel == 'HZZ1':
                HT = event.MC_secondb_afterFSR_pt + event.MC_b_from_t_pt + event.MC_Wdecay1_from_t_pt + event.MC_Wdecay2_from_t_pt + decay_1[0].Pt() + decay_2[0].Pt() + event.MC_H_decay2_pt
            if tool.channel == 'HZZ1':
                HT = event.MC_secondb_afterFSR_pt + event.MC_b_from_t_pt + event.MC_Wdecay1_from_t_pt + event.MC_Wdecay2_from_t_pt + decay_1[0].Pt() + decay_2[0].Pt()+ event.MC_H_decay1_pt
            
            h1_HT.Fill(HT/1000, event.weight_mc)
            h1_DeltaEta_bl_from_t_3L1HadTau.Fill(event.MC_Wdecay1_from_t_eta - event.MC_b_from_t_eta, event.weight_mc)
            h1_DeltaPhi_bl_from_t_3L1HadTau.Fill(tool.DeltaPhi(tool.TLorentz("MC_Wdecay1_from_t", event), tool.TLorentz("MC_b_from_t", event)), event.weight_mc)
            h1_DeltaR_bl_from_t_3L1HadTau.Fill(tool.DeltaR(tool.TLorentz("MC_Wdecay1_from_t", event), tool.TLorentz("MC_b_from_t", event)), event.weight_mc)

            h1_DeltaEta_Hdecay1and2_3L1HadTau.Fill(event.MC_H_decay1_eta - event.MC_H_decay2_eta, event.weight_mc )#eta between taus or WW                                                                  
            h1_DeltaPhi_Hdecay1and2_3L1HadTau.Fill(tool.DeltaPhi(tool.TLorentz("MC_H_decay1", event),tool.TLorentz("MC_H_decay2", event)), event.weight_mc)
            h1_DeltaR_Hdecay1and2_3L1HadTau.Fill(tool.DeltaR(tool.TLorentz("MC_H_decay1", event),tool.TLorentz("MC_H_decay2", event)), event.weight_mc)

            h1_MET_3L1HadTau.Fill(MET/1000, event.weight_mc)
            h1_t_MT_3L1HadTau.Fill(MC_top_Lorentz.Mt()/1000, event.weight_mc)
            h1_W_from_t_MT_3L1HadTau.Fill(MC_W_from_t_Lorentz.Mt()/1000, event.weight_mc)
            
            # In the 3L1HadTau we have to check whether the Wdecay1 is a lepton or hadron. For the mlb variable only leptons are allowed
            if abs(event.MC_Wdecay1_from_t_pdgId) in [11, 13, 15]:
                h1_mlb_3L1HadTau.Fill((tool.TLorentz("MC_Wdecay1_from_t", event) +  b_jet[0]).M() / 1000, event.weight_mc)
            if tool.channel == 'Htautau':
                if abs(event.MC_W_decay1_from_Tau1_pdgId) in [11, 13, 15]:
                    h1_mlb_l_fromHdec1_3L1HadTau.Fill((decay_1[0] +  b_jet[0]).M() / 1000, event.weight_mc)
                if abs(event.MC_W_decay1_from_Tau2_pdgId) in [11, 13, 15]:
                    h1_mlb_l_fromHdec2_3L1HadTau.Fill((decay_2[0] +  b_jet[0]).M() / 1000, event.weight_mc)
            elif tool.channel == 'HWW':
                if abs(event.MC_W_decay1_from_W1_pdgId) in [11, 13, 15]:
                    h1_mlb_l_fromHdec1_3L1HadTau.Fill((decay_1[0] +  b_jet[0]).M() / 1000, event.weight_mc)
                if abs(event.MC_W_decay1_from_W2_pdgId) in [11, 13, 15]:
                    h1_mlb_l_fromHdec2_3L1HadTau.Fill((decay_2[0] +  b_jet[0]).M() / 1000, event.weight_mc)
            
            h1_DeltaEta_W1_from_Hdecay1and2_3L1HadTau.Fill(decay_1[0].Eta() - decay_2[0].Eta(), event.weight_mc ) #DeltaEta between W1decay of Tau1and Tau2 or W1andW2                                      
            h1_DeltaPhi_W1_from_Hdecay1and2_3L1HadTau.Fill(tool.DeltaPhi(decay_1[0], decay_2[0]), event.weight_mc )
            h1_DeltaR_W1_from_Hdecay1and2_3L1HadTau.Fill(tool.DeltaR(decay_1[0], decay_2[0]), event.weight_mc)
            
            #Fill 2D                                                                                                                                                                                        
            h2_Wdecay_from_tau1_pdgidVSeta.Fill(event.MC_W_decay1_from_Tau1_eta, event.MC_W_decay1_from_Tau1_pdgId)
            h2_Wdecay_from_tau1_pdgidVSpt.Fill(event.MC_W_decay1_from_Tau1_pt/1000, event.MC_W_decay1_from_Tau1_pdgId)
            h2_3L1HadTau_secondb_beforeFSR_pt_vs_eta.Fill(event.MC_secondb_beforeFSR_pt/1000, event.MC_secondb_beforeFSR_eta, event.weight_mc)           
            h2_3L1HadTau_b_from_t_pt_vs_eta.Fill(event.MC_b_from_t_pt/1000, event.MC_b_from_t_eta, event.weight_mc)
            
        #########################################################################
        #Plots for 3L Region
        #########################################################################
        if tool.Region(event, '3L'):
            j2['3L'] = j2['3L'] + eval(sum_step)
            if tool.channel == 'Htautau':
                decay_1 = [tool.TLorentz('MC_W_decay1_from_Tau1',event),event.MC_W_decay1_from_Tau1_pdgId,15]
                decay_2 = [tool.TLorentz('MC_W_decay1_from_Tau2',event),event.MC_W_decay1_from_Tau2_pdgId,15]
                decay_1_nu = [tool.TLorentz('MC_W_decay2_from_Tau1',event),event.MC_W_decay2_from_Tau1_pdgId,15]
                decay_2_nu = [tool.TLorentz('MC_W_decay2_from_Tau2',event),event.MC_W_decay2_from_Tau2_pdgId,15]
                tau1_nu_pt = event.MC_H_decay1_pt - decay_1[0].Pt() - decay_1_nu[0].Pt()
                tau2_nu_pt = event.MC_H_decay2_pt - decay_2[0].Pt() - decay_2_nu[0].Pt()
            elif tool.channel == 'HWW':
                decay_1 = [tool.TLorentz('MC_W_decay1_from_W1',event),event.MC_W_decay1_from_W1_pdgId,24]
                decay_2 = [tool.TLorentz('MC_W_decay1_from_W2',event),event.MC_W_decay1_from_W2_pdgId,24]
                decay_1_nu = [tool.TLorentz('MC_W_decay2_from_W1',event),event.MC_W_decay2_from_W1_pdgId,24]
                decay_2_nu = [tool.TLorentz('MC_W_decay2_from_W2',event),event.MC_W_decay2_from_W2_pdgId,24]
                tau1_nu_pt, tau2_nu_pt = 0., 0.
            elif tool.channel == 'HZZ1':
                decay_1 = [tool.TLorentz('MC_Z_Lepton1_from_Z1',event),event.MC_Z_Lepton1_from_Z1_pdgId,23]
                decay_2 = [tool.TLorentz('MC_Z_Lepton2_from_Z1',event),event.MC_Z_Lepton2_from_Z1_pdgId,23]
                decay_1_nu, decay_2_nu, tau1_nu_pt, tau2_nu_pt = 0., 0., 0., 0.
            elif tool.channel == 'HZZ2':
                decay_1 = [tool.TLorentz('MC_Z_Lepton1_from_Z2',event),event.MC_Z_Lepton1_from_Z2_pdgId,23]
                decay_2 = [tool.TLorentz('MC_Z_Lepton2_from_Z2',event),event.MC_Z_Lepton2_from_Z2_pdgId,23]
                decay_1_nu, decay_2_nu, tau1_nu_pt, tau2_nu_pt = 0., 0., 0., 0.
            decay_1_top = [tool.TLorentz('MC_Wdecay1_from_t',event),event.MC_Wdecay1_from_t_pdgId,6]
            b_jet =[tool.TLorentz('MC_b_from_t',event),5,5]
            MC_top_Lorentz = tool.ChildsToParent(event, 3,"MC_Wdecay1_from_t", "MC_Wdecay2_from_t","MC_b_from_t")
            MC_W_from_t_Lorentz = tool.ChildsToParent(event, 2, "MC_Wdecay1_from_t", "MC_Wdecay2_from_t", "")
            if tool.channel == 'HZZ1' or tool.channel == 'HZZ2':
                MET = decay_1_nu + decay_2_nu + event.MC_Wdecay2_from_t_pt + tau1_nu_pt + tau2_nu_pt
            else:
                MET = decay_1_nu[0].Pt() + decay_2_nu[0].Pt() + event.MC_Wdecay2_from_t_pt + tau1_nu_pt + tau2_nu_pt

            #Calculate DeltaR, DeltaPhi, DeltaEta decay_*-b_jet
            # Particles is a list where each element has [TLorentz,pdgID,parentPdgID,DeltaR,DeltaPhi,DeltaEta]
            Particles = tool.DeltaDecayBjet(decay_1,decay_2,decay_1_top,b_jet)
            #Check if minimun DeltaR is top-b_jet (inclusive top)
            sort_particle_deltaR =sorted(Particles, key = lambda Particles: Particles[3])
            sort_particle_deltaPhi = sorted(Particles, key = lambda Particles: Particles[4])
            sort_particle_deltaEta = sorted(Particles, key = lambda Particles: Particles[5])
            if sort_particle_deltaR[0][2]==6:
                TopTopbar_DeltaRMin['3L'] = TopTopbar_DeltaRMin['3L'] + eval(sum_step)
            #Check if minimun DeltaPhi is top-b_jet (inclusive top)
            if sort_particle_deltaPhi[0][2]==6:
                TopTopbar_DeltaPhiMin['3L'] = TopTopbar_DeltaPhiMin['3L'] + eval(sum_step)
            #Check if minimun DeltaEta is top-b_jet (inclusive top)
            if sort_particle_deltaEta[0][2]==6:
                TopTopbar_DeltaEtaMin['3L'] = TopTopbar_DeltaEtaMin['3L'] + eval(sum_step)
            #Check if maximun Pt comming from  top (inclusive top) 
            if decay_1_top[0].Pt() > decay_1[0].Pt() and decay_1_top[0].Pt() > decay_2[0].Pt():
                TopTopbar_PtMax['3L'] = TopTopbar_PtMax['3L']  + eval(sum_step)
            #Chack same variableas as before but for top and top bar
            if sort_particle_deltaR[0][2]==6 and np.sign(sort_particle_deltaR[0][1])<0:
                Top_DeltaRMin['3L'] = Top_DeltaRMin['3L'] + eval(sum_step)
            if sort_particle_deltaPhi[0][2]==6 and np.sign(sort_particle_deltaPhi[0][1])<0:
                Top_DeltaPhiMin['3L'] = Top_DeltaPhiMin['3L'] + eval(sum_step)
            if sort_particle_deltaEta[0][2]==6 and np.sign(sort_particle_deltaEta[0][1])<0:
                Top_DeltaEtaMin['3L'] = Top_DeltaEtaMin['3L'] + eval(sum_step)
            if sort_particle_deltaR[0][2]==6 and np.sign(sort_particle_deltaR[0][1])>0:
                Topbar_DeltaRMin['3L'] = Topbar_DeltaRMin['3L'] + eval(sum_step)
            if sort_particle_deltaPhi[0][2]==6 and np.sign(sort_particle_deltaPhi[0][1])>0:
                Topbar_DeltaPhiMin['3L'] = Topbar_DeltaPhiMin['3L'] + eval(sum_step)
            if sort_particle_deltaEta[0][2]==6 and np.sign(sort_particle_deltaEta[0][1])>0:
                Topbar_DeltaEtaMin['3L'] = Topbar_DeltaEtaMin['3L'] + eval(sum_step)
            #Same variables as before for the pair of leptons with the same charge
            if np.sign(decay_1_top[1])<0:
                Number_of_top['3L'] = Number_of_top['3L'] + eval(sum_step)
                if np.sign(decay_1[1])>0:
                    neg_child = decay_1
                else:
                    pos_child = decay_1
                if np.sign(decay_2[1])>0:
                    neg_child = decay_2
                else:
                    pos_child = decay_2
                if  tool.DeltaR(neg_child[0],decay_1_top[0])<tool.DeltaR(neg_child[0],pos_child[0]):
                    Top_DeltaRMinLep['3L'] = Top_DeltaRMinLep['3L'] + eval(sum_step)
                if  tool.DeltaPhi(neg_child[0],decay_1_top[0])<tool.DeltaPhi(neg_child[0],pos_child[0]):
                    Top_DeltaPhiMinLep['3L'] = Top_DeltaPhiMinLep['3L'] + eval(sum_step)
                if  neg_child[0].Eta()-decay_1_top[0].Eta()<neg_child[0].Eta()-pos_child[0].Eta():
                    Top_DeltaEtaMinLep['3L'] = Top_DeltaEtaMinLep['3L'] + eval(sum_step)
                if decay_1_top[0].Pt() > pos_child[0].Pt():
                    Top_PtMax['3L'] = Top_PtMax['3L']  + eval(sum_step)
            else:
                Number_of_topbar['3L'] = Number_of_topbar['3L'] + eval(sum_step)
                if np.sign(decay_1[1])>0:
                    neg_child = decay_1
                else:
                    pos_child = decay_1
                if np.sign(decay_2[1])>0:
                    neg_child = decay_2
                else:
                    pos_child = decay_2
                if  tool.DeltaR(pos_child[0],decay_1_top[0])<tool.DeltaR(neg_child[0],pos_child[0]):
                    Topbar_DeltaRMinLep['3L'] = Topbar_DeltaRMinLep['3L'] + eval(sum_step)
                if  tool.DeltaPhi(pos_child[0],decay_1_top[0])<tool.DeltaPhi(neg_child[0],pos_child[0]):
                    Topbar_DeltaPhiMinLep['3L'] = Topbar_DeltaPhiMinLep['3L'] + eval(sum_step)
                if  pos_child[0].Eta()-decay_1_top[0].Eta()<pos_child[0].Eta()-neg_child[0].Eta():
                    Topbar_DeltaEtaMinLep['3L'] = Topbar_DeltaEtaMinLep['3L'] + eval(sum_step)
                if decay_1_top[0].Pt() > neg_child[0].Pt():
                    Topbar_PtMax['3L'] = Topbar_PtMax['3L']  + eval(sum_step)

                        # Comb                                                                                                                                                                                          
            h1_DeltaEta_bl_from_t_3L.Fill(event.MC_Wdecay1_from_t_eta - event.MC_b_from_t_eta, event.weight_mc)
            h1_DeltaEta_bl_from_t_3L.Fill(event.MC_Wdecay1_from_t_eta - event.MC_b_from_t_eta, event.weight_mc)
            h1_DeltaPhi_bl_from_t_3L.Fill(tool.DeltaPhi(tool.TLorentz("MC_Wdecay1_from_t", event), tool.TLorentz("MC_b_from_t", event)), event.weight_mc)
            h1_DeltaR_bl_from_t_3L.Fill(tool.DeltaR(tool.TLorentz("MC_Wdecay1_from_t", event), tool.TLorentz("MC_b_from_t", event)), event.weight_mc)
            h1_DeltaEta_Hdecay1and2_3L.Fill(event.MC_H_decay1_eta - event.MC_H_decay2_eta, event.weight_mc ) #  eta between higgs childs                                                                    
            h1_DeltaPhi_Hdecay1and2_3L.Fill(tool.DeltaPhi(tool.TLorentz("MC_H_decay1", event),tool.TLorentz("MC_H_decay2", event)), event.weight_mc)
            h1_DeltaR_Hdecay1and2_3L.Fill(tool.DeltaR(tool.TLorentz("MC_H_decay1", event),tool.TLorentz("MC_H_decay2", event)), event.weight_mc)
            h1_DeltaEta_W1_from_Hdecay1and2_3L.Fill(decay_1[0].Eta() - decay_2[0].Eta(), event.weight_mc) #DeltaEta between leptons of higgs                                                                
            h1_DeltaPhi_W1_from_Hdecay1and2_3L.Fill(tool.DeltaPhi(decay_1[0], decay_2[0]), event.weight_mc)
            h1_DeltaR_W1_from_Hdecay1and2_3L.Fill(tool.DeltaR(decay_1[0], decay_2[0]), event.weight_mc)

            h1_MET_3L.Fill(MET/1000, event.weight_mc)
            h1_t_MT_3L.Fill(MC_top_Lorentz.Mt()/1000, event.weight_mc)
            h1_W_from_t_MT_3L.Fill(MC_W_from_t_Lorentz.Mt()/1000, event.weight_mc)
            
            h1_mlb_3L.Fill((tool.TLorentz("MC_Wdecay1_from_t", event) + b_jet[0]).M() / 1000, event.weight_mc)
            h1_mlb_l_fromHdec1_3L.Fill((decay_1[0] + b_jet[0]).M() / 1000, event.weight_mc)
            h1_mlb_l_fromHdec2_3L.Fill((decay_2[0] + b_jet[0]).M() / 1000, event.weight_mc)

            #2D                                                                                                                                                                                             
            h2_3L_secondb_beforeFSR_pt_vs_eta.Fill(event.MC_secondb_beforeFSR_pt/1000, event.MC_secondb_beforeFSR_eta, event.weight_mc)
            h2_3L_b_from_t_pt_vs_eta.Fill(event.MC_b_from_t_pt/1000, event.MC_b_from_t_eta, event.weight_mc)
            
    sys.stdout.write('\n')
    #msg.printInfo("Processed events: %2.1f%% [%d/%d]" % (100*float(j1)/float(Truth.GetEntries()), j1, Truth.GetEntries()))
    msg.printInfo("Events that pass all regions: %d" % j2["all"])
    for region in SRs:
        msg.printInfo("- Events that pass region %s: %d" % (region, j2[region]))

    end_fillAll =  time.time()
    msg.printInfo("Filling time: "+ str((end_fillAll - start_fillAll)/1) + " s")
    
    # Step 3 - Drawing
    msg.printGreen("Step 3 - Drawing and saving the histograms")
    start_drawAll = time.time()

    # draw plots for pdgIds
    tool.DrawDonutsForHiggsDecay(histosInSR)
    tool.DrawDonutsForPDGIds(histosInSR)
    
    # Histos - Basic
    tool.DrawBasic1DHistos(histosInSR)

    # Histos - Combined
    # 3L1HadTau signal region
    tool.DrawChargeAndMtHistos(ChargeHistos, MtHistos)
    tool.DrawOneBasic(h1_nu_from_t_pz, '3L1HadTau', ["p_{z}(W decay2 from t) ", 50., -1000., 1000., "W_decay2_from_t", "GeV"],"MC_W_decay2_from_t_pz")
    tool.DrawOneBasic(h1_lp_from_t_pz, '3L1HadTau', ["p_{z}(W decay1 from t) ", 50., -800., 800., "W_decay1_from_t", "GeV"],"MC_W_decay1_from_t_pz")
    tool.DrawOneBasic(h1_pz_ratio, '3L1HadTau', ["W dec from t p_{z}^{nu} / p_{z}^{lp}  ", 50., 0., 1., "alpha", " "], "alpha")
    tool.DrawOneBasic(h1_Higgs_m , '3L1HadTau', ["m(H)", 20., 124., 126., "Higgs_m", "GeV"], "MC_Higgs_m")
    tool.DrawOneBasic(h1_Higgs_pt , '3L1HadTau', ["p_{T}(H)", 50., 0., 500., "Higgs_pt", "GeV"], "MC_Higgs_pt")
    tool.DrawOneBasic(h1_Higgs_eta , '3L1HadTau', ["#eta(H)", 20., -4.5, 4.5, "Higgs_eta", ""], "MC_Higgs_eta")
    tool.DrawOneBasic(h1_Higgs_phi , '3L1HadTau', ["#phi(H)", 21., -TMath.Pi(), TMath.Pi(), "Higgs_phi", "rad"], "MC_Higgs_phi")
    tool.DrawOneBasic(h1_Higgs_pz , '3L1HadTau', ["p_{z}(H)", 40., 0., 400., "Higgs_pz", "GeV"], "MC_Higgs_pz")
    tool.DrawOneBasic(h1_top_m , '3L1HadTau', ["m(t)", 20, 100., 200., "top_m", "GeV"], "MC_t_m")
    tool.DrawOneBasic(h1_top_pt , '3L1HadTau', ["p_{T}(t)", 40, 0., 400., "top_pt", "GeV"], "MC_t_pt")
    tool.DrawOneBasic(h1_top_pz , '3L1HadTau', ["p_{z}(t)", 40, 0., 400., "top_pz", "GeV"], "MC_t_pz")
    tool.DrawOneBasic(h1_top_eta , '3L1HadTau', ["#eta(t)", 20, -4.5, 4.5, "top_eta", ""], "MC_t_eta")
    tool.DrawOneBasic(h1_top_phi , '3L1HadTau', ["#phi(t)", 21, -TMath.Pi(), TMath.Pi(), "top_phi", "rad"], "MC_t_phi")
    tool.DrawOneBasic(h1_HT , '3L1HadTau', ["H_{T}", 75, 0., 750., "HT", "GeV"], "MC_HT")
    tool.DrawOneBasic(h1_DeltaEta_bl_from_t_3L1HadTau, '3L1HadTau', ["#Delta#eta(bl) with l from t}", 20, -4.5, 4.5, "deltaEta_lb_from_t", " "], "MC_b_from_and_Wdecay1_from_t_Delta_eta")
    tool.DrawOneBasic(h1_DeltaPhi_bl_from_t_3L1HadTau, '3L1HadTau', ["#Delta#phi(bl) with l from t}", 21, -TMath.Pi(), TMath.Pi(), "deltaPhi_lb_from_t", "rad"], "MC_b_from_and_Wdecay1_from_t_Delta_phi")
    tool.DrawOneBasic(h1_DeltaR_bl_from_t_3L1HadTau, '3L1HadTau', ["#DeltaR(bl) with l from t}", 20, 0., 6., "deltaR_lb_from_t", " "], "MC_b_from_and_Wdecay1_from_t_Delta_R")
    tool.DrawOneBasic(h1_DeltaEta_Hdecay1and2_3L1HadTau, '3L1HadTau', ["#Delta#eta(H decay1, H decay2)",  20, -4.5, 4.5, "deltaEta_Hdecay1and2", " "], "MC_Hdecay_1_and_2_Delta_eta")
    tool.DrawOneBasic(h1_DeltaPhi_Hdecay1and2_3L1HadTau, '3L1HadTau', ["#Delta#phi(H decay1, H decay2)",  20, -TMath.Pi(), TMath.Pi(), "deltaPhi_Hdecay1and2", " "], "MC_Hdecay_1_and_2_Delta_phi")
    tool.DrawOneBasic(h1_DeltaR_Hdecay1and2_3L1HadTau, '3L1HadTau', ["#DeltaR(H decay1, H decay2)",  20, 0., 6., "deltaR_Hdecay1and2", " "], "MC_Hdecay_1_and_2_Delta_R")
    tool.DrawOneBasic(h1_DeltaEta_W1_from_Hdecay1and2_3L1HadTau, '3L1HadTau', ["#Delta#eta(decay1s from decays 1 and 2 from H)",  20, -4.5, 4.5, "deltaEta_W1_from_Hdecay1and2", " "], "MC_W1_Hdecays_Delta_eta")
    tool.DrawOneBasic(h1_DeltaPhi_W1_from_Hdecay1and2_3L1HadTau, '3L1HadTau', ["#Delta#phi(decay1s from decays 1 and 2 from H)",  20, -TMath.Pi(), TMath.Pi(), "deltaPhi_W1_from_Hdecay1and2", " "], "MC_W1_Hdecays_Delta_phi")
    tool.DrawOneBasic(h1_DeltaR_W1_from_Hdecay1and2_3L1HadTau, '3L1HadTau', ["#DeltaR(decay1s from decays 1 and 2 from H)",  20, 0., 6., "deltaR_W1_from_Hdecay1and2", " "], "MC_W1_Hdecays_Delta_R")
    #tool.DrawOneBasic(h1_Mass_decay1_AllEvent,'3L1HadTau', ["mass",126., 0., 1000., "m", "GeV"], "MC_m")

    tool.DrawOneBasic(h1_Wdecay1_AllEvent_m,'3L1HadTau', ["mass", 40, -3.5, 3.5, "m", "GeV"], "MC_AllEvent_Wdecay1_m")
    tool.DrawOneBasic(h1_Wdecay1_AllEvent_phi,'3L1HadTau', ["#phi ", 21, -TMath.Pi(), TMath.Pi(), "phi", "rad"], "MC_AllEvent_Wdecay1_phi")
    tool.DrawOneBasic(h1_Wdecay1_AllEvent_eta,'3L1HadTau', ["#eta", 15, -4.5, 4.5, "eta", ""], "MC_AllEvent_Wdecay1_eta")
    tool.DrawOneBasic(h1_Wdecay1_AllEvent_pt,'3L1HadTau', ["p_{T}", 75, 0., 400., "pt", "GeV"], "MC_AllEvent_Wdecay1_pt")

    tool.DrawOneBasic(h1_Wdecay2_AllEvent_m,'3L1HadTau', ["mass", 40, -3.5, 3.5, "m", "GeV"], "MC_AllEvent_Wdecay_2_m")
    tool.DrawOneBasic(h1_Wdecay2_AllEvent_phi,'3L1HadTau', ["#phi ", 21, -TMath.Pi(), TMath.Pi(), "phi", "rad"], "MC_AllEvent_Wdecay2_phi")
    tool.DrawOneBasic(h1_Wdecay2_AllEvent_eta,'3L1HadTau', ["#eta", 15, -4.5, 4.5, "eta", ""], "MC_AllEvent_eta_decay2_eta")
    tool.DrawOneBasic(h1_Wdecay2_AllEvent_pt,'3L1HadTau', ["p_{T}", 75, 0., 400., "pt", "GeV"], "MC_AllEvent_pt_decay2_pt")

    tool.DrawOneBasic(h1_MET_3L1HadTau, '3L1HadTau', ["E_{T}^{miss}",40, 0, 500., "MET", "GeV"], "MC_MET")
    tool.DrawOneBasic(h1_t_MT_3L1HadTau, '3L1HadTau', ["M_{T}", 20, 0., 400., "MT", "GeV"], "MC_t_MT")
    tool.DrawOneBasic(h1_W_from_t_MT_3L1HadTau, '3L1HadTau', ["M_{T}(W from t)", 20, 0., 400., "MT", "GeV"], "MC_W_from_t_MT")
    tool.DrawOneBasic(h1_mlb_3L1HadTau,'3L1HadTau', ["m_{lb} l from t", 25, 0., 250., "m", "GeV"], "MC_mlb")
    tool.DrawOneBasic(h1_mlb_l_fromHdec1_3L1HadTau,'3L1HadTau', ["m_{lb} l from H child1", 20, 0., 400., "m", "GeV"], "MC_mlb_lep_from_Hdecay_1") 
    tool.DrawOneBasic(h1_mlb_l_fromHdec2_3L1HadTau,'3L1HadTau', ["m_{lb} l from H child2", 20, 0., 400., "m", "GeV"], "MC_mlb_lep_from_Hdecay_2")

    # 3L signal region
    tool.DrawOneBasic(h1_DeltaEta_bl_from_t_3L, '3L', ["#Delta#eta(bl) with l from t", 20, -4.5, 4.5, "deltaEta_lb_from_t", " "], "MC_b_from_and_Wdecay1_from_t_Delta_eta")
    tool.DrawOneBasic(h1_DeltaPhi_bl_from_t_3L, '3L', ["#Delta#phi(bl) with l from t", 21, -TMath.Pi(), TMath.Pi(), "deltaPhi_lb_from_t", "rad"], "MC_b_from_and_Wdecay1_from_t_Delta_phi")
    tool.DrawOneBasic(h1_DeltaR_bl_from_t_3L, '3L', ["#DeltaR(bl) with l from t", 20, 0.0, 4.5, "deltaR_lb_from_t", " "], "MC_b_from_and_Wdecay1_from_t_Delta_R")
    tool.DrawOneBasic(h1_DeltaEta_Hdecay1and2_3L, '3L', ["#Delta#eta(H decay1, H decay2)",  20, -4.5, 4.5, "deltaEta_Hdecay1and2", " "], "MC_Hdecay_1_and_2_Delta_eta")
    tool.DrawOneBasic(h1_DeltaPhi_Hdecay1and2_3L, '3L', ["#Delta#phi(H decay1, H decay2)",  20, -TMath.Pi(), TMath.Pi(), "deltaPhi_Hdecay1and2", " "], "MC_Hdecay_1_and_2_Delta_phi")
    tool.DrawOneBasic(h1_DeltaR_Hdecay1and2_3L, '3L', ["#DeltaR(H decay1, H decay2)",  20, 0., 6., "deltaR_Hdecay1and2", " "], "MC_Hdecay_1_and_2_Delta_R")
    tool.DrawOneBasic(h1_DeltaEta_W1_from_Hdecay1and2_3L, '3L', ["#Delta#eta(decay1s from decays 1 and 2 from H)",  20, -4.5, 4.5, "deltaEta_W1_from_Hdecay1and2", " "], "MC_W1_Hdecays_Delta_eta")
    tool.DrawOneBasic(h1_DeltaPhi_W1_from_Hdecay1and2_3L, '3L', ["#Delta#phi(decay1s from decays 1 and 2 from H)",  20, -TMath.Pi(), TMath.Pi(), "deltaPhi_W1_from_Hdecay1and2", " "], "MC_W1_Hdecays_Delta_phi")
    tool.DrawOneBasic(h1_DeltaR_W1_from_Hdecay1and2_3L, '3L', ["#DeltaR(decay1s from decays 1 and 2 from H)",  20, 0., 6., "deltaR_W1_from_Hdecay1and2", " "], "MC_W1_Hdecays_Delta_R")

    tool.DrawOneBasic(h1_MET_3L, '3L', ["E_{T}^{miss}",40, 0, 500., "MET", "GeV"], "MC_MET")
    tool.DrawOneBasic(h1_t_MT_3L, '3L', ["M_{T}(top)", 20, 0., 400., "MT", "GeV"], "MC_t_MT")
    tool.DrawOneBasic(h1_W_from_t_MT_3L, '3L', ["M_{T}(W from t)", 20, 0., 400., "MT", "GeV"], "MC_W_from_t_MT")
    tool.DrawOneBasic(h1_mlb_3L,'3L', ["m_{lb} l from t", 25, 0., 250., "m", "GeV"], "MC_mlb")
    tool.DrawOneBasic(h1_mlb_l_fromHdec1_3L,'3L', ["m_{lb} l from H child1", 20, 0., 400., "m", "GeV"], "MC_mlb_lep_from_Hdecay_1")
    tool.DrawOneBasic(h1_mlb_l_fromHdec2_3L,'3L', ["m_{lb} l from H child2", 20, 0., 400., "m", "GeV"], "MC_mlb_lep_from_Hdecay_2")

    # Histos - 2D
    tool.Draw2DHisto(h2_Wdecay_from_tau1_pdgidVSeta, '3L1HadTau','SCAT',['W_decay1_from_Tau1_EtaVsId', 'eta', 'pdgId', 'W decay1 from Tau1'])
    tool.Draw2DHisto(h2_Wdecay_from_tau1_pdgidVSpt, '3L1HadTau','SCAT',['W_decay1_from_Tau1_PtVsId', 'p_{T} [GeV]', 'pdgId', 'W decay1 from Tau1'])
    tool.Draw2DHisto(h2_3L1HadTau_secondb_beforeFSR_pt_vs_eta, '3L1HadTau','COLZ',['secondb_beforeFSR_pt_vs_eta', 'p_{T}(second b) [GeV]', '#eta(second b)', '#eta(second b)'])
    tool.Draw2DHisto(h2_3L_secondb_beforeFSR_pt_vs_eta, '3L','COLZ',['secondb_beforeFSR_pt_vs_eta', 'p_{T}(second b) [GeV]', '#eta(second b)', '#eta(second b)'])   
    tool.Draw2DHisto(h2_3L1HadTau_b_from_t_pt_vs_eta, '3L1HadTau','COLZ',['b_from_t_pt_vs_eta', 'p_{T}(b) [GeV]', '#eta(b)', '#eta(b from t)'])
    tool.Draw2DHisto(h2_3L_b_from_t_pt_vs_eta, '3L','COLZ',['b_from_t_pt_vs_eta', 'p_{T}(b) [GeV]', '#eta(b)', '#eta(b from t)'])

    #for 2D histos - explore other plot types
    tool.Draw2DHisto(h2_3L1HadTau_b_from_t_pt_vs_eta, '3L1HadTau','SCAT',['b_from_t_pt_vs_eta_TEST_SCAT', 'p_{T}(b) [GeV]', '#eta(b)', '#eta(b from t)'])
    tool.Draw2DHisto(h2_3L1HadTau_b_from_t_pt_vs_eta, '3L1HadTau','CONT1',['b_from_t_pt_vs_eta_TEST_CONT1', 'p_{T}(b) [GeV]', '#eta(b)', '#eta(b from t)'])
    tool.Draw2DHisto(h2_3L1HadTau_b_from_t_pt_vs_eta, '3L1HadTau','ARR',['b_from_t_pt_vs_eta_TEST_ARR', 'p_{T}(b) [GeV]', '#eta(b)', '#eta(b from t)'])
    tool.Draw2DHisto(h2_3L1HadTau_b_from_t_pt_vs_eta, '3L1HadTau','ARR COLZ',['b_from_t_pt_vs_eta_TEST_ArrColz', 'p_{T}(b) [GeV]', '#eta(b)', '#eta(b from t)'])
    tool.Draw2DHisto(h2_3L1HadTau_b_from_t_pt_vs_eta, '3L1HadTau','COLZ1',['b_from_t_pt_vs_eta_TEST_COLZ1', 'p_{T}(b) [GeV]', '#eta(b)', '#eta(b from t)'])

    # Ratios - Pie Chart
    style_name.SetOptTitle(1)

    tool.DrawPie('Ratio_DeltaRMinTopTopBar','3L',[TopTopbar_DeltaRMin['3L'],j2['3L']-TopTopbar_DeltaRMin['3L']])
    tool.DrawPie('Ratio_DeltaRMinTop','3L',[Top_DeltaRMin['3L'],Number_of_top['3L']-Top_DeltaRMin['3L']])
    tool.DrawPie('Ratio_DeltaRMinLepTop','3L',[Top_DeltaRMinLep['3L'],Number_of_top['3L']-Top_DeltaRMinLep['3L']])
    tool.DrawPie('Ratio_DeltaRMinTopbar','3L',[Topbar_DeltaRMin['3L'],Number_of_topbar['3L']-Topbar_DeltaRMin['3L']])
    tool.DrawPie('Ratio_DeltaRMinLepTopbar','3L',[Topbar_DeltaRMinLep['3L'],Number_of_topbar['3L']-Topbar_DeltaRMinLep['3L']])

    try:
        tool.DrawPie('Ratio_DeltaRMinTopTopBar','3L1HadTau',[TopTopbar_DeltaRMin['3L1HadTau'],j2['3L1HadTau']-TopTopbar_DeltaRMin['3L1HadTau']])
        tool.DrawPie('Ratio_DeltaRMinTop','3L1HadTau',[Top_DeltaRMin['3L1HadTau'],Number_of_top['3L1HadTau']-Top_DeltaRMin['3L1HadTau']])
        tool.DrawPie('Ratio_DeltaRMinLepTop','3L1HadTau',[Top_DeltaRMinLep['3L1HadTau'],Number_of_top['3L1HadTau']-Top_DeltaRMinLep['3L1HadTau']])
        tool.DrawPie('Ratio_DeltaRMinTopbar','3L1HadTau',[Topbar_DeltaRMin['3L1HadTau'],Number_of_topbar['3L1HadTau']-Topbar_DeltaRMin['3L1HadTau']])
        tool.DrawPie('Ratio_DeltaRMinLepTopbar','3L1HadTau',[Topbar_DeltaRMinLep['3L1HadTau'],Number_of_topbar['3L1HadTau']-Topbar_DeltaRMinLep['3L1HadTau']])

        tool.DrawPie('Ratio_DeltaPhiMinTopTopbar','3L',[TopTopbar_DeltaPhiMin['3L'],j2['3L']-TopTopbar_DeltaPhiMin['3L']])
        tool.DrawPie('Ratio_DeltaPhiMinTop','3L',[Top_DeltaPhiMin['3L'],Number_of_top['3L']-Top_DeltaPhiMin['3L']])
        tool.DrawPie('Ratio_DeltaPhiMinLepTop','3L',[Top_DeltaPhiMinLep['3L'],Number_of_top['3L']-Top_DeltaPhiMinLep['3L']])
        tool.DrawPie('Ratio_DeltaPhiMinTopbar','3L',[Topbar_DeltaPhiMin['3L'],Number_of_topbar['3L']-Topbar_DeltaPhiMin['3L']])
        tool.DrawPie('Ratio_DeltaPhiMinLepTopbar','3L',[Topbar_DeltaPhiMinLep['3L'],Number_of_topbar['3L']-Topbar_DeltaPhiMinLep['3L']])

        tool.DrawPie('Ratio_DeltaEtaMinTopTopbar','3L',[TopTopbar_DeltaEtaMin['3L'],j2['3L']-TopTopbar_DeltaEtaMin['3L']])
        tool.DrawPie('Ratio_DeltaEtaMinTop','3L',[Top_DeltaEtaMin['3L'],Number_of_top['3L']-Top_DeltaEtaMin['3L']])
        tool.DrawPie('Ratio_DeltaEtaMinLepTop','3L',[Top_DeltaEtaMinLep['3L'],Number_of_top['3L']-Top_DeltaEtaMinLep['3L']])
        tool.DrawPie('Ratio_DeltaEtaMinTopbar','3L',[Topbar_DeltaEtaMin['3L'],Number_of_topbar['3L']-Topbar_DeltaEtaMin['3L']])
        tool.DrawPie('Ratio_DeltaEtaMinLepTopbar','3L',[Topbar_DeltaEtaMinLep['3L'],Number_of_topbar['3L']-Topbar_DeltaEtaMinLep['3L']])

        tool.DrawPie('Ratio_DeltaPhiMinTopTopbar','3L1HadTau',[TopTopbar_DeltaPhiMin['3L1HadTau'],j2['3L1HadTau']-TopTopbar_DeltaPhiMin['3L1HadTau']])
        tool.DrawPie('Ratio_DeltaPhiMinTop','3L1HadTau',[Top_DeltaPhiMin['3L1HadTau'],Number_of_top['3L1HadTau']-Top_DeltaPhiMin['3L1HadTau']])
        tool.DrawPie('Ratio_DeltaPhiMinLepTop','3L1HadTau',[Top_DeltaPhiMinLep['3L1HadTau'],Number_of_top['3L1HadTau']-Top_DeltaPhiMinLep['3L1HadTau']])
        tool.DrawPie('Ratio_DeltaPhiMinTopbar','3L1HadTau',[Topbar_DeltaPhiMin['3L1HadTau'],Number_of_topbar['3L1HadTau']-Topbar_DeltaPhiMin['3L1HadTau']])
        tool.DrawPie('Ratio_DeltaPhiMinLepTopbar','3L1HadTau',[Topbar_DeltaPhiMinLep['3L1HadTau'],Number_of_topbar['3L1HadTau']-Topbar_DeltaPhiMinLep['3L1HadTau']])

        tool.DrawPie('Ratio_PtMaxTopTopbar','3L',[TopTopbar_PtMax['3L'],j2['3L']-TopTopbar_PtMax['3L']])
        tool.DrawPie('Ratio_PtMaxTop','3L',[Top_PtMax['3L'],Number_of_top['3L']-Top_PtMax['3L']])
        tool.DrawPie('Ratio_PtMaxTopbar','3L',[Topbar_PtMax['3L'],Number_of_topbar['3L']-Topbar_PtMax['3L']])

        tool.DrawPie('Ratio_PtMaxTopTopbar','3L1HadTau',[TopTopbar_PtMax['3L1HadTau'],j2['3L1HadTau']-TopTopbar_PtMax['3L1HadTau']])
        tool.DrawPie('Ratio_PtMaxTop','3L1HadTau',[Top_PtMax['3L1HadTau'],Number_of_top['3L1HadTau']-Top_PtMax['3L1HadTau']])
        tool.DrawPie('Ratio_PtMaxTopbar','3L1HadTau',[Topbar_PtMax['3L1HadTau'],Number_of_topbar['3L1HadTau']-Topbar_PtMax['3L1HadTau']])
    except:
        msg.printWarning("problem with ratios")

    end_drawAll = time.time()
    msg.printInfo("Drawing time: " +str((end_drawAll - start_drawAll)/60) + " min")
    # End drawing
    
    msg.printInfo("--- %s minutes ---" % ((time.time() - start_time)/60))

# =================================================================================
#  __main__
# =================================================================================
if __name__ == '__main__':
  main(sys.argv[1:])

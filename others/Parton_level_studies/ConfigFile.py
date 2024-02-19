import os, commands
from ROOT import TMath
from MsgHelper import msgServer

# =====================================================================
#  configFile
# =====================================================================
class configFile:
    def __init__(self, options):
        self.msg = msgServer('ConfigFile', options.debugLevel)

        # input file(s), directory(ies) or dataset(s)
        self.rootFile = []
        self.input = options.myinput.split(',')
        for idx,i in enumerate(self.input):
            if os.path.exists(i):
                if os.path.isfile(i):
                    self.rootFile += [i]
                    if len(self.input) == 1: self.msg.printInfo("- Input ROOT file: " + self.rootFile[idx])
                    else: self.msg.printInfo("- [%02d/%02d] Input ROOT file: %s" % (idx+1, len(self.input), self.rootFile[idx]))

                elif os.path.isdir(i):
                    self.msg.printInfo("Input directory: " + i)
                    nfiles = 0
                    for f in os.listdir(i):
                        if f.startswith('.'): continue
                        if os.path.isdir(i+f): continue
                        nfiles += 1

                    if nfiles == 0:
                        print self.msg.printWarning("Files not found in the input directory (%s)! :(" % i)

                    idx2 = 0
                    for f in os.listdir(i):
                        if f.startswith('.'): continue
                        if os.path.isdir(i+f): continue
                        if options.maxfiles > 0 and idx2 == options.maxfiles: break
                        if not i.endswith('/'): i = i + '/'
                        # print i+f
                        self.rootFile += [ i+f ]
                        self.msg.printInfo("- [%02d/%02d] Input ROOT file: %s" % (idx2+1, nfiles, self.rootFile[idx2]))
                        idx2 += 1
            else:
                if i.startswith('user.'):
                    self.msg.printInfo("Input sample name: " + i)
                    self.rootFile += self.get_rucio_location(i, 'IFIC-LCG2_LOCALGROUPDISK', options.maxfiles)
                    if len(self.rootFile) == 0: self.rootFile += self.get_rucio_location(i, 'IFIC-LCG2_SCRATCHDISK', options.maxfiles)
                    if len(self.rootFile) == 0: exit()

        # summary input file(s), directory(ies) or dataset(s)          
        #for idx,i in enumerate(self.rootFile):
        #    self.msg.printInfo("[%02d/%02d] Input ROOT file: %s" % (idx+1, len(self.rootFile), i))

        Configuration = self.OpenYaml(options.myconfig)
        Cuts = Configuration['selection_options']
        Cuts['bjet_pt_min'] = float(Cuts['bjet_pt_min'])*1000
        Cuts['lep_pt_min'] = float(Cuts['lep_pt_min'])*1000
        Cuts['tau_pt_min'] = float(Cuts['tau_pt_min'])*1000
        self.cuts = Cuts

        self.TreeName = "truth"
        self.save_directory = "./parton_truth_plots"

        self.energyUnits = 'MeV'
        self.phiUnits = 'rad'

        self.HistogramDetails_common = {"MC_H_decay" :["Higgs decays", 50, 0.0, 50.0, "MC_H_decay", ""],
                                        "MC_H_decay_weights" :["Higgs decays (with weights)", 50, 0.0, 50.0, "MC_H_decay_weights", ""],
                                        "weight_mc" :["MC weight", 50, -0.3, 0.3, "weight", ""]
                                        }
        
        self.HistogramDetails_commonForSRs = {"weight_mc" :["MC weight", 50, -0.3, 0.3, "weight", ""],
                                            "MC_Higgs_m" :["m (Higgs)", 20, 0.,  200000, "Higgs", self.energyUnits],
                                            "MC_Higgs_pt" :["p_{T} (Higgs)", 30, 0., 300000., "Higgs", self.energyUnits],
                                            "MC_Higgs_eta" :["#eta (Higgs)", 20, -4.5, 4.5,  "Higgs",""],
                                            "MC_Higgs_phi" :["#phi (Higgs)", 21, -TMath.Pi(), TMath.Pi(), "Higgs", self.phiUnits],
        
											
											# DECAY N FROM H #
											
                                            "MC_Higgs_decay1_m" :["m(H decay1)", 20, 0., 100000., "H_decay1", self.energyUnits],
                                            "MC_Higgs_decay1_pt":["p_{T}(H decay1)", 30, 0., 300000., "H_decay1", self.energyUnits],
                                            "MC_Higgs_decay1_eta" :["#eta(H decay1)", 20, -4.5, 4.5, "H_decay1", ""],
                                            "MC_Higgs_decay1_phi" :["#phi(H decay1)", 21, -TMath.Pi(), TMath.Pi(), "H_decay1", self.phiUnits],
                                            "MC_Higgs_decay1_pdgId" :["pdgId(H decay1)", 60, -30., 30., "H_decay1", ""],
                                            
                                            "MC_Higgs_tau_decay1_isHadronic" :["pdgId (Tau 1 from H)", 60, -30., 30., "H_decay1_Tau", ""],
                                            "MC_Higgs_tau_decay1_m" :["m(Tau 1 from H)", 20, 0., 100000., "H_decay1_Tau", self.energyUnits],
                                            "MC_Higgs_tau_decay1_pt":["p_{T}(Tau 1 from H)", 30, 0., 300000., "H_decay1_Tau", self.energyUnits],
                                            "MC_Higgs_tau_decay1_eta" :["#eta(Tau 1 from H)", 20, -4.5, 4.5, "H_decay1_Tau", ""],
                                            "MC_Higgs_tau_decay1_phi" :["#phi(Tau 1 from H)", 21, -TMath.Pi(), TMath.Pi(), "H_decay1_Tau", self.phiUnits],
	
                                            
                                            "MC_Higgs_decay2_m" :["m(H decay2)", 20, 0., 100000., "H_decay2", self.energyUnits],
                                            "MC_Higgs_decay2_pt":["p_{T}(H decay2)", 30, 0., 300000., "H_decay2", self.energyUnits],
                                            "MC_Higgs_decay2_eta" :["#eta(H decay2)", 20, -4.5, 4.5, "H_decay2", ""],
                                            "MC_Higgs_decay2_phi" :["#phi(H decay2)", 21, -TMath.Pi(), TMath.Pi(), "H_decay2", self.phiUnits],
                                            "MC_Higgs_decay2_pdgId" :["pdgId(H decay2)", 60, -30., 30., "H_decay2", ""],
                                            
                                            "MC_Higgs_tau_decay2_isHadronic" :["pdgId (Tau 2 from H)", 60, -30., 30., "H_decay2_Tau", ""],
                                            "MC_Higgs_tau_decay2_m" :["m(Tau 2 from H)", 20, 0., 100000., "H_decay2_Tau", self.energyUnits],
                                            "MC_Higgs_tau_decay2_pt":["p_{T}(Tau 2 from H)", 30, 0., 300000., "H_decay2_Tau", self.energyUnits],
                                            "MC_Higgs_tau_decay2_eta" :["#eta(Tau 2 from H)", 20, -4.5, 4.5, "H_decay2_Tau", ""],
                                            "MC_Higgs_tau_decay2_phi" :["#phi(Tau 2 from H)", 21, -TMath.Pi(), TMath.Pi(), "H_decay2_Tau", self.phiUnits],
                                            
                                            
                                            # DECAY N FROM DECAY N FROM H #
                                            
                                            "MC_Higgs_decay1_from_decay1_m" : ["m(H decay1 from decay1)", 20, 0., 100000., "H_decay1_from_decay1", self.energyUnits],
                                            "MC_Higgs_decay1_from_decay1_pt":["p_{T}(H decay1 from decay1)", 30, 0., 300000., "H_decay1_from_decay1", self.energyUnits],
                                            "MC_Higgs_decay1_from_decay1_eta" :["#eta(H decay1 from decay1)", 20, -4.5, 4.5, "H_decay1_from_decay1", ""],
                                            "MC_Higgs_decay1_from_decay1_phi" :["#phi(H decay1 from decay1)", 21, -TMath.Pi(), TMath.Pi(), "H_decay1_from_decay1", self.phiUnits],
                                            "MC_Higgs_decay1_from_decay1_pdgId" :["pdgId(H decay1 from decay1)", 60, -30., 30., "H_decay1_from_decay1", ""],
											
                                            "MC_Higgs_tau_decay1_from_decay1_isHadronic" :["pdgId (Tau1 from decay1 H)", 60, -30., 30., "H_from_decay1_decay1_Tau", ""],
                                            "MC_Higgs_tau_decay1_from_decay1_m" :["m(Tau1 from decay1 H)", 20, 0., 100000., "H_from_decay1_decay1_Tau", self.energyUnits],
                                            "MC_Higgs_tau_decay1_from_decay1_pt":["p_{T}(Tau1 from decay1 H)", 30, 0., 300000., "H_from_decay1_decay1_Tau", self.energyUnits],
                                            "MC_Higgs_tau_decay1_from_decay1_eta" :["#eta(Tau1 from decay1 H)", 20, -4.5, 4.5, "H_from_decay1_decay1_Tau", ""],
                                            "MC_Higgs_tau_decay1_from_decay1_phi" :["#phi(Tau1 from decay1 H)", 21, -TMath.Pi(), TMath.Pi(), "H_from_decay1_decay1_Tau", self.phiUnits],
                                            
                                            "MC_Higgs_decay2_from_decay1_m" : ["m(H decay2 from decay1)", 20, 0., 100000., "H_decay2_from_decay1", self.energyUnits],
                                            "MC_Higgs_decay2_from_decay1_pt":["p_{T}(H decay2 from decay1)", 30, 0., 300000., "H_decay2_from_decay1", self.energyUnits],
                                            "MC_Higgs_decay2_from_decay1_eta" :["#eta(H decay2 from decay1)", 20, -4.5, 4.5, "H_decay2_from_decay1", ""],
                                            "MC_Higgs_decay2_from_decay1_phi" :["#phi(H decay2 from decay1)", 21, -TMath.Pi(), TMath.Pi(), "H_decay2_from_decay1", self.phiUnits],
                                            "MC_Higgs_decay2_from_decay1_pdgId" :["pdgId(H decay2 from decay1)", 60, -30., 30., "H_decay2_from_decay1", ""],
                                            
                                            "MC_Higgs_tau_decay2_from_decay1_isHadronic" :["pdgId (Tau2 from decay1 H)", 60, -30., 30., "H_from_decay2_decay1_Tau", ""],
                                            "MC_Higgs_tau_decay2_from_decay1_m" :["m(Tau2 from decay1 H)", 20, 0., 100000., "H_from_decay2_decay1_Tau", self.energyUnits],
                                            "MC_Higgs_tau_decay2_from_decay1_pt":["p_{T}(Tau2 from decay1 H)", 30, 0., 300000., "H_from_decay2_decay1_Tau", self.energyUnits],
                                            "MC_Higgs_tau_decay2_from_decay1_eta" :["#eta(Tau2 from decay1 H)", 20, -4.5, 4.5, "H_from_decay2_decay1_Tau", ""],
                                            "MC_Higgs_tau_decay2_from_decay1_phi" :["#phi(Tau2 from decay1 H)", 21, -TMath.Pi(), TMath.Pi(), "H_from_decay2_decay1_Tau", self.phiUnits],
                                            
                                            "MC_Higgs_decay1_from_decay2_m" : ["m(H decay1 from decay2)", 20, 0., 100000., "H_decay1_from_decay2", self.energyUnits],
                                            "MC_Higgs_decay1_from_decay2_pt":["p_{T}(H decay1 from decay2)", 30, 0., 300000., "H_decay1_from_decay2", self.energyUnits],
                                            "MC_Higgs_decay1_from_decay2_eta" :["#eta(H decay1 from decay2)", 20, -4.5, 4.5, "H_decay1_from_decay2", ""],
                                            "MC_Higgs_decay1_from_decay2_phi" :["#phi(H decay1 from decay2)", 21, -TMath.Pi(), TMath.Pi(), "H_decay1_from_decay2", self.phiUnits],
                                            "MC_Higgs_decay1_from_decay2_pdgId" :["pdgId(H decay1 from decay2)", 60, -30., 30., "H_decay1_from_decay2", ""],
											
                                            "MC_Higgs_tau_decay1_from_decay2_isHadronic" :["pdgId (Tau1 from decay1 H)", 60, -30., 30., "H_from_decay1_decay2_Tau", ""],
                                            "MC_Higgs_tau_decay1_from_decay2_m" :["m(Tau1from decay2 H)", 20, 0., 100000., "H_from_decay1_decay2_Tau", self.energyUnits],
                                            "MC_Higgs_tau_decay1_from_decay2_pt":["p_{T}(Tau1 from decay2 H)", 30, 0., 300000., "H_from_decay1_decay2_Tau", self.energyUnits],
                                            "MC_Higgs_tau_decay1_from_decay2_eta" :["#eta(Tau1 from decay2 H)", 20, -4.5, 4.5, "H_from_decay1_decay2_Tau", ""],
                                            "MC_Higgs_tau_decay1_from_decay2_phi" :["#phi(Tau1 from decay2 H)", 21, -TMath.Pi(), TMath.Pi(), "H_from_decay1_decay2_Tau", self.phiUnits],
                                            
                                            "MC_Higgs_decay2_from_decay2_m" : ["m(H decay2 from decay2)", 20, 0., 100000., "H_decay2_from_decay2", self.energyUnits],
                                            "MC_Higgs_decay2_from_decay2_pt":["p_{T}(H decay2 from decay2)", 30, 0., 300000., "H_decay2_from_decay2", self.energyUnits],
                                            "MC_Higgs_decay2_from_decay2_eta" :["#eta(H decay2 from decay2)", 20, -4.5, 4.5, "H_decay2_from_decay2", ""],
                                            "MC_Higgs_decay2_from_decay2_phi" :["#phi(H decay2 from decay2)", 21, -TMath.Pi(), TMath.Pi(), "H_decay2_from_decay2", self.phiUnits],
                                            "MC_Higgs_decay2_from_decay2_pdgId" :["pdgId(H decay2 from decay2)", 60, -30., 30., "H_decay2_from_decay2", ""],
                                            
                                            "MC_Higgs_tau_decay2_from_decay2_isHadronic" :["pdgId (Tau2 from decay2 H)", 60, -30., 30., "H_from_decay2_decay2_Tau", ""],
                                            "MC_Higgs_tau_decay2_from_decay2_m" :["m(Tau2from decay2 H)", 20, 0., 100000., "H_from_decay2_decay2_Tau", self.energyUnits],
                                            "MC_Higgs_tau_decay2_from_decay2_pt":["p_{T}(Tau2 from decay2 H)", 30, 0., 300000., "H_from_decay2_decay2_Tau", self.energyUnits],
                                            "MC_Higgs_tau_decay2_from_decay2_eta" :["#eta(Tau2 from decay2 H)", 20, -4.5, 4.5, "H_from_decay2_decay2_Tau", ""],
                                            "MC_Higgs_tau_decay2_from_decay2_phi" :["#phi(Tau2 from decay2 H)", 21, -TMath.Pi(), TMath.Pi(), "H_from_decay2_decay2_Tau", self.phiUnits],
                                            
                                            # TOP SYSTEM
                                            "MC_Wdecay1_from_t_m" : ["m(W decay1 from t)", 20, -200., 90000., "Wdecay1_from_t", self.energyUnits],
                                            "MC_Wdecay1_from_t_pt": ["p_{T}(W decay1 from t)", 20, 0., 200000., "Wdecay1_from_t", self.energyUnits],
                                            "MC_Wdecay1_from_t_eta":["#eta(W decay1 from t)", 20, -4.5, 4.5, "Wdecay1_from_t", ""],
                                            "MC_Wdecay1_from_t_phi":["#phi(W decay1 from t)", 21, -TMath.Pi(), TMath.Pi(), "Wdecay1_from_t", self.phiUnits],
                                            "MC_Wdecay1_from_t_pdgId":["pdgId(W decay1 from t)", 60, -30., 30., "Wdecay1_from_t", " "],
                                            
                                            "MC_Wdecay2_from_t_m" : ["m(W decay2 from t)", 20, -200., 90000., "Wdecay2_from_t", self.energyUnits],
                                            "MC_Wdecay2_from_t_pt": ["p_{T}(W decay2 from t)", 20, 0., 200000., "Wdecay2_from_t", self.energyUnits],
                                            "MC_Wdecay2_from_t_eta":["#eta(W decay2 from t)", 20, -4.5, 4.5, "Wdecay2_from_t", ""],
                                            "MC_Wdecay2_from_t_phi":["#phi(W decay2 from t)", 21, -TMath.Pi(), TMath.Pi(), "Wdecay1_from_t", self.phiUnits],
                                            "MC_Wdecay2_from_t_pdgId":["pdgId(W decay2 from t)", 60, -30., 30., "Wdecay2_from_t", " "],
                                        
                                        
                                            "MC_tau_from_W_from_t_m" : ["m(tau from t)", 20, -100., 100., "tau_from_W__from_t", self.energyUnits],
                                            "MC_tau_from_W_from_t_pt": ["p_{T}(tau from t)", 20, 0., 200000., "tau_from_W__from_t", self.energyUnits],
                                            "MC_tau_from_W_from_t_eta":["#eta(tau from t)", 20, -4.5, 4.5, "tau_from_W__from_t", ""],
                                            "MC_tau_from_W_from_t_phi":["#phi(tau from t)", 21, -TMath.Pi(), TMath.Pi(), "tau_from_W__from_t", self.phiUnits],
                                            "MC_tau_from_W_from_t_isHadronic":["pdgId(tau from t)", 60, -30., 30., "tau_from_W__from_t", ""],
                                    
                                            "MC_b_from_t_m" :["m(b)", 20, 4400., 5000., "b", self.energyUnits],
                                            "MC_b_from_t_pt":["p_{T}(b)", 30, 0., 300000., "b", self.energyUnits],
                                            "MC_b_from_t_eta" :["#eta(b)", 20, -4.5, 4.5, "b", ""],
                                            "MC_b_from_t_phi" :["#phi(b)", 21, -TMath.Pi(), TMath.Pi(), "b", self.phiUnits],
                                            
                                            "MC_secondb_beforeFSR_m" :["m(second b) before FSR", 20, 4600., 4900., "second b quark before FSR", self.energyUnits],
                                            "MC_secondb_beforeFSR_pt":["p_{T}(second b) before FSR", 30, 0., 300000., "second b quar before FSRk", self.energyUnits],
                                            "MC_secondb_beforeFSR_eta" :["#eta(second b) before FSR", 20, -4.5, 4.5, "second b quark before FSR", ""],
                                            "MC_secondb_beforeFSR_phi" :["#phi(second b) before FSR", 21, -TMath.Pi(), TMath.Pi(), "second b quark before FSR", self.phiUnits],
                                            "MC_secondb_beforeFSR_pdgId" :["pdgId(second b) before FSR", 60, -30., 30., "second b quark", ""],
                                            
                                            "MC_secondb_afterFSR_m" :["m(second b) after FSR", 20, 4600., 4900., "second b quark after FSR", self.energyUnits],
                                            "MC_secondb_afterFSR_pt":["p_{T}(second b) after FSR", 30, 0., 300000., "second b quark after FSR", self.energyUnits],
                                            "MC_secondb_afterFSR_eta" :["#eta(second b) after FSR", 20, -4.5, 4.5, "second b quark after FSR", ""],
                                            "MC_secondb_afterFSR_phi" :["#phi(second b) after FSR", 21, -TMath.Pi(), TMath.Pi(), "second b quark after FSR", self.phiUnits],
                                            "MC_secondb_afterFSR_pdgId" :["pdgId(second b) after FSR", 60, -30., 30., "second b quark after FSR", ""],

                                            "MC_spectatorquark_pdgId" :["pdgId(spectator quark)", 60, -30., 30., "spectator quark", ""],
                                            "MC_spectatorquark_status" :["status(spectator quark)", 100, 0., 100., "spectator quark", ""],  
                                            "MC_spectatorquark_beforeFSR_m" :["m(spectator quark before FSR)", 20, 4600., 4900., "spectator quark before FSR", self.energyUnits],
                                            "MC_spectatorquark_beforeFSR_pt":["p_{T}(spectator quark before FSR)", 30, 0., 300000., "spectator quark before FSR", self.energyUnits],
                                            "MC_spectatorquark_beforeFSR_eta" :["#eta(spectator quark before FSR)", 20, -4.5, 4.5, "spectator quark before FSR", ""],
                                            "MC_spectatorquark_beforeFSR_phi" :["#phi(spectator quark before FSR)", 21, -TMath.Pi(), TMath.Pi(), "spectator quark before FSR", self.phiUnits],
                                            
                                            "MC_spectatorquark_afterFSR_m" :["m(spectator quark after FSR)", 20, 4600., 4900., "spectator quark after FSR", self.energyUnits],
                                            "MC_spectatorquark_afterFSR_pt":["p_{T}(spectator quark after FSR)", 30, 0., 300000., "spectator quark after FSR", self.energyUnits],
                                            "MC_spectatorquark_afterFSR_eta" :["#eta(spectator quark after FSR)", 20, -4.5, 4.5, "spectator quark after FSR", ""],
                                            "MC_spectatorquark_afterFSR_phi" :["#phi(spectator quark after FSR)", 21, -TMath.Pi(), TMath.Pi(), "spectator quark after FSR", self.phiUnits],
                                    }

		# The specific histos are inherited from the old variables, this makes no sense now
        self.HistogramDetails_specific = {'3L1HadTau' : {#"MC_W_decay2_from_Tau1_m" : ["m(W decay2 from Tau1)", 20, -70., 70., "W_decay2_from_Tau1", self.energyUnits],
                                                         #"MC_W_decay2_from_Tau1_pt": ["p_{T}(W decay2 from Tau1)",20, 0., 80000., "W_decay2_from_Tau1", self.energyUnits],
                                                         #"MC_W_decay2_from_Tau1_eta":["#eta(W decay2 from Tau1)", 20, -4.5, 4.5, "W_decay2_from_Tau1", ""],
                                                         #"MC_W_decay2_from_Tau1_phi":["#phi(W decay2 from Tau1)", 21, -TMath.Pi(), TMath.Pi(), "W_decay2_from_Tau1", self.phiUnits],
                                                         #"MC_W_decay2_from_Tau1_pdgId":["pdgId(W decay2 from Tau1)", 60, -30., 30., "W_decay2_from_Tau1", ""],
                                                         #
                                                         #"MC_W_decay2_from_Tau2_m" : ["m(W decay2 from Tau2)", 20, -70., 70., "W_decay2_from_Tau2", self.energyUnits],
                                                         #"MC_W_decay2_from_Tau2_pt": ["p_{T}(W decay2 from Tau2)",20, 0., 80000., "W_decay2_from_Tau2", self.energyUnits],
                                                         #"MC_W_decay2_from_Tau2_eta":["#eta(W decay2 from Tau2)", 20, -4.5, 4.5, "W_decay2_from_Tau2", ""],
                                                         #"MC_W_decay2_from_Tau2_phi":["#phi(W decay2 from Tau2)", 21, -TMath.Pi(), TMath.Pi(), "W_decay2_from_Tau2", self.phiUnits],
                                                         #"MC_W_decay2_from_Tau2_pdgId":["pdgId(W decay2 from Tau2)", 60, -30., 30., "W_decay2_from_Tau2", ""]
                                                     },
									
                                          '3L' : {#"MC_Z_Lepton1_from_Z1_m" :   ["m(Z lepton1 from Z1)", 40, 0., 1000., "Z_Lepton1_from_Z1", self.energyUnits],
                                                  #"MC_Z_Lepton1_from_Z1_phi" : ["#phi(Z lepton1 from Z1)", 21, -TMath.Pi(), TMath.Pi(), "Z_Lepton1_from_Z1", self.phiUnits],
                                                  #"MC_Z_Lepton1_from_Z1_eta" : ["#eta(Z lepton1 from Z1)", 40, -4.5, 4.5, "Z_Lepton1_from_Z1", ""],
                                                  #"MC_Z_Lepton1_from_Z1_pt" :  ["p_{T}(Z lepton1 from Z1)", 40, 0., 200000., "Z_Lepton1_from_Z1", self.energyUnits],
                                                  #
                                                  #"MC_Z_Lepton1_from_Z2_m" :   ["m(Z lepton1 from Z2)", 40, 0., 1000., "Z_Lepton1_from_Z2", self.energyUnits],
                                                  #"MC_Z_Lepton1_from_Z2_phi" : ["#phi(Z lepton1 from Z2)", 21, -TMath.Pi(), TMath.Pi(), "Z_Lepton1_from_Z2", self.phiUnits],
                                                  #"MC_Z_Lepton1_from_Z2_eta" : ["#eta(Z lepton1 from Z2)", 40, -4.5, 4.5, "Z_Lepton1_from_Z2", ""],
                                                  #"MC_Z_Lepton1_from_Z2_pt" :  ["p_{T}(Z lepton1 from Z2)", 40, 0., 200000., "Z_Lepton1_from_Z2", self.energyUnits],
                                                  #
                                                  #"MC_Z_Lepton2_from_Z1_m" : ["m(Z lepton2 from Z1)", 40, 0., 1000., "Z_Lepton1_from_Z1", self.energyUnits],
                                                  #"MC_Z_Lepton2_from_Z1_phi" : ["#phi(Z lepton2 from Z1)", 21, -TMath.Pi(), TMath.Pi(), "Z_Lepton2_from_Z1", self.phiUnits], 
                                                  #"MC_Z_Lepton2_from_Z1_eta" : ["#eta(Z lepton2 from Z1)", 40, -4.5, 4.5, "Z_Lepton2_from_Z1", ""],
                                                  #"MC_Z_Lepton2_from_Z1_pt" : ["p_{T}(Z lepton2 from Z1)", 40, 0., 200000., "Z_Lepton2_from_Z1", self.energyUnits],
                                                  #        
                                                  #"MC_Z_Lepton2_from_Z2_m" : ["m(Z lepton2 from Z2)", 40, 0., 1000., "Z_Lepton2_from_Z2", self.energyUnits],
                                                  #"MC_Z_Lepton2_from_Z2_phi" : ["#phi(Z lepton2 from Z2)", 21, -TMath.Pi(), TMath.Pi(), "Z_Lepton2_from_Z2", self.phiUnits],
                                                  #"MC_Z_Lepton2_from_Z2_eta" : ["#eta(Z lepton2 from Z2)", 40, -4.5, 4.5, "Z_Lepton2_from_Z2", ""],
                                                  #"MC_Z_Lepton2_from_Z2_pt" : ["p_{T}(Z lepton2 from Z2)", 40, 0., 200000., "Z_Lepton2_from_Z2", self.energyUnits],
												  #
                                                  #"MC_Z_Lepton1_from_Z1_pdgId" : ["pdgId(Z lepton1 from Z1)", 60, -30., 30., "Z_Lepton1_from_Z1", ""],
                                                  #"MC_Z_Lepton1_from_Z2_pdgId" : ["pdgId(Z lepton1 from Z2)", 60, -30., 30., "Z_Lepton1_from_Z2", ""],
                                                  #"MC_Z_Lepton2_from_Z1_pdgId" : ["pdgId(Z lepton2 from Z1)", 60, -30., 30., "Z_Lepton2_from_Z1", ""],
                                                  #"MC_Z_Lepton2_from_Z2_pdgId" : ["pdgId(Z lepton2 from Z2)", 60, -30., 30., "Z_Lepton2_from_Z2", ""]
                                              }
                                          }

        
        self.particles = ["Higgs_decay1",
                          "Higgs_decay2",
                          "Higgs_decay1_from_decay1",
                          "Higgs_decay2_from_decay1",
                          "Higgs_decay1_from_decay2",
                          "Higgs_decay2_from_decay2",
                          "Higgs_tau_decay1",
                          "Higgs_tau_decay2",
                          "Higgs_tau_decay1_from_decay1",
                          "Higgs_tau_decay2_from_decay1",
                          "Higgs_tau_decay1_from_decay2",
                          "Higgs_tau_decay2_from_decay2",
                          "Wdecay1_from_t",
                          "Wdecay2_from_t",
                          "tau_from_W_from_t" 
                          "secondb_beforeFSR",
                          "secondb_afterFSR"
						]

    # =====================================================================
    #  get_rucio_location()
    # =====================================================================
    def get_rucio_location(self, datasetName, SRE, maxfiles):
        rootfiles = []
        self.msg.printInfo("- Looking for %s in %s..." % (datasetName, SRE))
        cmd = 'rucio list-file-replicas %s --rse %s --pfns' % (datasetName, SRE)
        print cmd
        try:
            for idx,line in enumerate(commands.getoutput(cmd).splitlines()):
                # self.msg.printDebug(line)
                separator = "="
                if 'srmdav' in line: separator = '8443'
                elif 'xrootd' in line: separator = '1094'
                filepath = line.split('%s' % separator)[1]
                if os.path.isfile(filepath):
                    if maxfiles > 0 and idx == maxfiles: break
                    rootfiles += [ filepath ]
        except IndexError:
            print self.msg.printFatal("Dataset identifier not found (%s) in %s! :(" % (datasetName, SRE))
            return rootfiles

        if len(rootfiles) == 0:
            print self.msg.printFatal("Files not found for the input dataset (%s) in %s! :(" % (datasetName, SRE))
            return rootfiles

        for idx,rootfile in enumerate(rootfiles):
            self.msg.printInfo("- [%02d/%02d] Input ROOT file: %s" % (idx+1, len(rootfiles), rootfiles[idx]))

        return rootfiles

        
    # =====================================================================
    # OpenYaml
    # =====================================================================
    def OpenYaml(self, path, option = 'r'):
        import yaml
        with open(path, option) as ymlfile:
            cfg = yaml.load(ymlfile,Loader=yaml.BaseLoader)
        return cfg

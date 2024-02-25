import os,sys
import math
from array import array
import ROOT
from ROOT import TFile, TTree, TChain
from ROOT import TCanvas, TNtuple, TH1F, TH2F, TF1, TLegend, TFile, TTree, THStack, TGraph, TPad
from ROOT import TLatex, TAxis, TPaveText, TGaxis, TStyle
from ROOT import gROOT, gSystem, gStyle, gPad, gEnv, gRandom, gDirectory
from optparse import OptionParser
import matplotlib
matplotlib.use('Agg') # Bypass the need to install Tkinter GUI framework
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable



##########################################
#   Draw plots of S/B and Significance   #
#   according to the BDT cut             #
#                                        #
#   Counting based on histograms         #
#                                        ########################
#   Run the program frist to store the histograms. This may     #
#   take a bit but the rest of times it runs faster ;)          #
#################################################################

# Example: python Significance_vs_CutBDT.py --channel='OS' --target='tHq' --readHist
# if running for first time do: python Significance_vs_CutBDT.py --channel='OS' --target='tHq' 

# =========================================
#  main
# =========================================
def main(argv):
    parser = OptionParser()
    parser.add_option("-c", "--channel", dest="channel", help="The channel is either SS or OS (default: %default)")
    parser.add_option("-t", "--target", dest="bdt", help="The BDT to plot is either tHq or ttbar (default: %default)")
    #parser.add_option("-s", "--saveHisto", action='store_true', dest="saveHist", default=True, help="When the flag is present, the histograms are saved.")
    parser.add_option("-r", "--readHist", action='store_true', dest="readHist", default=False, help="When the flag is present, read the TH1Fs intead of computing them.")
    

    parser.set_defaults(channel='OS', bdt='ttbar')

    try:
        (options, args) = parser.parse_args()
    except:
        parser.print_help()
        exit()

    tree = "tHqLoop_nominal_Loose"
    channel = options.channel
    bdt = options.bdt
    lumi = 140

    #saveHisto = options.saveHist
    readHist = options.readHist

    #########################################################
    # Build the histograms for target and rest processes    #
    # Do this only once. Rest of times, use option readHist #
    #########################################################
    if not readHist: # Use if this is first time reading the BDT that you want to study
        if channel == "OS":
            #samples_dir = "/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/EBreview_v34_dilepOStau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV_BDT_tHq_ttbar/nominal_Loose"
            #samples_dir = "/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/EBreview_v34_dilepOStau_BDT_tHq_ttbar/nominal_Loose"  
            samples_dir = "/lustre/ific.uv.es/grid/atlas/t3/cescobar/tHq_analysis/13TeV/V34_2LOS1TAU_BDT_tHq_ttbar/nominal_Loose/"
        elif channel == "SS":
            #samples_dir = "/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/EBreview_v34_dilepSStau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV_BDT_tHq/nominal_Loose"
            samples_dir = "/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/NewSamples_2024_SS_bdt_tH/nominal_Loose"
        else:
            print("Error: Channel must be either OS or SS")
            exit()
        if not os.path.exists(samples_dir): print("WARNING: The directory '" + str(samples_dir) + "' does not exist")
        
        Chain_tHq = TChain("tHqLoop_nominal_Loose","") 
        Chain_ttbar = TChain("tHqLoop_nominal_Loose","")
        Chain_tWH = TChain("tHqLoop_nominal_Loose","")
        Chain_others = TChain("tHqLoop_nominal_Loose","") # Rest of processes

        
        # Dataset ID
        DSID_list ={
        'tHq':['346799', '508776'],
        'ttbar':['410470'],
        'Zjet':['700320', '700321', '700322', '700323', '700324', '700325', '700326', '700327', '700328', '700329', '700330', '700331', '700332', '700333', '700334'],
        'Wjet':['700338', '700339', '700340', '700341', '700342', '700343', '700344', '700345', '700346', '700347', '700348', '700349'],
        'Zjets_low':['364204','364205','364206','364207','364208','364209','364198','364199','364200','364201','364202','364203','364210','364211','364212','364213','364214','364215'],
        'Diboson':['364250','364253','364254','364255','364283','364284','364286','364287','364288','364289','364290','363355','363356','363357','363358','363359','363360','363489'],
        'Triboson':['364242','364243','364244','364245','364246','364247','364248','364249'],
        'tZq':['512059'],
        'ttW_Sherpa':['700168', '700205'],
        'ttZ':['410156','410157','410218','410219','410220','410276','410277','410278'],
        'tWZ':['412118'],
        'ttH':['346343','346344','346345'],
        't-channel':['410658','410659'],
        'tW':['410646','410647'],
        's-channel':['410644','410645'],
        #'tWH':['508776'],
        'ggH': ['342282'],
        'VBFH': ['342283'],
        'WH': ['342284'],
        'ZH': ['342285'],
        'ttt': ['304014'],
        'SM4top': ['412043']
        }

        # invert the DSID 
        dsid_to_process = {dsid: process for process, dsids in DSID_list.items() for dsid in dsids}


        # Read the merged samples or the unmerged
        dsid_found = False
        for file in os.listdir(samples_dir): # Check for merged samples
            for dsid_group in DSID_list.values():
                for dsid in dsid_group:
                    if dsid in file:
                        dsid_found = True # This means unmerged samples
                    break  
                if dsid_found:
                    break 
            if dsid_found:
                break  

        # Unmerged samples:
        if dsid_found:
            print("Working on unmerged samples")
            print("Filling chains")
            for file in os.listdir(samples_dir):
                file_path = samples_dir + "/"+ str(file) + str("/") + tree
                dsid = extract_dsid(file)    
                if dsid in dsid_to_process:
                    process = dsid_to_process[dsid] # get process
                    if process == 'tHq':
                        Chain_tHq.Add(file_path)
                        #print("File " + str(file) + " is tHq")
                    elif process == 'ttbar':
                        Chain_ttbar.Add(file_path)
                        #print("File " + str(file) + " is ttbar")
                    elif process == 'tWH':
                        Chain_tWH.Add(file_path)
                    else:  # For all other processes
                        Chain_others.Add(file_path)
                        #print("File " + str(file) + " is other")
        # Merged samples
        if dsid_found == False:
            print("Working on merged samples")
            print("Filling chains")
            for file in os.listdir(samples_dir):
                file_path = samples_dir + "/"+ str(file) + str("/") + tree   
                if 'tHq.root' in file:
                    Chain_tHq.Add(file_path)
                    print("File "+str(file)+" is tHq")
                elif 'ttbar.root' in file:
                    Chain_ttbar.Add(file_path)
                    print("Filen "+str(file)+" is ttbar")
                elif 'tWH.root' in file:
                    Chain_tWH.Add(file_path)
                    print("File "+str(file)+" is tWH")
                elif 'data' in file:
                    print("File "+str(file)+" is ignored")
                else:
                    Chain_others.Add(file_path)
                    print("File " + str(file) + " is other")
        
        print("Define target and rest")
        # Initialize Chain_rest as a TChain
        Chain_rest = TChain(tree)
        Chain_target = TChain(tree)

        if bdt == 'tHq':
            Chain_target = Chain_tHq
            for file in Chain_ttbar.GetListOfFiles():
                Chain_rest.Add(file.GetTitle())
            for file in Chain_tWH.GetListOfFiles():
                Chain_rest.Add(file.GetTitle())
            for file in Chain_others.GetListOfFiles():
                Chain_rest.Add(file.GetTitle())

        elif bdt == 'tH':
            for file in Chain_tHq:
                Chain_target.Add(file.GetTitle())
            for file in Chain_tWH:
                Chain_target.Add(file.GetTitle())
            for file in Chain_ttbar.GetListOfFiles():
                Chain_rest.Add(file.GetTitle())
            for file in Chain_others.GetListOfFiles():
                Chain_rest.Add(file.GetTitle())

        elif bdt == 'ttbar':
            if channel == "SS":
                print("Error: No BDT(ttbar) in the SS channel")
            else:
                Chain_target = Chain_ttbar
                for file in Chain_tHq.GetListOfFiles():
                    Chain_rest.Add(file.GetTitle())
                for file in Chain_tWH.GetListOfFiles():
                    Chain_rest.Add(file.GetTitle())
                for file in Chain_others.GetListOfFiles():
                    Chain_rest.Add(file.GetTitle())
        else:
            print("Error: the otpion '--target' must be either tHq, tH or ttbar")
            exit()


        h1_BDT_targ  = TH1F("BDT_targ", "BDT", 50,0,1)
        h1_BDT_rest  = TH1F("BDT_rest", "BDT", 50,0,1)

        print("Filling histograms:")
        print("     -  TH1F for target process")
        for event in Chain_target:
            if bdt == 'tHq': 
                if channel == "OS":
                    if event.OS_LepHad == 1: h1_BDT_targ.Fill(event.bdt_tHq, event.weight_nominalWtau * lumi)
                elif channel == "SS":
                    if event.OS_LepHad == 0: h1_BDT_targ.Fill(event.bdt_tHq, event.weight_nominalWtau * lumi)
            if bdt == 'ttbar': 
                if channel == "OS":
                    if event.OS_LepHad == 1: h1_BDT_targ.Fill(event.bdt_ttbar, event.weight_nominalWtau * lumi)
                elif channel == "SS":
                    if event.OS_LepHad == 0: h1_BDT_targ.Fill(event.bdt_ttbar, event.weight_nominalWtau * lumi)
                
        print("     -  TH1F for rest of processes")
        for event in Chain_rest:
            if bdt == 'tHq': 
                if channel == "OS":
                    if event.OS_LepHad == 1: h1_BDT_rest.Fill(event.bdt_tHq, event.weight_nominalWtau * lumi)
                elif channel == "SS":
                    if event.OS_LepHad == 0: h1_BDT_rest.Fill(event.bdt_tHq, event.weight_nominalWtau * lumi)
            if bdt == 'ttbar': 
                if channel == "OS":
                    if event.OS_LepHad == 1: h1_BDT_rest.Fill(event.bdt_ttbar, event.weight_nominalWtau * lumi) 
                elif channel == "SS":
                    if event.OS_LepHad == 0: h1_BDT_rest.Fill(event.bdt_ttbar, event.weight_nominalWtau * lumi)
        print("Histograms filled")  


        # Store the histo as root objet: This way we don't have to read it every time
        #if saveHisto == True:
        print("Saving histogram histogram") 
        if bdt == 'tHq' and channel == "OS": h1_targ_object = TFile("TH1F_BDT_tHq_OS_Target.root", "recreate")
        if bdt == 'ttbar' and channel == "OS": h1_targ_object = TFile("TH1F_BDT_ttbar_OS_Target.root", "recreate")
        if bdt == 'tHq' and channel == "SS": h1_targ_object = TFile("TH1F_BDT_tHq_SS_Target.root", "recreate")
        h1_targ_object.cd()
        h1_BDT_targ.Write()
        h1_targ_object.Close()
        if bdt == 'tHq' and channel == "OS": h1_rest_object = TFile("TH1F_BDT_tHq_OS_Rest.root", "recreate")
        if bdt == 'ttbar' and channel == "OS": h1_rest_object = TFile("TH1F_BDT_ttbar_OS_Rest.root", "recreate")
        if bdt == 'tHq' and channel == "SS": h1_rest_object = TFile("TH1F_BDT_tHq_SS_Rest.root", "recreate")
        h1_rest_object.cd()
        h1_BDT_rest.Write()
        h1_rest_object.Close()
        print("Histogram histogram saved")

    #######################################################
    # Build the histograms for target and rest processes  #
    #######################################################    
    elif readHist == True:
        print("Reading the stored histograms")
        if bdt == 'tHq' and channel == "OS":
            f_target_name = "TH1F_BDT_tHq_OS_Target.root"
            f_rest_name = "TH1F_BDT_tHq_OS_Rest.root"
        if bdt == 'ttbar' and channel == "OS":
            f_target_name = "TH1F_BDT_ttbar_OS_Target.root"
            f_rest_name = "TH1F_BDT_ttbar_OS_Rest.root"
        if bdt == 'tHq' and channel == "SS":
            f_target_name = "TH1F_BDT_tHq_SS_Target.root"
            f_rest_name = "TH1F_BDT_tHq_SS_Rest.root"
    
        if not os.path.exists(f_target_name): 
            print("WARNING: The directory '" + str(f_target_name) + "' does not exist")
            exit()
        if not os.path.exists(f_rest_name): 
            print("WARNING: The directory '" + str(f_rest_name) + "' does not exist")
            exit()
    
        f_target = TFile(f_target_name)
        f_rest = TFile(f_rest_name)
        h1_BDT_targ = f_target.Get("BDT_targ")
        h1_BDT_rest = f_rest.Get("BDT_rest")
    else:
        print("Error :: readHist must be True or False")
        exit()
    
    # Loop over cut-points
    cutPoints = [0.1,0.125,0.15,0.175,0.2,0.225,0.25,0.275,0.3,0.325,0.35,0.375,0.4,0.425,0.45,0.475,0.5,0.525,0.55,0.575,0.6,0.625,0.65,0.675,0.7,0.725,0.75,0.775,0.8,0.825,0.85,0.875,0.9,0.925,0.95]
    significances = []
    StoBs = []
    best_significance = 0 
    best_threshold = 0
    signal_evts = []
    print("Explore BDT thresholds")  
    for threshold in cutPoints:
        nEvents_target, nEvents_rest = get_yields_left(h1_BDT_targ, h1_BDT_rest, threshold)
        
        # Calculate significance and ratio
        if nEvents_rest > 0:
            #term = (nEvents_rest + nEvents_target) * math.log(1 + nEvents_target / float(nEvents_rest)) - 2 * nEvents_target
            #significance = math.sqrt(2 * term)
            significance = nEvents_target/math.sqrt(nEvents_rest)
            if bdt == 'tHq':
                StoB = 100*nEvents_target / nEvents_rest
            if bdt == 'ttbar':
                StoB = 100*nEvents_target / (nEvents_rest+nEvents_target)
            print("Info :: If " +str(threshold)+" \t --> significance:: "+str(significance))
            print("Info ::      \t \t --> StoB:: "+str(StoB))
            print("Info ::      \t Target = "+str(nEvents_target))
            print("Info ::      \t Rest   = "+str(nEvents_rest))
        else:
            significance = 0
            StoB = 0
            print("Info :: If " +str(threshold)+" --> significance 0")

        signal_evts.append(nEvents_target)
        significances.append(significance)
        StoBs.append(StoB)

        if significance > best_significance:
            best_significance = significance
            best_threshold = threshold
            
    print("Best :: cut = "+str(best_threshold)+" significance ="+str(best_significance))


    # =========================================
    #  Plot
    # ========================================
    # Convert lists to arrays for TGraph
    bdt_cuts_array = array('f', cutPoints)
    significances_array = array('f', significances)
    StoBs_array = array('f', StoBs)
    signal_evts_array = array('f', signal_evts)

    #print bdt_cuts_array
    #print significances_array
    #print StoBs_array

    #print len(bdt_cuts_array)
    #print len(significances_array)
    #print len(StoBs_array)

    print("Plots")
    if False:
        print("Two panels plots")
        # Create a figure and a set of subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

        # Plotting significances_array vs bdt_cuts_array
        ax1.plot(bdt_cuts_array, significances_array, 'b-')  # 'b-' is a blue line
        ax1.set_ylabel('Significance')
        ax1.set_title('Significance and S/B Ratio vs BDT Cuts')

        # Plotting StoBs_array vs bdt_cuts_array
        ax2.plot(bdt_cuts_array, StoBs_array, 'r-')  # 'r-' is a red line
        ax2.set_xlabel('BDT Cuts')
        if bdt == 'tHq':
            ax2.set_ylabel('S/B [%]')
        else:
            ax2.set_ylabel('tt/All [%]')

        #plt.show()
        plt.savefig('BDT_thereholds_'+str(channel)+'_'+str(bdt)+'_TwoPanels.pdf', format='pdf')
        plt.Close()

    if True:
        # Create a figure and a single subplot
        fig, ax1 = plt.subplots(figsize=(12, 6))  # Adjusting the figure size

        # Set xlabel based on condition
        if bdt == 'tHq' and channel == "OS": 
            ax1.set_xlabel(r'BDT($tH|_{OS}$) hreshold', fontsize=16)
        elif bdt == 'ttbar' and channel == "OS": 
            ax1.set_xlabel(r'BDT($t\bar{t}|_{OS}$) threshold', fontsize=16)
        elif bdt == 'tHq' and channel == "SS": 
            ax1.set_xlabel(r'BDT($tH|_{SS}$) threshold', fontsize=16)

        # Create the second y-axis
        ax2 = ax1.twinx()

        # Create the third y-axis
        ax3 = ax1.twinx()
        ax3.spines["right"].set_position(("axes", 1.15))  # Position the third y-axis further out
        ax3.spines["right"].set_visible(True)

        # Define colors for each y-axis
        color_sig = 'tab:red'
        color_stob = 'tab:blue'
        color_nEvts = 'tab:green'

        # Define y-axis labels
        ylabel2 = r'$\frac{tHq}{Bkg}$ (%)' if bdt == 'tHq' else r'$\frac{t\bar{t}}{All}$ (%)'
        ylabel3 = r'$tHq$ yields' if bdt == 'tHq' else r'$t\bar{t}$ yields'

        # Set y-axis labels and colors
        ax1.set_ylabel('Significance', color=color_sig, fontsize=16)
        ax2.set_ylabel(ylabel2, color=color_stob, fontsize=18)
        ax3.set_ylabel(ylabel3, color=color_nEvts, fontsize=14)

        # Plot the data
        p1, = ax1.plot(bdt_cuts_array, significances_array, color=color_sig, label='Significance')
        if bdt == 'tHq': p2, = ax2.plot(bdt_cuts_array, StoBs_array, color=color_stob, label='S/B')
        if bdt == 'ttbar': p2, = ax2.plot(bdt_cuts_array, StoBs_array, color=color_stob, label=r'$t\bar{t}$/All')
        if bdt == 'tHq': p3, = ax3.plot(bdt_cuts_array, signal_evts_array, color=color_nEvts, label='Signal events')
        if bdt == 'ttbar': p3, = ax3.plot(bdt_cuts_array, signal_evts_array, color=color_nEvts, label=r'$t\bar{t}$ events')

        # Set tick parameters
        tkw = dict(size=4, width=1.5)
        ax1.tick_params(axis='y', labelcolor=color_sig, **tkw)
        ax2.tick_params(axis='y', labelcolor=color_stob, **tkw)
        ax3.tick_params(axis='y', labelcolor=color_nEvts, **tkw)
        ax1.tick_params(axis='x', **tkw)

        # Legend
        lines = [p1, p2, p3]
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels, loc='upper left')

        # Adjust the layout to make room for the third y-axis
        fig.tight_layout(rect=[0, 0, 0.9, 1])  # Left, Bottom, Right, Top
        plt.subplots_adjust(right=0.75)

        # Save the figure
        plt.savefig('BDT_Resplicated_For_Thesis_thresholds_'+str(channel)+'_'+str(bdt)+'_SinglePanel_with_nEvts_NewSamples.pdf', format='pdf')
        plt.close()


# =========================================
#  get_yields_left: Obtain the yields given 
#  a cut of the form BDT > cut
# =========================================
def get_yields_left(h1_target, h1_rest, cut):
    nEvents_target = h1_target.Integral(h1_target.FindFixBin(cut), h1_target.FindFixBin(1))
    nEvents_rest = h1_rest.Integral(h1_rest.FindFixBin(cut), h1_rest.FindFixBin(1))
    return nEvents_target, nEvents_rest 

# =========================================
#  extract_dsid
# =========================================
def extract_dsid(filename):
    parts = filename.split('.')
    if len(parts) > 1:
        return parts[1] 
    return None

# =================================================================================
#  __main__
# =================================================================================
if __name__ == '__main__':
  main(sys.argv[1])

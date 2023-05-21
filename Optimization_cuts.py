try: import ROOT
except: sys.exit("\nROOT is not available\n")

from time import time
from optparse import OptionParser
import math

list_of_process = ['qcd', 'zdiboson','wjets','top','tchannel']
rootdirectory = 'topPlots/'
nominal_cuts = '_mass%i_ht%i_eta%.2f_delta%.2f'%(130., 195., 1.25, 2.25)
nominal_cuts = nominal_cuts.replace(".","")

def getFirstKey(item):
    return item[0]

def getSecondKey(item):
    return item[1]


def main():
    parser = OptionParser()
    parser.add_option('-f', dest='file', action='store', default=None,   help='file with histograms from readResultsTree cut_study')
    (options,args) = parser.parse_args()
    
    mass_threshold     = [130.]
    ht_threshold       = [180.]
    eta_threshold      = [1.0, 1.10, 1.25, 1.40, 1.55, 1.70, 1.85, 2.0, 2.15, 2.30]
    deltaeta_threshold = [0.85, 1.0, 1.10, 1.25, 1.40, 1.55, 1.70, 1.85, 2.0, 2.10, 2.25]
    
    cuts_better_performance  = []
    
    tfile = ROOT.TFile(options.file, "read")
    
    h_nominal_signal = tfile.Get(rootdirectory+'signal'+nominal_cuts)
    h_nominal_backgd = tfile.Get(rootdirectory+'backgd'+nominal_cuts)

    nominal_signal_content = h_nominal_signal.GetBinContent(2)
    
    nominal_SB     = h_nominal_signal.GetBinContent(2)/h_nominal_backgd.GetBinContent(2)
    nominal_SBerr  = 0.
    nominal_sig    = h_nominal_signal.GetBinContent(2)/math.sqrt(h_nominal_signal.GetBinContent(2)+h_nominal_backgd.GetBinContent(2))
    nominal_sigerr = 0.
    
    print "\nnominal cuts:", nominal_cuts
    print "nominal S/B:          %.2f" %(nominal_SB)
    print "nominal S/sqrt(S+B): %.2f" %(nominal_sig), "\n"

    for mt in mass_threshold:
        for ht in ht_threshold:
            for e in eta_threshold:
                for d in deltaeta_threshold:

                    name = '_mass%i_ht%i_eta%.2f_delta%.2f'%(mt, ht, e, d)
                    name = name.replace(".","")
                    
                    h_temp_signal = tfile.Get(rootdirectory+'signal'+name)
                    h_temp_backgd = tfile.Get(rootdirectory+'backgd'+name)
                    
                    content_signal = h_temp_signal.GetBinContent(2)
                    content_backgd = h_temp_backgd.GetBinContent(2)
                    
                    h_temp_signal.IsA().Destructor(h_temp_signal)
                    h_temp_backgd.IsA().Destructor(h_temp_backgd)
                    
                    total_yields = content_signal+content_backgd
                    tmp_SB  = content_signal/content_backgd
                    tmp_sig = content_signal/math.sqrt(total_yields)
                    
                    if content_signal < nominal_signal_content: continue
                    if tmp_SB         < nominal_SB :            continue
                    if tmp_sig        < nominal_sig:            continue

                    cuts_better_performance.append((tmp_SB, tmp_sig, total_yields, name))


    best_SB  = sorted(cuts_better_performance, key=getFirstKey)[-1]
    best_sig = sorted(cuts_better_performance, key=getSecondKey)[-1]
    
    print "Now the results."
    print "Best S/B"
    print "-> Cuts:",best_SB[3]
    print "-> S/B:          %.2f" %(best_SB[0])
    print "-> S/sqrt(S+B): %.2f" %(best_SB[1])
    print "Best S/sqrt(S+B)"
    print "-> Cuts:", best_sig[3]
    print "-> S/B:          %.2f" %(best_sig[0])
    print "-> S/sqrt(S+B): %.2f" %(best_sig[1])
    print
    
    best_SB_process  = {}
    best_sig_process = {}
    nominal_process  = {}
    
    for p in list_of_process:

        h_temp_SB  = tfile.Get(rootdirectory+p+best_SB[3]+"_costhetaN")
        h_temp_sig = tfile.Get(rootdirectory+p+best_sig[3]+"_costhetaN")
        h_temp_nom = tfile.Get(rootdirectory+p+nominal_cuts+"_costhetaN")
        
        best_SB_process[p]  = h_temp_SB.Integral()
        best_sig_process[p] = h_temp_sig.Integral()
        nominal_process[p]  = h_temp_nom.Integral()
        
        h_temp_SB.IsA().Destructor(h_temp_SB)
        h_temp_sig.IsA().Destructor(h_temp_sig)
        h_temp_nom.IsA().Destructor(h_temp_nom)
    
    
    print "Yields content:"
    print "\nBest S/B"
    for p in list_of_process:
        print "%8s: %.2f, %.2f (over total)" %(p, best_SB_process[p], best_SB_process[p]/best_SB[2])
    print "\nBest S/sqrt(S+B)"
    for p in list_of_process:
        print "%8s: %.2f, %.2f (over total)" %(p, best_sig_process[p], best_sig_process[p]/best_sig[2])
    print "\nNominal"
    for p in list_of_process:
        print "%8s: %.2f" %(p, nominal_process[p])
    print




    
if __name__ == '__main__':
    main()

import sys

try: import ROOT
except: sys.exit("\nROOT is not available\n")

from time import time
from optparse import OptionParser
import minuit2
from array import array

def wait(message):
    rep = ''
    while not rep in ['y','Y','yes','yeah']:
        rep = raw_input('\n%s: '%(message))
        if 1 < len(rep):
            rep = rep[0]


     
def GetStackElements(stack):

	process_a = ['qcd', 'zjets','diboson','wlight','wheavy','ttbar','schannel','wtchannel','tchannel']
	process_b = ['qcd', 'zjets','diboson','wjets','ttbar','schannel','wtchannel','tchannel']
	process_c = ['qcd', 'zdiboson','wlight','wheavy','top','tchannel']
	process_d = ['qcd', 'zdiboson','wjets','top','tchannel']
	process_e = ['tchannel']
	process_list = 0
	TList =  stack.GetHists()	
	
	if len(TList) == len(process_a)   : process_list = process_a
	elif len(TList) == len(process_b) : process_list = process_b
	elif len(TList) == len(process_c) : process_list = process_c
	elif len(TList) == len(process_d) : process_list = process_d
	elif len(TList) == len(process_e) : process_list = process_e
	else: sys.exit("THE NUMBER OF BACKGROUNDS IN HISTOGRAMS IS WRONG, CHECK THEM OR UPDATE THE LIST OF PROCESS")

	histo_process = {}
	
	for i in range(len(TList)):
		histo_process[process_list[i]] = TList.At(i)


	return histo_process



def get_histos (options, cregion, h_names, h_data, h_stack):

    file = {}
    print "\n Loading files in", cregion
    if options['elfile'][cregion] : file['el'] = ROOT.TFile(options['elfile'][cregion])
    if options['mufile'][cregion] : file['mu'] = ROOT.TFile(options['mufile'][cregion])
    if len(file) == 0 : sys.exit("\nInsert input file\n")

    #print
    #print file['el']
    #print file['mu']
    #print

    channels = file.keys()

    for c in channels:
        print "Channel: ", c
        print 'Histogram: topPlots/'+h_names['data'][options['hist']]
        temp       = file[c].Get('topPlots/'+h_names['data'][options['hist']])
        h_data[c]  = temp.Clone(c+'_dataclone%s'%(cregion))
        h_stack[c] = GetStackElements(file[c].Get('topPlots/'+h_names['stack'][options['hist']]))

        for p in h_stack[c]: h_stack[c][p].SetDirectory(0)
        h_data[c].SetDirectory(0)

        file[c].Close()



def compute_globalSF( options, h_data_wjets=0, h_mcprocess_wjets=0, h_data_ttbar=0, h_mcprocess_ttbar=0, h_data_tchan=0, h_mcprocess_tchan=0):
    
    debug   = False
    doWjets = False
    doTtbar = False
    doTchan = False
    
    if len(h_data_wjets) > 0 : doWjets = True
    if len(h_data_ttbar) > 0 : doTtbar = True
    if len(h_data_tchan) > 0 : doTchan = True
    
    data_wjets        = array('f', [])
    MC_tchan_wjets    = array('f', [])
    MC_top_wjets      = array('f', [])
    MC_wjets_wjets    = array('f', [])
    MC_zdiboson_wjets = array('f', [])
    MC_qcd_wjets      = array('f', [])

    data_ttbar        = array('f', [])
    MC_tchan_ttbar    = array('f', [])
    MC_top_ttbar      = array('f', [])
    MC_wjets_ttbar    = array('f', [])
    MC_zdiboson_ttbar = array('f', [])
    MC_qcd_ttbar      = array('f', [])
    
    data_tchan        = array('f', [])
    MC_tchan_tchan    = array('f', [])
    MC_top_tchan      = array('f', [])
    MC_wjets_tchan    = array('f', [])
    MC_zdiboson_tchan = array('f', [])
    MC_qcd_tchan      = array('f', [])
	
    try :
        Nbins = h_data_wjets.GetNbinsX()
    except :
        Nbins = h_data_ttbar.GetNbinsX()


    for i in xrange(1,Nbins+2): # Take the overflow bin

        if doWjets :
            data_wjets.append(h_data_wjets.GetBinContent(i))
            MC_tchan_wjets.append(h_mcprocess_wjets['tchannel'].GetBinContent(i))
            MC_top_wjets.append(h_mcprocess_wjets['top'].GetBinContent(i))
            MC_wjets_wjets.append(h_mcprocess_wjets['wjets'].GetBinContent(i))
            MC_zdiboson_wjets.append(h_mcprocess_wjets['zdiboson'].GetBinContent(i))
            MC_qcd_wjets.append(h_mcprocess_wjets['qcd'].GetBinContent(i))

        if doTtbar :
            data_ttbar.append(h_data_ttbar.GetBinContent(i))
            MC_tchan_ttbar.append(h_mcprocess_ttbar['tchannel'].GetBinContent(i))
            MC_top_ttbar.append(h_mcprocess_ttbar['top'].GetBinContent(i))
            MC_wjets_ttbar.append(h_mcprocess_ttbar['wjets'].GetBinContent(i))
            MC_zdiboson_ttbar.append(h_mcprocess_ttbar['zdiboson'].GetBinContent(i))
            MC_qcd_ttbar.append(h_mcprocess_ttbar['qcd'].GetBinContent(i))
            
        if doTchan :
            data_tchan.append(h_data_tchan.GetBinContent(i))
            MC_tchan_tchan.append(h_mcprocess_tchan['tchannel'].GetBinContent(i))
            MC_top_tchan.append(h_mcprocess_tchan['top'].GetBinContent(i))
            MC_wjets_tchan.append(h_mcprocess_tchan['wjets'].GetBinContent(i))
            MC_zdiboson_tchan.append(h_mcprocess_tchan['zdiboson'].GetBinContent(i))
            MC_qcd_tchan.append(h_mcprocess_tchan['qcd'].GetBinContent(i))

    
    if debug :
        print "\nCheck content arrays:"

        if doWjets :
            print "Wjets: "
            print " data:  array = ",sum(data_wjets), " histogram = ", h_data_wjets.Integral()
            print " tchan: array = ",sum(MC_tchan_wjets), " histogram = ", h_mcprocess_wjets['tchannel'].Integral()
            print " top:   array = ",sum(MC_top_wjets), " histogram = ", h_mcprocess_wjets['top'].Integral()
            print " wjets: array = ",sum(MC_wjets_wjets), " histogram = ", h_mcprocess_wjets['wjets'].Integral()
            print " zdib:  array = ",sum(MC_zdiboson_wjets), " histogram = ", h_mcprocess_wjets['zdiboson'].Integral()
            print " qcd:   array = ",sum(MC_qcd_wjets), " histogram = ", h_mcprocess_wjets['qcd'].Integral()
            print
        if doTtbar :
            print "ttbar: "
            print " data:  array = ",sum(data_ttbar), " histogram = ", h_data_ttbar.Integral()
            print " tchan: array = ",sum(MC_tchan_ttbar), " histogram = ", h_mcprocess_ttbar['tchannel'].Integral()
            print " top:   array = ",sum(MC_top_ttbar), " histogram = ", h_mcprocess_ttbar['top'].Integral()
            print " wjets: array = ",sum(MC_wjets_ttbar), " histogram = ", h_mcprocess_ttbar['wjets'].Integral()
            print " zdib:  array = ",sum(MC_zdiboson_ttbar), " histogram = ", h_mcprocess_ttbar['zdiboson'].Integral()
            print " qcd:   array = ",sum(MC_qcd_ttbar), " histogram = ", h_mcprocess_ttbar['qcd'].Integral()
            print


    def logLikeliHood(b_tchan, b_top, b_wjets, b_zdiboson, b_qcd):
	        
        delta_top   = 0.06
        delta_wjets = 0.6
	
        likelihood = 0.
	
        for k in xrange(Nbins):

            mu_k_wjets = 0.
            mu_k_ttbar = 0.
            mu_k_tchan = 0.
		
            if doWjets :
                mu_k_wjets += b_tchan*MC_tchan_wjets[k]+b_top*MC_top_wjets[k]+b_wjets*MC_wjets_wjets[k]+b_zdiboson*MC_zdiboson_wjets[k]+b_qcd*MC_qcd_wjets[k]

            if doTtbar :
                mu_k_ttbar += b_tchan*MC_tchan_ttbar[k]+b_top*MC_top_ttbar[k]+b_wjets*MC_wjets_ttbar[k]+b_zdiboson*MC_zdiboson_ttbar[k]+b_qcd*MC_qcd_ttbar[k]

            if doTchan :
                mu_k_tchan += b_tchan*MC_tchan_tchan[k]+b_top*MC_top_tchan[k]+b_wjets*MC_wjets_tchan[k]+b_zdiboson*MC_zdiboson_tchan[k]+b_qcd*MC_qcd_tchan[k]

            if mu_k_wjets > 0. :
                likelihood += -mu_k_wjets + data_wjets[k]*ROOT.TMath.log(mu_k_wjets)

            if mu_k_ttbar > 0. :
                likelihood += -mu_k_ttbar + data_ttbar[k]*ROOT.TMath.log(mu_k_ttbar)
                
            if mu_k_tchan > 0. :
                likelihood += -mu_k_tchan + data_tchan[k]*ROOT.TMath.log(mu_k_tchan)

        if doWjets :
            likelihood += -0.5*(b_wjets-1.)*(b_wjets-1.)/(delta_wjets*delta_wjets)
            likelihood += -0.5*(b_top-1.)*(b_top-1.)/(delta_top*delta_top)
        if doTtbar :
            likelihood += -0.5*(b_wjets-1.)*(b_wjets-1.)/(delta_wjets*delta_wjets)
            likelihood += -0.5*(b_top-1.)*(b_top-1.)/(delta_top*delta_top)
        if doTchan :
            likelihood += -0.5*(b_wjets-1.)*(b_wjets-1.)/(delta_wjets*delta_wjets)
            likelihood += -0.5*(b_top-1.)*(b_top-1.)/(delta_top*delta_top)

        return -1.*likelihood


    m = minuit2.Minuit2(logLikeliHood)


    m.values["b_tchan"]    = 1.
    m.values["b_top"]      = 1.
    m.values["b_wjets"]    = 1.
    m.values["b_zdiboson"] = 1.
    m.values["b_qcd"]      = 1.

    m.up = 0.5
    m.strategy = 2

    if not options.tchannel: m.fixed['b_tchan']    = True
    if not options.top:      m.fixed['b_top']      = True
    if not options.wjets:    m.fixed['b_wjets']    = True
    if not options.zdiboson: m.fixed['b_zdiboson'] = True
    if not options.qcd:      m.fixed['b_qcd']      = True

    #m.printMode = 1

    m.migrad()
    
    print "\n Results: "
    print "beta tchannel = %.3f +- %.3f" %(m.values["b_tchan"], m.errors["b_tchan"])
    print "beta top      = %.3f +- %.3f" %(m.values["b_top"], m.errors["b_top"])
    print "beta wjets    = %.3f +- %.3f" %(m.values["b_wjets"],m.errors["b_wjets"])
    print "beta zdiboson = ", m.values["b_zdiboson"]
    print "beta qcd      = ", m.values["b_qcd"]
    print

    finaltop  = m.values["b_top"]
    finalwjet = m.values["b_wjets"]
    finaltchan = m.values["b_tchan"]

    return finalwjet, finaltop, finaltchan



def main():
    parser = OptionParser()
    parser.add_option('--ttpath', dest='tpath',    action='store',   default='./', help='directory containing ttbarCR and signal ROOT file')
    parser.add_option('--ttel',   dest='ttelfile', action='store',   default=None, help='file for electrons ttbar CR')
    parser.add_option('--ttmu',   dest='ttmufile', action='store',   default=None, help='file for muons ttbar CR')
    parser.add_option('--tchel',  dest='tchelfile', action='store',  default=None, help='file for electrons signal region')
    parser.add_option('--tchmu',  dest='tchmufile', action='store',  default=None, help='file for muons signal region')
    parser.add_option('--wpath',  dest='wpath',     action='store',  default='./', help='directory containing WjetsCR ROOT file')
    parser.add_option('--wel',    dest='wjetelfile', action='store', default=None, help='file for electrons W+jets CR')
    parser.add_option('--wmu',    dest='wjetmufile', action='store', default=None, help='file for muons W+jets CR')
    parser.add_option('-c',       dest='channel',   action='store',  default='both', help='channel: el, mu, both')
    parser.add_option('--hist',   dest='hist',      action='store',  default=None, help='choose pT(W): pt, or MET: met')
    parser.add_option('--tchan',  dest='tchannel',  action='store_true', default=False, help='activate beta_tchannel')
    parser.add_option('--top',    dest='top',   action='store_true', default=False, help='activate beta_top')
    parser.add_option('--wjets',  dest='wjets', action='store_true', default=False, help='activate beta_wjets')
    parser.add_option('--zdiboson', dest='zdiboson', action='store_true', default=False, help='activate beta_diboson')
    parser.add_option('--qcd',      dest='qcd',      action='store_true', default=False, help='activate beta_qcd')

    (options,args) = parser.parse_args()


    histoname = {'stack': {'pt':'h_wbosonfromtop_pt_2-jetbin_tag_Selection_stack', 'met':'MET_stack'},
                 'data' : {'pt':'h_wbosonfromtop_pt_2-jetbin_tag_Selection_data', 'met':'MET_data'}}
    histonamettbar = {'stack': {'pt':'h_wbosonfromtop_pt_4-jetbin_tag_PreSelection_stack', 'met':'MET_stack'},
                      'data' : {'pt':'h_wbosonfromtop_pt_4-jetbin_tag_PreSelection_data', 'met':'MET_data'}}
    
    filename = {'pt':'pT', 'met':'MET'}
    
    channels = []
    process  = []
    
    if options.channel == 'both': channels = ['el', 'mu']
    else: channels.append(options.channel)
    
    h_data_ttbar    = {}
    h_MC_ttbar      = {}
    h_data_tchan    = {}
    h_MC_tchan      = {}
    h_data_wjet     = {}
    h_MC_wjet       = {}
    h_Wjet_fromdata = {}
    h_SF     = {}
    process  = []
    setup    = {}

    setup['hist'] = options.hist
    setup['elfile'] = {}
    setup['mufile'] = {}


    if options.wjetelfile : setup['elfile']['wjets'] = options.wpath+"/"+options.wjetelfile
    if options.wjetmufile : setup['mufile']['wjets'] = options.wpath+"/"+options.wjetmufile
    if options.ttelfile   : setup['elfile']['ttbar'] = options.tpath+"/"+options.ttelfile
    if options.ttmufile   : setup['mufile']['ttbar'] = options.tpath+"/"+options.ttmufile
    if options.tchelfile  : setup['elfile']['tchan'] = options.tpath+"/"+options.tchelfile
    if options.tchmufile  : setup['mufile']['tchan'] = options.tpath+"/"+options.tchmufile

    if not options.hist : sys.exit("\nchoose what histogram you want to use\n")
    
    if options.wjetelfile or options.wjetmufile :
        get_histos (setup,'wjets', histoname, h_data_wjet, h_MC_wjet)
        process = h_MC_wjet[channels[0]].keys()
        
    if options.ttelfile or options.ttmufile:
        get_histos (setup,'ttbar', histonamettbar, h_data_ttbar, h_MC_ttbar)
        process = h_MC_ttbar[channels[0]].keys()
    
    if options.tchelfile or options.tchmufile :
        get_histos (setup,'tchan', histoname, h_data_tchan, h_MC_tchan)
        process = h_MC_tchan[channels[0]].keys()

    
    topSF   = {'el':1.,'mu':1.}
    wjetsSF = {'el':1.,'mu':1.}
    tchanSF = {'el':1.,'mu':1.}

    if options.top or options.wjets :
        print "\n Computing global SF's"
        for c in channels:
            print "Channel: ",c
            if options.tchannel:
              wjetsSF[c], topSF[c], tchanSF[c] = compute_globalSF( options, h_data_wjet[c], h_MC_wjet[c], h_data_ttbar[c], h_MC_ttbar[c], h_data_tchan[c], h_MC_tchan[c])
            else:
              wjetsSF[c], topSF[c], tchanSF[c] = compute_globalSF( options, h_data_wjet[c], h_MC_wjet[c], h_data_ttbar[c], h_MC_ttbar[c], [], [])


    print "\n===>pT REWEIGHTING..."
    for c in channels:

        print "Channel: ",c,
        h_Wjet_fromdata[c] = h_data_wjet[c].Clone('Wfromdata_%s'%(c))
        h_Wjet_fromdata[c].SetDirectory(0)
        
        for p in process:
            if p == 'wjets': continue
            else: h_Wjet_fromdata[c].Add(h_MC_wjet[c][p], -1.)

        h_SF[c] = h_Wjet_fromdata[c].Clone(c+'_SFactors')
        h_SF[c].Divide(h_MC_wjet[c]['wjets'])

        print " done!"

    print 
    outfile = ROOT.TFile("Wjets_%s_reweighting.root"%(filename[options.hist]),'RECREATE')
    outfile.cd()
    for c in channels: 
        h_SF[c].Write()
    outfile.Close()
    
    

    
if __name__ == '__main__':
    main()

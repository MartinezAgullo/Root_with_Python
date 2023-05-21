#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time
import os,sys
from optparse import OptionParser
from array import array

try:    import ROOT
except: sys.exit('ROOT is not available')

from handling_files   import identifyFiles, config_process_list
from histograms_stuff import makeHistograms, make_stacks, save_histos
from Cuts_Selections  import pass_Selection, pass_Preselection, load_cuts, cuts_study, migration, closure, angular_dist, efficiency
from Ttree_variables  import load_treevars

ROOT.gROOT.SetBatch(True)

analysis_list = ['cut_study', 'get_angles', 'migration', 'closure', 'efficiency']

controlregion_list = ['signal', 'highmass', 'ttbar', 'wjets', 'cut_study', 'custom']

reweigting_files = {'met': 'Wjets_MET_reweighting.root', 'pt':'Wjets_pT_reweighting.root'}

def main():
    
    parser = OptionParser()
    parser.add_option('-i','--inputDir',  dest='inputdir',action='store', default='./', help='directory containing normal input files')
    parser.add_option('-d','--outputDir', dest='outputdir',  action='store', default='../', help='directory to store outputs')
    parser.add_option('-s','--sample',    dest='sample',  action='store', default=None, help='Run over selected sample/s')
    parser.add_option('-c','--channel',   dest='channel', action='store', default=None, help='mu for muons, el electrons, both for combined')
    parser.add_option('-o','--outputname',dest='name',    action='store', default='test_output',help='output file name')
    parser.add_option('-a','--analysis', dest='analysis', action='store', default=None, help='load histograms needed for cut study, migration matrix...')
    parser.add_option('-N','--Nevents',  dest='Nevents',  action='store', default=0,    help='run over n events')
    parser.add_option('-v','--verbose',  dest='verbose',  action='store_true', default=False, help='increase verbosity')
    parser.add_option('--combined',      dest='combined', action='store_true', default=False, help='combine mu and el')
    parser.add_option('--data',    dest='includedata',    action='store_true', default=False, help='include data samples in your search. Useful if you want to read syst. samples')
    parser.add_option('--qcd',     dest='includeqcd',     action='store_true', default=False, help='include qcd samples in your search. Useful if you want to read syst. samples')
    parser.add_option('--nbins',   dest='nbins',          action='store',      default=0,     help='Change the binning for all the histos')
    parser.add_option('--cregion', dest='region',         action='store',      default='signal', help='Select the control region you want to use, highmass, signal, ttbar (default signal)')
    parser.add_option('--doplots', dest='doplots',        action='store_true', default=False,    help='make plots, check the plots to be done before run!!')
    parser.add_option('--reweighting', dest='reweighting',action='store',      default=None,     help='do a reweighting using pt(W) or MET distribution' )
    parser.add_option('--syst',        dest='systematic',       action='store',      default='nominal',help='insert the syst you want to run on, default=nominal')
    parser.add_option('--list',        dest='listfiles',  action='store',      default=None,     help='insert a file with the list of samples you want to run on')
    parser.add_option('--binsAsym',      dest='binsAsym', action='store_true', default=False, help='Change binning to better define A_plus and A_minus')
    (options,args) = parser.parse_args()
    
    if not options.channel:  sys.exit("\nPlease choose channel: el, mu, both\n")
    if not options.analysis: sys.exit("\nPlease choose the thing you are doing: cut_study, migration, get_angles, closure \n")
    if options.analysis not in analysis_list : sys.exit("\nPlease choose the thing you are doing: cut_study, migration, get_angles, closure \n")
    if options.analysis == 'cut_study': options.region = 'cut_study'
    if options.region not in controlregion_list: sys.exit("\nPlease, choose a correct region to define the cuts to be applied"+" ".join(controlregion_list))
    
    name = options.name
    
    channel = [options.channel]    
    if options.channel == 'both': channel = ['el', 'mu']

    print "\n"+40*"="
    print "== readResultsTree is going to be executed"
    print '== Reading files from:'
    print '== -> ',os.path.abspath(options.inputdir)
    print '== Storing files at:'
    print '== -> ',os.path.abspath(options.outputdir)
    print "== With the next setup:"
    print "== -> Analysis: ", options.analysis
    print "== -> Region:   ", options.region
    print "== -> Channels: ", " ".join(channel)
    if options.combined: print "== -> Combining el and mu channels!!"
    else:                print "== -> el and mu channels are stored separately"
    if options.reweighting: print "== -> Reweighting the W+jets background using", options.reweighting, "distribution"
    if options.sample:      print "== Running over selected sample(s) with ID:", options.sample
    if options.listfiles:   print "== Running over samples listed in file:", options.listfiles
    print "== Output will be save in a file wich main name is:", name
    print 40*"="+"\n"
    
    # Get files
    Files = identifyFiles(options)
    
    yields = {}
    process_list = config_process_list
    if options.analysis in ['migration', 'closure']: process_list = ['tchannel']
    
    for c in channel:
        yields[c] = {}
        for p in process_list: yields[c][p] = {'presel': 0., 'sel': 0.}

    print "\n"+40*"="
    print "==> Running over all input files"

    if options.combined:
        # make your histos, the histos are filled w.r.t the current process, dont care about channel
        # so they are filled for both channels
    
        h_types    = Files[channel[0]].keys()
        
        for t in h_types:
            histograms = makeHistograms(options.analysis, process_list,options.nbins, options.binsAsym)
            
            for p in process_list: yields[c][p] = {'presel': 0., 'sel': 0.}
            
            for c in channel:

                print "\nChannel: ", c
                for p,f in Files[c][t]:
                    if p not in process_list: sys.exit("\n * Check the list of process to be used in handling_files.py\n")
                    temp_yields = fillHistograms(histograms, f, p, options)
                    yields[c][p]['presel'] += temp_yields[0]
                    yields[c][p]['sel'] += temp_yields[1]
                print "end channel ", c
        
            print "\nstoring"
            save_histos(name+'_comb', config_process_list, histograms, options.analysis, options.outputdir)
            del histograms

            print "\n===> Yields Preselection:"
            print repr("process").rjust(12), repr("el").rjust(8), repr("mu").rjust(8), repr("comb").rjust(8)
            for p in yields['el']:
                ye   = "%.1f"%(yields['el'][p]['presel'])
                ym   = "%.1f"%(yields['mu'][p]['presel'])
                comy = "%.1f"%(yields['el'][p]['presel']+yields['mu'][p]['presel'])
                print repr(p).rjust(12), repr(ye).rjust(8), repr(ym).rjust(8), repr(comy).rjust(8)
            print "\n===> Yields Selection:"
            print repr("process").rjust(12), repr("el").rjust(8), repr("mu").rjust(8), repr("comb").rjust(8)
            for p in yields['el']:
                ye   = "%.1f"%(yields['el'][p]['sel'])
                ym   = "%.1f"%(yields['mu'][p]['sel'])
                comy = "%.1f"%(yields['el'][p]['sel']+yields['mu'][p]['sel'])
                print repr(p).rjust(12), repr(ye).rjust(8), repr(ym).rjust(8), repr(comy).rjust(8)
            print "==="
    
    else:
        # make your histos for each channel, they will be filled by process
        # dont forget to destroy the histos before change to next channel
        for c in channel:
            
            good_channelname = {'el': 'electrons', 'mu': 'muons'}
            print "\nChannel: ", c
            
            for s in Files[c]:
                print "\nType: ", s
                
                histograms = None
                for p in process_list: yields[c][p] = {'presel': 0., 'sel': 0.}
                
                if options.analysis == 'get_angles':  name = 'topPlots'
                if s == 'nominal': name = 'topPlots_'+good_channelname[c]
                else:              name = 'topPlots_'+good_channelname[c]+'.'+s
                histograms = makeHistograms(options.analysis, process_list,options.nbins, options.binsAsym)
                
                for p,f in sorted(Files[c][s]):
                    temp_yields = fillHistograms(histograms, f, p, options)
                    yields[c][p]['presel'] += temp_yields[0]
                    yields[c][p]['sel'] += temp_yields[1]
                
                save_histos(name, config_process_list, histograms, options.analysis, options.outputdir)
                
                del histograms
            
                print "\n===> Yields Preselection:"
                print repr("process").rjust(12), repr(c).rjust(8)
                for p in sorted(yields[c]):
                    y = "%.1f"%(yields[c][p]['presel'])
                    print repr(p).rjust(10), repr(y).rjust(8)
                print "\n===> Yields Selection:"
                print repr("process").rjust(12), repr(c).rjust(8)
                for p in sorted(yields[c]):
                    y = "%.1f"%(yields[c][p]['sel'])
                    print repr(p).rjust(10), repr(y).rjust(8)
                print "==="



def normalize_to_lumi(tfile, process):
    
    if process in ['qcd', 'data'] : return 1.
    
    metavars = {
        'initialNbrOfEventsGenTimesPileUpWeighted': array('f',[0]),
        'cross_section': array('f',[0]),
        'k_factor'     : array('f',[0]),
        'totalLumi'    : array('f',[0])
        }
    
    metatree = tfile.Get('ResultsMetaTree')
    metatree.SetBranchStatus("*",0)
    #metatree.SetCacheSize(6000000) 
    
    for key in metavars:
        metatree.SetBranchStatus(key,1)
        metatree.SetBranchAddress(key,metavars[key])
    metatree.StopCacheLearningPhase()
    metatree.GetEntry(0)
    
    scaleF = metavars['k_factor'][0]*metavars['cross_section'][0]*metavars['totalLumi'][0]
    scaleF = scaleF/metavars['initialNbrOfEventsGenTimesPileUpWeighted'][0]
    
    return  scaleF



def ComputeWeight(lumi, ttreevars, region):
    mc_weight = {'signal':'combinedWeight', 'highmass':'combinedWeight', 'ttbar':'combinedWeight', 
                 'wjets':'combinedWeightForPretag', 'custom':'combinedWeight'}
    
    return lumi*ttreevars[mc_weight[region]][0]*ttreevars['matrixMethodWeights'].at(0)*ttreevars['SF_loosejets'][0]



def get_SF_histo(options, inputfile):
    
    h_temp = 0
    
    if 'el.root' in inputfile: 
        f = ROOT.TFile(reweigting_files[options.reweighting],'r')
        h_temp = f.Get('electron_SFactors')
    if 'mu.root' in inputfile: 
        f = ROOT.TFile(reweigting_files[options.reweighting],'r')
        h_temp = f.Get('muon_SFactors')
    
    h_temp.SetDirectory(0)
    
    return h_temp



def reweight(treevars, h_scale, option):

    variable = {'pt': 'reco_wbosonfromtop_pt_tag', 'met':'MET'}
    
    bin = h_scale.FindBin(treevars[variable[options.reweighting]])
    
    scale = h_scale.GetBinContent(b)

    return scale



def fillHistograms(histograms,file, process, options):

    rfile = ROOT.TFile(file,'read')

    printname = file.split("/")[-1].split('.')[1:3]
    printname = " ".join(printname)
    
    print "Running : ", repr(process).ljust(12), "sample: ", repr(printname).ljust(9),

    norm_lumi = 1.

    if options.region != 'ProtosRWT':
        norm_lumi = normalize_to_lumi(rfile, process)
    if options.analysis == 'migration':
        norm_lumi = 1.

    vars = load_treevars(options.analysis)

    # to optimize the reading of the ttree
    # we just activate the branches we need,
    # set the address of the branches to variables -> they are cached
    # and then stop the cache learning
    rtree = rfile.Get('ResultsDataTree')
    rtree.SetBranchStatus("*", 0)
    #rtree.SetCacheSize(12000000)

    for key in vars:
        if options.region != 'ttbar'  and key == 'eventPreSelectionBitSet':  continue 
        if options.region != 'ProtosRWT' and key == 'passed_AllSelection':  continue
        if options.region != 'wjets' and key == 'SF_loosejets':
            vars['SF_loosejets'][0] = 1.
            continue
        if options.region == 'ProtosRWT' and key == 'generatorWeight' :
            vars['generatorWeight'][0] = 1.
            continue

        rtree.SetBranchStatus(key,1)
        rtree.SetBranchAddress(key,vars[key])
    
    rtree.StopCacheLearningPhase()

    selectedentries    = 0
    preselectedentries = 0
    weighted_presel    = 0
    weighted_sel       = 0
    
    #bound fill method to improve performance:
    histostofill = {}
    try:    
        for k in histograms:
            histostofill[k] = histograms[k].Fill
    except:
        for k in histograms:
            histostofill[k] = {}
            for j in histograms[k]:
                histostofill[k][j] = histograms[k][j].Fill

    cuts = load_cuts(options.region)
    
    random = 0
    if options.analysis == 'closure':
        random = ROOT.TRandom3(0)
        random.SetSeed(0)
    
    h_SF = None
    
    if options.reweighting and process == 'wjets':
        h_SF = get_SF_histo(options, file)

    i = 0
    while rtree.GetEntry(i):

        if (int(options.Nevents) > 0) and (i >= int(options.Nevents)):
            print 'Stopping'
            break

        if options.verbose and (not i%100000) : print "entry ",i

        i += 1

        ################################
        ###
        ### if building migration matrix, you need to fill 
        ### all generated events!
        ###
        ################################
        
        random_choice = 0
        if options.analysis == 'migration'  : migration(vars,  histostofill, True)
        if options.analysis == 'efficiency' : efficiency(vars, histostofill, norm_lumi, True)
        if options.analysis == 'closure'    :
            random_choice = random.Gaus(0., 1.)
            closure(vars, histostofill, random_choice, electrons)

        ################################
        ###
        ### Now filter the events
        ###
        ################################
        
        if not pass_Preselection(vars, cuts, options.region) : continue
        preselectedentries +=1
        if not pass_Selection(vars, cuts, options.region)    : continue
        
        weightedevent = ComputeWeight(norm_lumi, vars, options.region)
        
        selectedentries += 1
        
        weighted_sel += weightedevent
        
        extraweight = 1.
        
        if options.reweighting and process == 'wjets': extraweight = reweight(vars, h_SF, options)
        
        weightedevent *= extraweight
        
        if   options.analysis == 'cut_study' : cuts_study(vars,   weightedevent, process, histostofill)
        elif options.analysis == 'get_angles': angular_dist(vars, weightedevent, process, histostofill, options.region)
        elif options.analysis == 'migration' : migration(vars,  histostofill, False)
        elif options.analysis == 'closure'   : closure(vars,    histostofill, random_choice, False)
        elif options.analysis == 'efficiency': efficiency(vars, histostofill, norm_lumi,     False)
        else: pass

    try:
        keys = histostofill.keys()
        for k in keys: del histostofill[k] 

    except:
        keys1 = histostofill.keys()
        for k in keys1:
            keys2 = histostofill[k].keys()
            for j in keys2: del histostofill[k][j]

    del histostofill

    rfile.Close()
    print 'Ran over:',repr(i).rjust(8),'After preselection: %i'%(preselectedentries),'After selection: %i'%(selectedentries)

    return weighted_presel, weighted_sel






if __name__ == '__main__':
    t0 = time()
    main()
    t1 = time()
    print "\nTotal time: %f min.\n" %((t1-t0)/60.)

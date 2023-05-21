import ROOT
from array import array
def save_histos(outputfilename, process, histo_dict, analysis, outputdir):

    if analysis == 'closure':
        for k in histo_dict:
            output = ROOT.TFile(outputdir+outputfilename+'_%s.root'%(k),'recreate')
            output.cd()
            keys = histo_dict[k].keys()
            for h in keys:
                histo_dict[k][h].Write()
                histo_dict[k][h].IsA().Destructor(histo_dict[k][h])
            output.Close()
        print "histograms for closure written!!"
        return
    
    if analysis == 'migration':

        output = ROOT.TFile(outputdir+outputfilename+'.root','recreate')
        output.cd()
        keys = histo_dict.keys()
        for h in keys:
            histo_dict[h].Write()
            histo_dict[h].IsA().Destructor(histo_dict[h])
        output.Close()
        print "histograms for closure written!!"
        return
        
    if analysis ==  'efficiency':
        
        output = ROOT.TFile(outputdir+outputfilename+'.root','recreate')
        output.cd()
        
        for h in ['cos_LN', 'cos_LT', 'cos_X', 'cos_S', 'cos_W']:
            histo_dict[h+'_generator'].Write()
            histo_dict[h+'_selection_truth'].Write()
            temp = histo_dict[h+'_selection_truth'].Clone(h+'_efficiency')
            temp.Divide(histo_dict[h+'_generator'])
            temp.Write()
        
        keys = histo_dict.keys()
        for h in keys:
            histo_dict[h].IsA().Destructor(histo_dict[h])
        
        output.Close()
        print "histograms for selection efficiency written!!"
        return
    
    output = ROOT.TFile(outputdir+outputfilename+'.root','recreate')
    output.mkdir('topPlots')
    output.cd('topPlots')

    try:
        initial_h = histo_dict.keys()
        for h in initial_h:
            #print 5*"HAS COMENTADO LA LINEA DE HACER STACKS PORQUE NO TE HACIAN FALTA... PERO AHORA PUEDE QUE SI\n"
            do_ratio = False
            #if 'data' in process: do_ratio = True
            if h in ['cos_LN', 'cos_LT', 'cos_X', 'cos_S', 'cos_W']: #, 'MET', 'MTW', 'kine_topmass_tag', 'DeltaPhiLepMET', 'reco_wbosonfromtop_pt_tag', 'reco_wbosonfromtop_eta_tag']:
                stackname = "h_"+h+"_2-jetbin_tag_Selection"
                make_stacks(histo_dict[h], process, output, stackname, do_ratio)
            else: pass
            
            keys = histo_dict[h].keys()
            for j in keys:
                histo_dict[h][j].IsA().Destructor(histo_dict[h][j])
        print "stacks done!!"

    except:
        keys = histo_dict.keys()
        for k in keys:
            histo_dict[k].Write()
            histo_dict[k].IsA().Destructor(histo_dict[k])
        print "histograms written!!"

    output.Close()


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

	#print "\n\nlen a:     ", len(process_a)
	#print "len b:       ", len(process_b)
	#print "len Tlist:   ", len(TList)
	#print "len process: ", len(process_list)

	histo_process = {}
	
	for i in range(len(TList)):
		histo_process[process_list[i]] = TList.At(i)


	return histo_process
	

def makeHistograms(htype, processlist, binning=0, binAsym=False):
    retval = { }
    ROOT.TH1.SetDefaultSumw2(True)
    ROOT.TH2.SetDefaultSumw2(True)
    
    nbins = {'cos_LN': 16, 'cos_LT': 16, 'cos_X': 8, 'cos_S': 12, 'cos_W': 12}
    
    if htype == 'efficiency': nbins = {'cos_LN': 16, 'cos_LT': 16, 'cos_X': 16, 'cos_S': 16, 'cos_W': 16}

    if (binAsym):
        for a in nbins: nbins[a]=4
        edges = array('f',[-1,-1*(pow(2.,2./3.)-1),0,(pow(2.,2./3.)-1),1])    

    elif int(binning) != 0:
	for a in nbins: nbins[a]= int(binning)
    if htype == 'cut_study':
    
        mass_cut  = ['mass130']#, 'mass140', 'mass150']
        ht_cut    = ['ht180']#['ht180', 'ht195', 'ht210']
        eta_light = ['eta100', 'eta110', 'eta125', 'eta140', 'eta155', 'eta170', 'eta185', 'eta200', 'eta215', 'eta230']
        delta     = ['delta085', 'delta100', 'delta110', 'delta125', 'delta140', 'delta155', 'delta170', 'delta185', 
                     'delta200', 'delta210', 'delta225']
        
        for m in mass_cut:
            for h in ht_cut:
                for e in eta_light:
                    for d in delta:
                        name = "_"+m+"_"+h+"_"+e+"_"+d
                        retval['signal'+name] = ROOT.TH1F('signal'+name, 'signal'+name, 3, 0., 2.)
                        retval['backgd'+name] = ROOT.TH1F('backgd'+name, 'backgd'+name, 3, 0., 2.)
                        for p in processlist:

                            retval[p+name+'_etalight']   = ROOT.TH1F(p+name+'_etalight' , "#eta(lightjet);#eta(lightjet);events",7,1.5,5.)
                            retval[p+name+'_HT']         = ROOT.TH1F(p+name+'_HT'       , "Ht;Ht;events", 42, 165.,800)
                            retval[p+name+'_deltaEta']   = ROOT.TH1F(p+name+'_deltaEta' , "#Delta#eta;#Delta#eta;events", 11, 0.5, 6.)
                            retval[p+name+'_masstop']    = ROOT.TH1F(p+name+'_masstop'  , "m(t);m(t);events", 9, 120.,210.)
                            retval[p+name+'_costhetaN']  = ROOT.TH1F(p+name+'_costhetaN', "cos#theta N;cos#theta N; events", 16, -1.,1.)
                            retval[p+name+'_costhetaX']  = ROOT.TH1F(p+name+'_costhetaX', "cos#theta X;cos#theta X; events", 16, -1.,1.)
                            retval[p+name+'_costhetaT']  = ROOT.TH1F(p+name+'_costhetaT', "cos#theta T;cos#theta T; events", 16, -1.,1.)
                            retval[p+name+'_costhetaS']  = ROOT.TH1F(p+name+'_costhetaS', "cos#theta S;cos#theta S; events", 16, -1.,1.)

    if htype == 'migration':
        if (binAsym): 
            for a in ['cos_LN', 'cos_LT', 'cos_X', 'cos_S', 'cos_W']:
                retval[a+'_generator']  = ROOT.TH1F(a+'_generator', ";"+a+'_generator;events', nbins[a], edges)
                retval[a+'_selection']  = ROOT.TH1F(a+'_selection', ";"+a+'_selection;events', nbins[a], edges)
                retval[a+'_resolution'] = ROOT.TH2F(a+'_resolution', ";"+a+'_resolution;events', nbins[a], edges, nbins[a], edges)
        else:
            for a in ['cos_LN', 'cos_LT', 'cos_X', 'cos_S', 'cos_W']:
                retval[a+'_generator']  = ROOT.TH1F(a+'_generator', ";"+a+'_generator;events', nbins[a], -1.,1.)
                retval[a+'_selection']  = ROOT.TH1F(a+'_selection', ";"+a+'_selection;events', nbins[a], -1.,1.)
                retval[a+'_resolution'] = ROOT.TH2F(a+'_resolution', ";"+a+'_resolution;events', nbins[a], -1., 1., nbins[a], -1., 1.)

    if htype == 'efficiency':
        if (binAsym):
            for a in ['cos_LN', 'cos_LT', 'cos_X', 'cos_S', 'cos_W']:
                retval[a+'_generator']  = ROOT.TH1F(a+'_generator', ";"+a+'_generator;events', nbins[a], edges)
                retval[a+'_selection_truth']  = ROOT.TH1F(a+'_selection_truth', ";"+a+'_selection;events', nbins[a], edges)
        else:
            for a in ['cos_LN', 'cos_LT', 'cos_X', 'cos_S', 'cos_W']:
                retval[a+'_generator']  = ROOT.TH1F(a+'_generator', ";"+a+'_generator;events', nbins[a], -1.,1.)
                retval[a+'_selection_truth']  = ROOT.TH1F(a+'_selection_truth', ";"+a+'_selection;events', nbins[a], -1.,1.)    

    if htype=='closure':
        retval = {'file1':{}, 'file2':{}}
        if (binAsym):
            for k in retval:
               for a in ['cos_LN', 'cos_LT', 'cos_X', 'cos_S', 'cos_W']:
                   retval[k][a+'_generator']  = ROOT.TH1F(a+'_generator_%s'%(k) , ";"+a+'_generator;events', nbins[a], edges)
                   retval[k][a+'_selection']  = ROOT.TH1F(a+'_selection_%s'%(k) , ";"+a+'_selection;events', nbins[a], edges)
                   retval[k][a+'_resolution'] = ROOT.TH2F(a+'_resolution_%s'%(k), ";"+a+'_resolution;events', nbins[a],edges, nbins[a], edges)
        else:
            for k in retval:
               for a in ['cos_LN', 'cos_LT', 'cos_X', 'cos_S', 'cos_W']:
                   retval[k][a+'_generator']  = ROOT.TH1F(a+'_generator_%s'%(k) , ";"+a+'_generator;events', nbins[a], -1.,1.)
                   retval[k][a+'_selection']  = ROOT.TH1F(a+'_selection_%s'%(k) , ";"+a+'_selection;events', nbins[a], -1.,1.)
                   retval[k][a+'_resolution'] = ROOT.TH2F(a+'_resolution_%s'%(k), ";"+a+'_resolution;events', nbins[a], -1., 1., nbins[a], -1., 1.)

    if htype == 'get_angles':
        
        for h in ['cos_LN', 'cos_LT', 'cos_X', 'cos_S', 'cos_W'] : retval[h] = {}
                
        for a in ['cos_LN', 'cos_LT', 'cos_X', 'cos_S', 'cos_W']:
            if (binAsym):
                for p in processlist:
                    retval[a][p] = ROOT.TH1F(a+"_"+p+'_selection', ";"+a+';events', nbins[a], edges)
            else:
                for p in processlist:
                    retval[a][p] = ROOT.TH1F(a+"_"+p+'_selection', ";"+a+';events', nbins[a], -1.,1.)

    try:
        for k in retval: retval[k].Sumw2(True)
    except:
        for k in retval:
            for j in retval[k]:
                retval[k][j].Sumw2(True)

    return retval


def make_stacks(histos_dict, process, outputfile, name, ratio=False):

    ROOT.TH1.SetDefaultSumw2(True)
    stack = ROOT.THStack(name+"_stack", name)

    colorlist = {'qcd'     : 618,
                 'top'     : 625,
                 'tchannel': 865,
                 'zdiboson': 801,
                 'wjets'   : 416}
    
    for p in process:
        if p == 'data': continue
        histos_dict[p].SetLineColor(colorlist[p])
        histos_dict[p].SetFillColor(colorlist[p])
        stack.Add(histos_dict[p])
    
    maximum_plot = 1.5*stack.GetMaximum()
    minimum_plot = 0.
    stack.SetMaximum(maximum_plot)
    stack.SetMinimum(minimum_plot)
    
    outputfile.cd('topPlots')
    stack.Write()

    if 'data' in process:
        temp = histos_dict['data'].Clone(name+'_data')
        temp.Write()

    stack.IsA().Destructor(stack)
    
    '''if ratio: 
        uncertainty = histos_dict['data'].Clone("uncertaintyertainy_%s"%(name))
        uncertainty.Reset("ICESM")
        uncertainty.Sumw2(True)
 
        for p in process:

            if p == 'data': pass
            elif p == 'qcd': pass
            else: uncertainty.Add(histos_dict[p])

        for i in range(1,uncertainty.GetNbinsX()+1):
            content = uncertainty.GetBinContent(i)
            error   = uncertainty.GetBinError(i)
            qcdcont = histos_dict['qcd'].GetBinContent(i)
            qcderr  = ROOT.TMath.Abs(0.5*qcdcont)
            #print "err: ",error," qcd err: ",qcderr," total: ", error+qcderr
            uncertainty.SetBinContent(i, content+qcdcont)
            uncertainty.SetBinError(i, error+qcderr)
            #print "finalerr: ",uncertainty.GetBinError(i)
        
        uncertainty.SetMarkerStyle(1)
        uncertainty.SetFillColor(1)
        uncertainty.SetLineColor(0)
        uncertainty.SetFillStyle(3256)
        uncertainty.GetXaxis().SetLabelColor(0)
        
        theLegend.AddEntry(uncertainty,"MC stat. + multijet uncertainty.","f")

        histos_dict['data'].SetLineColor(1)
        histos_dict['data'].SetMarkerStyle(20)
        histos_dict['data'].SetMarkerSize(0.8)
        theLegend.AddEntry(histos_dict[p],"Data","p")
        
        can = ROOT.TCanvas('ratiocanvas',"", 850, 800)
        #ROOT.gStyle.SetLegendBorderSize(0)
        
        data_mc  = histos_dict['data'].Clone("data_top")
        data_mc.Divide(uncertainty)
        data_mc.SetStats(False)
        line_one = histos_dict['data'].Clone("line_one")
        line_one.Divide(histos_dict['data'])
        line_one.SetStats(False)

        #error f=X/Y -> df = dX/Y + XdY/Y**2 -> dX/Y ->data_mc, XdY/Y**2 -> line_one
        for i in range(1, histos_dict['data'].GetNbinsX()+1):
            x  = histos_dict['data'].GetBinContent(i)
            dx = histos_dict['data'].GetBinError(i)
            y  = uncertainty.GetBinContent(i)
            dy = uncertainty.GetBinError(i)
            
            if x != 0. : data_mc.SetBinError(i,dx/y)
            else: data_mc.SetBinContent(i,0)
            if y != 0. : line_one.SetBinError(i, x*dy/(y*y))
            else: line_one.SetBinContent(i, 0.)
    
        pad1 = ROOT.TPad("pad1", 'pad1',0.0, 0.3, 1.0, 1.0, 0)
        pad1.SetTopMargin(0.08)
        pad1.SetBottomMargin(0.025)
        pad1.SetRightMargin(0.05)
        pad1.SetLeftMargin(0.15)
    
        pad2 = ROOT.TPad("pad2", 'pad2',0.0, 0.0, 1.0, 0.3, 0)
        pad2.SetTopMargin(0.04)
        pad2.SetBottomMargin(0.4)
        pad2.SetRightMargin(0.05)
        pad2.SetLeftMargin(0.15)
        
        pad1.Draw()
        pad2.Draw()
        
        pad1.cd()
        stack.SetTitle("")
        stack.SetMaximum(maximum_plot)
        stack.SetMinimum(minimum_plot)
        stack.Draw('HIST')
        uncertainty.GetXaxis().SetLabelColor(0)
        uncertainty.SetMaximum(maximum_plot)
        uncertainty.SetMinimum(minimum_plot)
        uncertainty.Draw('E2 SAME')
        histos_dict['data'].GetXaxis().SetLabelColor(0)
        histos_dict['data'].SetMaximum(maximum_plot)
        histos_dict['data'].SetMinimum(minimum_plot)
        histos_dict['data'].Draw('E1 X0 SAME')
        theLegend.Draw()
        ROOT.gPad.RedrawAxis()
        can.Update()
    
        pad2.cd()
        data_mc.SetMarkerSize(0.8)
        data_mc.SetMarkerStyle(8)
        data_mc.SetMarkerColor(1)
        data_mc.SetLineStyle(1)
        data_mc.SetLineColor(1)
        data_mc.GetYaxis().SetTitle("")
        data_mc.GetYaxis().SetTitleOffset(1.3)
        data_mc.GetYaxis().SetLabelSize(0.096)
        data_mc.GetYaxis().SetNdivisions(804)
        data_mc.GetYaxis().SetTickLength(0.05)
        data_mc.GetYaxis().SetRangeUser(0.6,1.4)
        data_mc.GetXaxis().SetLabelSize(0.096)
        data_mc.GetXaxis().SetTitleSize(0.096)
        data_mc.GetXaxis().SetLabelOffset(0.01)
        data_mc.GetXaxis().SetTickLength(0.07)
        data_mc.GetXaxis().SetLabelOffset(0.01)
        data_mc.GetXaxis().SetLabelColor(1)
        data_mc.Draw("AXIS")

        line = ROOT.TLine()
        line.SetLineStyle(2)
        line.SetLineColor(2)
        line.DrawLine(data_mc.GetXaxis().GetXmin(), 1., data_mc.GetXaxis().GetXmax(), 1.)

        line_one.SetMarkerStyle(8)
        line_one.SetMarkerSize(0.)
        line_one.SetFillColor(1)
        line_one.SetLineColor(0)
        line_one.SetFillStyle(3256)
        line_one.GetYaxis().SetRangeUser(0.8,1.2)
        line_one.SetTitle(";;;")
        line_one.Draw("L E2 SAME")

        data_mc.Draw("E1 X0 SAME")

        
    
        can.Update()
        can.SaveAs(name+".eps", 'eps')        
        print "despues eps"
        data_mc.IsA().Destructor(data_mc)
        line_one.IsA().Destructor(line_one)
        can.IsA().Destructor(can)
        print "todo destruido"
        del data_mc
        del line_one
        del can'''


    






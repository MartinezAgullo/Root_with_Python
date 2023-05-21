

def load_cuts(region):

    if region == 'cut_study' :
        cuts = {'preselection': 131071,
                'delta_eta': 0.85,
                'eta_ljet' : 1.0,
                'ht'       : 180.,
                'top_low'  : 130.,
                'top_up'   : 200.}
        return cuts
    
    if region == 'signal' :
        cuts = {'preselection': 32767,
                'delta_eta'   : 4.5,
                'eta_ljet'    : 3.6,
                'selection'   : 15}
        return cuts
    
    if region == 'ttbar' :
        cuts = {'preselection': 32767,
                'delta_eta'   : 4.5,
                'eta_ljet'    : 3.6,
                'nGoodJets'   : 4}
        return cuts
    
    if region == 'highmass' :
       cuts = {'preselection': 131071,
               'top_low'     : 230.}
       return cuts
       
    if region == 'wjets' :
        cuts = {'preselection'   : 20479,# 20479,#32767
                'delta_eta'      : 4.5,
                'eta_ljet'       : 3.6,
                'nGoodLooseBJets': 1}
        return cuts
        
    if region == 'ProtosRWT':
        cuts = {'preselection': 1}
        return cuts
        
    if region == 'custom':
        cuts = {'preselection': 131071,
                'delta_eta': 1.50,
                'eta_ljet' : 2.00,
                'ht'       : 195.,
                'top_low'  : 130.,
                'top_up'   : 200.}
        return cuts



def pass_Preselection(treevars, cutdict, region):
    
    if region == 'cut_study':
        if treevars['eventPreSelectionBitSet2jetbin'][0] != cutdict['preselection'] : return False
        if treevars['kine_eta_lightjet_tag'][0] > 3.6: return False
        if treevars['kine_dEtaLightJetBJet'][0] > 4.5: return False
        return True
    
    if region == 'custom':
        if treevars['eventPreSelectionBitSet2jetbin'][0] != cutdict['preselection'] : return False
        if treevars['kine_eta_lightjet_tag'][0] > 3.6: return False
        if treevars['kine_dEtaLightJetBJet'][0] > 4.5: return False
        return True
    
    if region == 'signal':
        if treevars['eventPreSelectionBitSet2jetbin'][0] != cutdict['preselection'] : return False
        if treevars['kine_dEtaLightJetBJet'][0] >= cutdict['delta_eta'] : return False
        if treevars['kine_eta_lightjet_tag'][0] >= cutdict['eta_ljet']  : return False
        return True
    
    if region == 'wjets':
        #if treevars['eventPreSelectionBitSet2jetbin'][0] != cutdict['preselection'] : return False
        #if treevars['DeltaEtaLooseJets'][0] != cutdict['delta_eta'] : return False
        #if treevars['EtaLooseLightJet'][0] != cutdict['eta_ljet']   : return False
        return True
        
    if region == 'ttbar':
        if treevars['eventPreSelectionBitSet'][0] != cutdict['preselection'] : return False
        if treevars['kine_dEtaLightJetBJet'][0] >= cutdict['delta_eta'] : return False
        if treevars['kine_eta_lightjet_tag'][0] >= cutdict['eta_ljet']  : return False
        return True
    
    return True



def pass_Selection(treevars, cutdict, region):

    if region =='ProtosRWT':
    
        if treevars['passed_AllSelection'][0] == 1: return True
        
        return False

    if region == 'ttbar' :

        if treevars['nGoodJets'][0] == cutdict['nGoodJets']: return True

        return False
        
    if region == 'highmass':

        if treevars['kine_topmass_tag'][0] < cutdict['top_low']: return False
        
        return True
    
    if region == 'wjets':
    
        if treevars['nGoodLooseBJets'][0] == cutdict['nGoodLooseBJets'] : return True
        
        return False
    
    if region == 'signal' :
        
        if treevars['eventSelectionBitSet'].at(1) == cutdict['selection'] : return True
        
        return False
    
    if region == 'cut_study':
    
        if treevars['kine_dEtaLightJetBJet'][0] <= cutdict['delta_eta'] : return False
        if treevars['kine_eta_lightjet_tag'][0] <= cutdict['eta_ljet']  : return False
        if treevars['kine_ht_tag'][0]      <= cutdict['ht']             : return False
        if treevars['kine_topmass_tag'][0] <= cutdict['top_low']        : return False
        if treevars['kine_topmass_tag'][0] >= cutdict['top_up']         : return False

        return True
        
    if region == 'custom':
        if treevars['kine_dEtaLightJetBJet'][0] <= cutdict['delta_eta'] : return False
        if treevars['kine_eta_lightjet_tag'][0] <= cutdict['eta_ljet']  : return False
        if treevars['kine_ht_tag'][0]      <= cutdict['ht']             : return False
        if treevars['kine_topmass_tag'][0] <= cutdict['top_low']        : return False
        if treevars['kine_topmass_tag'][0] >= cutdict['top_up']         : return False

        return True
    
    print "You shouldn't be here, something wrong with the selected region"
    
    return False



def cuts_study(treevars, finalweight, process, histostofill):

    # all combinations
    for  mt in [130.]:#, 140., 150.]:
        for ht in [180.]:#[ 180., 195., 210.]:
            for e in [1.0, 1.10, 1.25, 1.40, 1.55, 1.70, 1.85, 2.0, 2.15, 2.30]:
                for d in [0.85, 1.0, 1.10, 1.25, 1.40, 1.55, 1.70, 1.85, 2.0, 2.10, 2.25]:
                    
                    name = '_mass%i_ht%i_eta%.2f_delta%.2f'%(mt, ht, e, d)
                    name = name.replace(".","")
                    
                    if (treevars['kine_topmass_tag'][0] > mt) and (treevars['kine_ht_tag'][0] > ht) and (treevars['kine_eta_lightjet_tag'][0] > e) and (treevars['kine_dEtaLightJetBJet'][0] > d):

                        if process == 'tchannel': histostofill['signal'+name](1., finalweight)
                        elif process == 'data'  : pass
                        else:                    histostofill['backgd'+name](1.,  finalweight)

                        histostofill[process+name+'_etalight'](treevars['kine_eta_lightjet_tag'][0],finalweight)
                        histostofill[process+name+'_HT'](treevars['kine_ht_tag'][0],finalweight)
                        histostofill[process+name+'_deltaEta'](treevars['kine_dEtaLightJetBJet'][0],finalweight)
                        histostofill[process+name+'_masstop'](treevars['kine_topmass_tag'][0],  finalweight)
                        histostofill[process+name+'_costhetaN'](treevars['reco_tag_cos_LN'][0], finalweight)
                        histostofill[process+name+'_costhetaX'](treevars['reco_tag_cos_X'][0],  finalweight)
                        histostofill[process+name+'_costhetaT'](treevars['reco_tag_cos_LT'][0], finalweight)
                        histostofill[process+name+'_costhetaS'](treevars['reco_tag_cos_S'][0],  finalweight)



def migration(treevars, histostofill, generator):

    if abs(treevars['gen_cos_LN'][0]) > 1.: return
    
    if generator:
        histostofill['cos_LN_generator'](treevars['gen_cos_LN'][0], treevars['generatorWeight'][0])
        histostofill['cos_LT_generator'](treevars['gen_cos_LT'][0], treevars['generatorWeight'][0])
        histostofill['cos_X_generator'](treevars['gen_cos_X'][0],   treevars['generatorWeight'][0])
        histostofill['cos_S_generator'](treevars['gen_cos_S'][0],   treevars['generatorWeight'][0])
        histostofill['cos_W_generator'](treevars['gen_cos_W'][0],   treevars['generatorWeight'][0])

    else:
        histostofill['cos_LN_selection'](treevars['reco_tag_cos_LN'][0], treevars['combinedWeight'][0])
        histostofill['cos_LT_selection'](treevars['reco_tag_cos_LT'][0], treevars['combinedWeight'][0])
        histostofill['cos_X_selection'](treevars['reco_tag_cos_X'][0],   treevars['combinedWeight'][0])
        histostofill['cos_S_selection'](treevars['reco_tag_cos_S'][0],   treevars['combinedWeight'][0])
        histostofill['cos_W_selection'](treevars['reco_tag_cos_W'][0],   treevars['combinedWeight'][0])
        
        histostofill['cos_LN_resolution'](treevars['reco_tag_cos_LN'][0], treevars['gen_cos_LN'][0], treevars['combinedWeight'][0])
        histostofill['cos_LT_resolution'](treevars['reco_tag_cos_LT'][0], treevars['gen_cos_LT'][0], treevars['combinedWeight'][0])
        histostofill['cos_X_resolution'](treevars['reco_tag_cos_X'][0],   treevars['gen_cos_X'][0],  treevars['combinedWeight'][0])
        histostofill['cos_S_resolution'](treevars['reco_tag_cos_S'][0],   treevars['gen_cos_S'][0],  treevars['combinedWeight'][0])
        histostofill['cos_W_resolution'](treevars['reco_tag_cos_W'][0],   treevars['gen_cos_W'][0],  treevars['combinedWeight'][0])


def closure(treevars, histostofill, random, generator):

    if abs(treevars['gen_cos_LN'][0]) > 1.: return
    
    if random > 0.:
        if generator:
            histostofill['file1']['cos_LN_generator'](treevars['gen_cos_LN'][0], treevars['generatorWeight'][0])
            histostofill['file1']['cos_LT_generator'](treevars['gen_cos_LT'][0], treevars['generatorWeight'][0])
            histostofill['file1']['cos_X_generator'](treevars['gen_cos_X'][0],   treevars['generatorWeight'][0])
            histostofill['file1']['cos_S_generator'](treevars['gen_cos_S'][0],   treevars['generatorWeight'][0])
            histostofill['file1']['cos_W_generator'](treevars['gen_cos_W'][0],   treevars['generatorWeight'][0])

        else:
            histostofill['file1']['cos_LN_selection'](treevars['reco_tag_cos_LN'][0], treevars['combinedWeight'][0])
            histostofill['file1']['cos_LT_selection'](treevars['reco_tag_cos_LT'][0], treevars['combinedWeight'][0])
            histostofill['file1']['cos_X_selection'](treevars['reco_tag_cos_X'][0],   treevars['combinedWeight'][0])
            histostofill['file1']['cos_S_selection'](treevars['reco_tag_cos_S'][0],   treevars['combinedWeight'][0])
            histostofill['file1']['cos_W_selection'](treevars['reco_tag_cos_W'][0],   treevars['combinedWeight'][0])
        
            histostofill['file1']['cos_LN_resolution'](treevars['reco_tag_cos_LN'][0], treevars['gen_cos_LN'][0], treevars['combinedWeight'][0])
            histostofill['file1']['cos_LT_resolution'](treevars['reco_tag_cos_LT'][0], treevars['gen_cos_LT'][0], treevars['combinedWeight'][0])
            histostofill['file1']['cos_X_resolution'](treevars['reco_tag_cos_X'][0],   treevars['gen_cos_X'][0],  treevars['combinedWeight'][0])
            histostofill['file1']['cos_S_resolution'](treevars['reco_tag_cos_S'][0],   treevars['gen_cos_S'][0],  treevars['combinedWeight'][0])
            histostofill['file1']['cos_W_resolution'](treevars['reco_tag_cos_W'][0],   treevars['gen_cos_W'][0],  treevars['combinedWeight'][0])

    else:
        if generator:
            histostofill['file2']['cos_LN_generator'](treevars['gen_cos_LN'][0], treevars['generatorWeight'][0])
            histostofill['file2']['cos_LT_generator'](treevars['gen_cos_LT'][0], treevars['generatorWeight'][0])
            histostofill['file2']['cos_X_generator'](treevars['gen_cos_X'][0],   treevars['generatorWeight'][0])
            histostofill['file2']['cos_S_generator'](treevars['gen_cos_S'][0],   treevars['generatorWeight'][0])
            histostofill['file2']['cos_W_generator'](treevars['gen_cos_W'][0],   treevars['generatorWeight'][0])

        else:

            histostofill['file2']['cos_LN_selection'](treevars['reco_tag_cos_LN'][0], treevars['combinedWeight'][0])
            histostofill['file2']['cos_LT_selection'](treevars['reco_tag_cos_LT'][0], treevars['combinedWeight'][0])
            histostofill['file2']['cos_X_selection'](treevars['reco_tag_cos_X'][0],   treevars['combinedWeight'][0])
            histostofill['file2']['cos_S_selection'](treevars['reco_tag_cos_S'][0],   treevars['combinedWeight'][0])
            histostofill['file2']['cos_W_selection'](treevars['reco_tag_cos_W'][0],   treevars['combinedWeight'][0])
        
            histostofill['file2']['cos_LN_resolution'](treevars['reco_tag_cos_LN'][0], treevars['gen_cos_LN'][0], treevars['combinedWeight'][0])
            histostofill['file2']['cos_LT_resolution'](treevars['reco_tag_cos_LT'][0], treevars['gen_cos_LT'][0], treevars['combinedWeight'][0])
            histostofill['file2']['cos_X_resolution'](treevars['reco_tag_cos_X'][0],   treevars['gen_cos_X'][0],  treevars['combinedWeight'][0])
            histostofill['file2']['cos_S_resolution'](treevars['reco_tag_cos_S'][0],   treevars['gen_cos_S'][0],  treevars['combinedWeight'][0])
            histostofill['file2']['cos_W_resolution'](treevars['reco_tag_cos_W'][0],   treevars['gen_cos_W'][0],  treevars['combinedWeight'][0])


def angular_dist(treevars, finalweight, process, histostofill, region):

    key = 'reco_tag_'
    if region == 'wjets': key = 'reco_pretag_'
    
    histostofill['cos_LN'][process](treevars[key+'cos_LN'][0], finalweight)
    histostofill['cos_LT'][process](treevars[key+'cos_LT'][0], finalweight)
    histostofill['cos_X'][process](treevars[key+'cos_X'][0],   finalweight)
    histostofill['cos_S'][process](treevars[key+'cos_S'][0],   finalweight)
    histostofill['cos_W'][process](treevars[key+'cos_W'][0],   finalweight)
    
    
def efficiency(treevars, histostofill, luminosity, beforeselection):
    
    if abs(treevars['gen_cos_LN'][0]) > 1.: return

    if beforeselection :
        histostofill['cos_LN_generator'](treevars['gen_cos_LN'][0], luminosity*treevars['generatorWeight'][0])
        histostofill['cos_LT_generator'](treevars['gen_cos_LT'][0], luminosity*treevars['generatorWeight'][0])
        histostofill['cos_X_generator'](treevars['gen_cos_X'][0],   luminosity*treevars['generatorWeight'][0])
        histostofill['cos_S_generator'](treevars['gen_cos_S'][0],   luminosity*treevars['generatorWeight'][0])
        histostofill['cos_W_generator'](treevars['gen_cos_W'][0],   luminosity*treevars['generatorWeight'][0])

    else:
        histostofill['cos_LN_selection_truth'](treevars['gen_cos_LN'][0], luminosity*treevars['generatorWeight'][0])
        histostofill['cos_LT_selection_truth'](treevars['gen_cos_LT'][0], luminosity*treevars['generatorWeight'][0])
        histostofill['cos_X_selection_truth'](treevars['gen_cos_X'][0],   luminosity*treevars['generatorWeight'][0])
        histostofill['cos_S_selection_truth'](treevars['gen_cos_S'][0],   luminosity*treevars['generatorWeight'][0])
        histostofill['cos_W_selection_truth'](treevars['gen_cos_W'][0],   luminosity*treevars['generatorWeight'][0])
    
    



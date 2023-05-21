#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
from array import array

def load_treevars(analysis):
    
    if analysis == 'cut_study' :
    
        treevars = {
            'eventPreSelectionBitSet2jetbin' : array('i',[0]),
            'kine_dEtaLightJetBJet'  : array('f',[0.]),
            'kine_ht_tag'            : array('f',[0.]),
            'kine_topmass_tag'       : array('f',[0.]),
            'kine_eta_lightjet_tag'  : array('f',[0.]),
            'combinedWeight'         : array('d',[0.]),
            'matrixMethodWeights'    : ROOT.vector('float')(),
            'reco_tag_cos_LN'        : array('f',[0.]),
            'reco_tag_cos_LT'        : array('f',[0.]),
            'reco_tag_cos_X'         : array('f',[0.]),
            'reco_tag_cos_S'         : array('f',[0.])
            }
            
        return treevars

    if analysis == 'get_angles':
                             
        treevars = {
            'eventPreSelectionBitSet2jetbin' : array('i',[0]),
            'eventPreSelectionBitSet'   : array('i',[0]),
            'eventSelectionBitSet'      : ROOT.vector('int')(),
            'kine_eta_lightjet_tag'     : array('f',[0.]),
            'kine_dEtaLightJetBJet'     : array('f',[0.]),
            'DeltaEtaLooseJets'         : array('f',[0.]),
            'EtaLooseLightJet'          : array('f',[0.]),
            'nGoodJets'                 : array('i',[0]),
            'nGoodLooseBJets'           : array('i',[0]),
            'combinedWeight'            : array('d',[0.]),
            'combinedWeightForPretag'   : array('d',[0.]),
            'SF_loosejets'              : array('d',[0.]),
            'matrixMethodWeights'       : ROOT.vector('float')(),
            'reco_tag_cos_LN'           : array('f',[0.]),
            'reco_tag_cos_LT'           : array('f',[0.]),
            'reco_tag_cos_X'            : array('f',[0.]),
            'reco_tag_cos_W'            : array('f',[0.]),
            'reco_tag_cos_S'            : array('f',[0.]),
            'reco_pretag_cos_LN'        : array('f',[0.]),
            'reco_pretag_cos_LT'        : array('f',[0.]),
            'reco_pretag_cos_X'         : array('f',[0.]),
            'reco_pretag_cos_W'         : array('f',[0.]),
            'reco_pretag_cos_S'         : array('f',[0.])
            }

        return treevars

    if analysis in ['migration', 'closure', 'efficiency']:
        treevars = {
            'eventPreSelectionBitSet2jetbin' : array('i',[0]),
            'eventSelectionBitSet'   : ROOT.vector('int')(),
            'passed_AllSelection'    : array('i',[0]),
            'combinedWeight'         : array('d',[0.]),
            'generatorWeight'        : array('d',[0.]),
            'matrixMethodWeights'    : ROOT.vector('float')(),
            'gen_cos_LN' : array('f',[0.]),
            'gen_cos_LT' : array('f',[0.]),
            'gen_cos_X'  : array('f',[0.]),
            'gen_cos_S'  : array('f',[0.]),
            'gen_cos_W'  : array('f',[0.]),
            'reco_tag_cos_LN': array('f',[0.]),
            'reco_tag_cos_LT': array('f',[0.]),
            'reco_tag_cos_X' : array('f',[0.]),
            'reco_tag_cos_S' : array('f',[0.]),
            'reco_tag_cos_W' : array('f',[0.])
            }
        return treevars

#########
##  Plots_for_fold_dileptau.py :: Draws the BDT socres for all the folds simultaneously
#######

import os
import sys
import matplotlib
matplotlib.use('Agg') # Bypass the need to install Tkinter GUI framework
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.offsetbox import AnchoredText
import numpy as np

sys.path.append("../tHqUtils")
from Reader import Root2Df

lumi = 140
Channel = "OS"
BDT = "tHq"

if Channel == "OS":
    dir_path_n = '/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/EBreview_v34_dilepOStau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV_BDT_tHq_ttbar/nominal_Loose/'
    TreeName = 'tHqLoop_nominal_Loose'
    branches = ['bdt_tHq', 'bdt_ttbar', 'weight_nominalWtau', 'eventNumber', 'mcChannelNumber']
    text = r'$\sqrt{s}=13\ \mathrm{TeV},\ 140\ \mathrm{fb}^{-1}$' + '\n' + r'$tHq(2\ell\mathrm{OS} + \tau_{\mathrm{had}})$ channel' + '\n' + 'Pre-selection' + '\n' + 'Pre-Fit'

if Channel == "SS":
    dir_path_n = '/lustre/ific.uv.es/grid/atlas/t3/pamarag/tHq_analysis/13TeV/EBreview_v34_dilepSStau_PLIV_SFs_syst_BDTassignment_lep3_pt_min14GeV_BDT_tHq/nominal_Loose/'
    TreeName = 'tHqLoop_nominal_Loose'
    branches = ['bdt_tHq', 'weight_nominalWtau', 'eventNumber', 'mcChannelNumber']
    text = r'$\sqrt{s}=13\ \mathrm{TeV},\ 140\ \mathrm{fb}^{-1}$' + '\n' + r'$tHq(2\ell\mathrm{SS} + \tau_{\mathrm{had}})$ channel' + '\n' + 'Pre-selection' + '\n' + 'Pre-Fit'


df = Root2Df(dir_path_n, TreeName, branches, exclude='AllYear')

bins = np.linspace(0., 1., 11)
fig, ax = plt.subplots(figsize=(5, 5))
width = 0.05

folds = range(5)  # Iterate over the folds
colors = ['C0', 'C1', 'C2', 'C3', 'C4']

for fold in folds:
    print("Ploting BDT for Fold "+str(fold))
    if BDT == "tHq": 
        df_0 = df[df['eventNumber'] % 5 == fold][['bdt_tHq', 'weight_nominalWtau']]
        hist = ax.hist(df_0['bdt_tHq'], bins, histtype='step', label='k={}'.format(fold), weights=df_0['weight_nominalWtau'] * lumi, color=colors[fold], density=True) # Plot the histogram
    if BDT == "ttbar":
        df_0 = df[df['eventNumber'] % 5 == fold][['bdt_ttbar', 'weight_nominalWtau']]
        hist = ax.hist(df_0['bdt_ttbar'], bins, histtype='step', label='k={}'.format(fold), weights=df_0['weight_nominalWtau'] * lumi, color=colors[fold], density=True)
    binEdges = hist[1]
    bin_centers = 0.5 * (binEdges[1:] + binEdges[:-1])

    weighted_mean = np.average(bin_centers, weights=hist[0]) # Calculate the weighted mean 
    weighted_std = np.sqrt(np.average((bin_centers - weighted_mean) ** 2, weights=hist[0])) # Calculate the weighted standard deviation 
    ax.errorbar(bin_centers, hist[0], yerr=weighted_std, fmt='none', ecolor=colors[fold]) # Plot the error bars  


handles, labels = ax.get_legend_handles_labels()
legend_title = 'Fold:'
ax.legend(handles, labels, title=legend_title, loc='upper right')

plt.xlim(0., 1.)
if BDT == "ttbar":plt.ylim(0., 6.)
if BDT == "tHq": plt.ylim(0., 12.)
ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

at = AnchoredText(text, loc='upper left', prop=dict(size=15), borderpad=0., frameon=False)
ax.add_artist(at)
if BDT == "tHq": ax.set_xlabel('BDT($tHq$)')
if BDT == "ttbar": ax.set_xlabel('BDT$(t\\bar{t})$')
ax.set_ylabel('Events')

if BDT == "tHq":
    plt.savefig('test_fold_tHq_2L_OS_1Tau_tHq.png')
    plt.savefig('test_fold_tHq_2L_OS_1Tau_tHq.pdf')
if BDT == "ttbar":
    plt.savefig('test_fold_tHq_2L_OS_1Tau_ttbar.png')
    plt.savefig('test_fold_tHq_2L_OS_1Tau_ttbar.pdf')
plt.close()


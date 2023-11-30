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

print("BDT("+str(BDT)+"|"+str(Channel)+")")

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
# fig, ax = plt.subplots(figsize=(5, 5)) #single panel
#fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 10))  # Two panels
#fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 10), gridspec_kw={'height_ratios': [3, 1]})  # Adjusting subplot sizes
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 8), gridspec_kw={'height_ratios': [3, 1]})



width = 0.05

folds = range(5)  # Iterate over the folds
colors = ['C0', 'C1', 'C2', 'C3', 'C4']

# Store histogram for fold=0
fold_0_hist = None # for lower pannel

###
# Main Loop
###
for fold in folds:
    print("Ploting BDT for Fold "+str(fold))
    if BDT == "tHq": 
        df_0 = df[df['eventNumber'] % 5 == fold][['bdt_tHq', 'weight_nominalWtau']]
        hist = ax1.hist(df_0['bdt_tHq'], bins, histtype='step', label='k={}'.format(fold), weights=df_0['weight_nominalWtau'] * lumi, color=colors[fold], density=True) # Plot the histogram
        #counts, bin_edges = np.histogram(df_0['bdt_tHq'], bins=bins, weights=df_0['weight_nominalWtau'] * lumi)
        
    if BDT == "ttbar":
        df_0 = df[df['eventNumber'] % 5 == fold][['bdt_ttbar', 'weight_nominalWtau']]
        hist = ax1.hist(df_0['bdt_ttbar'], bins, histtype='step', label='k={}'.format(fold), weights=df_0['weight_nominalWtau'] * lumi, color=colors[fold], density=True)
        #counts, bin_edges = np.histogram(df_0['bdt_ttbar'], bins=bins, weights=df_0['weight_nominalWtau'] * lumi)

    #counts_normalized = counts / counts.sum() 
    #ax1.step(bin_edges[:-1], counts_normalized, where='mid', label='k={}'.format(fold), color=colors[fold])
        
    binEdges = hist[1]
    bin_centers = 0.5 * (binEdges[1:] + binEdges[:-1])

    weighted_mean = np.average(bin_centers, weights=hist[0]) # Calculate the weighted mean 
    weighted_std = np.sqrt(np.average((bin_centers - weighted_mean) ** 2, weights=hist[0])) # Calculate the weighted standard deviation 
    ax1.errorbar(bin_centers, hist[0], yerr=weighted_std, fmt='none', ecolor=colors[fold]) # Plot the error bars  

    # For lower panel:
    # Calculate and plot ratio for fold != 0
    if fold == 0:
        fold_0_hist = hist[0]  # Store histogram of fold=0 // hist[0] is the current fold
        #fold_0_err = weighted_std
        fold_0_std = weighted_std 
    else:
        # Calculate the ratio
        ratio = hist[0] / fold_0_hist
        valid = fold_0_hist > 0
        # Uncertainty  of the ratio
        #ratio_err = ratio * (1-((weighted_std/hist[0])+(fold_0_err/fold_0_hist)))
        #ratio_error = ratio * np.sqrt((weighted_std/hist[0])**2 + (fold_0_std/fold_0_hist)**2) # Propagacion errores  
        ratio_error = ratio * ( (fold_0_std/fold_0_hist) + (weighted_std/hist[0] ) ) # Propagacion errores
        ax2.errorbar(bin_centers[valid], ratio[valid], yerr=ratio_error[valid], fmt='o', color=colors[fold], label="Fold "+str(fold)+" / Fold 0")
        ax2.plot(bin_centers[valid], ratio[valid], label="Fold "+str(fold)+" / Fold 0", color=colors[fold])


print("The error bars int he top panel correspond to the weighted standard deviation. Using the weights corrected with the tau-missID SFs.")
print("The error vars in the lower panel represent the uncertainty in the ratio of the histogram values of a given fold to those of fold 0. The error of this ratio is calculated using error propagation rules, considering the uncertainties in both the numerator (current fold's histogram) and the denominator (fold 0's histogram). " )

# Formatting the top panel
ax1.set_ylabel('Events')
ax1.legend(title='Fold:', loc='upper right')
ax1.set_xlim(0., 1.)
if BDT == "ttbar":
    ax1.set_ylim(0., 6.)
if BDT == "tHq":
    ax1.set_yscale('log')
    ax1.set_ylim(0.1, 12.)
at = AnchoredText(text, loc='upper left', prop=dict(size=15), borderpad=0., frameon=False)
ax1.add_artist(at)

# Formatting the lower panel
ax2.set_xlabel('BDT Score')
ax2.set_ylabel('Fold k / Fold 0')
#ax2.legend()
ax2.xaxis.set_minor_locator(ticker.AutoMinorLocator())

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(hspace=0.1) #space betwen panels

# Save the plot
plt.savefig('test_fold_tHq_2L_with_ratio_{}_{}.png'.format(Channel, BDT))
plt.savefig('test_fold_tHq_2L_with_ratio_{}_{}.pdf'.format(Channel, BDT))
plt.close()


# Single Panel
exit()
handles, labels = ax.get_legend_handles_labels()
legend_title = 'Fold:'
ax.legend(handles, labels, title=legend_title, loc='upper right')

plt.xlim(0., 1.)
if BDT == "ttbar":
    plt.ylim(0., 6.)
if BDT == "tHq":
    ax.set_yscale('log')  # Set logarithmic scale
    plt.ylim(0.1, 12.)
    ax.set_ylim(bottom=0.1) 
ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
#ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
#ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

at = AnchoredText(text, loc='upper left', prop=dict(size=15), borderpad=0., frameon=False)
ax.add_artist(at)
if BDT == "tHq": ax.set_xlabel('BDT($tHq$)')
if BDT == "ttbar": ax.set_xlabel('BDT$(t\bar{t})$')
ax.set_ylabel('Events')

if BDT == "tHq":
    plt.savefig('test_fold_tHq_2L_'+str(Channel)+'_1Tau_tHq.png')
    plt.savefig('test_fold_tHq_2L_'+str(Channel)+'_1Tau_tHq.pdf')
if BDT == "ttbar":
    plt.savefig('test_fold_tHq_2L_'+str(Channel)+'_1Tau_ttbar.png')
    plt.savefig('test_fold_tHq_2L_'+str(Channel)+'_1Tau_ttbar.pdf')
plt.close()

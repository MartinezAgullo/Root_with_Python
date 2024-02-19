###############################################################
#   TMVA_DrawCurvesROC
###################################################################

import os,sys
try:
    import ROOT
except:
    print("import ROOT Failed")
    print("Version of Python used:: " +str(sys.version))
    exit()


def get_roc_curve(i):
    # Open TFile
    root_file =  "BDTG_fold"+str(i)+".root"
    file = ROOT.TFile.Open(root_file)
    print(dir(file))
    if not file or file.IsZombie():
        print(f"Error opening file {root_file}")
        return None
    

    # Move to dataset TDirectory within the TFile
    dir_dataset = file.Get("dataset/Method_BDT/BDTG_fold"+str(i))
    #if not dir_dataset:
    #    print("Directory not found")
   #     return
    print(dir_dataset)
    #MVA_BDTG_fold_rejBvsS
    dir_dataset.Get("MVA_BDTG_fold_rejBvsS")
    return.Clone()  # Clone the curve to avoid issues when the file is closed

def plot_roc_curves(roc_curves):
    """
    Plot multiple ROC curves on the same canvas.
    """
    canvas = ROOT.TCanvas("canvas", "ROC Curves", 800, 600)
    legend = ROOT.TLegend(0.1, 0.7, 0.4, 0.9)

    for i, roc_curve in enumerate(roc_curves):
        roc_curve.SetLineColor(i + 1)  # Set different color for each curve
        roc_curve.SetTitle(f"Fold {i+1}")
        legend.AddEntry(roc_curve, f"Fold {i+1}", "l")

        draw_option = "L" if i > 0 else "AL"
        roc_curve.Draw(draw_option)

    legend.Draw()
    canvas.Update()
    canvas.SaveAs("combined_roc_curves.png")

def main():
    #tree_paths = [f"dataset/Method_BDTG/BDTG_fold{i}" for i in range(1, 4)]
    
    roc_curves = []
    i = 0
    while i < 4:
        i = i+1
        print(f"Reading BDTG_fold{i}.root" )
        roc_curve = get_roc_curve(i)
        if roc_curve:
            roc_curves.append(roc_curve)
    
    if roc_curves:
        plot_roc_curves(roc_curves)

if __name__ == "__main__":
    main()



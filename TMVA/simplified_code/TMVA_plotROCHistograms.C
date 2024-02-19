//##############################################################
//   TMVA_plotROCHistograms
//      Plot ROC curves from the different folds
//      root -l -q  /Users/pablo/Desktop/tHq_Analysis/2-LeptonAssigment/Studies/Simplified/plotHistograms.C
//##############################################################
#include <TFile.h>
#include <TH1D.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <TDirectoryFile.h>

void TMVA_plotROCHistograms() {
    std::cout << "TMVA :: ROC Plotter " << std::endl;
    TCanvas *c1 = new TCanvas("c1", "Histograms", 800, 600);
    TLegend *legend = new TLegend(0.7, 0.7, 0.9, 0.9);

    // Colors for the histograms
    int colors[] = {kRed, kBlue, kGreen, kBlack};
    
    std::cout << "TMVA :: Looping over folds " << std::endl;
    for (int i = 1; i <= 4; ++i) {
        std::cout << "Reding fold: " << i << std::endl;
        // Construct the file and histogram names
        TString fileName = Form("BDTG_fold%d.root", i);

        // Open the ROOT file
        TFile *file = TFile::Open(fileName);
        if (!file || file->IsZombie()) {
            std::cout << "Error opening file: " << fileName << std::endl;
            continue;
        }

        // Navigate to the TDirectoryFile and then retrieve the histogram
        TDirectoryFile *dirDataset = (TDirectoryFile*)file->Get("dataset");
        TDirectoryFile *dirMethodBDT = (TDirectoryFile*)dirDataset->Get("Method_BDT");
        TDirectoryFile *dirFold = (TDirectoryFile*)dirMethodBDT->Get(Form("BDTG_fold%d", i));
        TH1D *histo = (TH1D*)dirFold->Get(Form("MVA_BDTG_fold%d_rejBvsS", i));
        
        if (!dirDataset) {
            std::cout << "Directory 'dataset' not found in file: " << fileName << std::endl;
            file->Close();
            continue;
        }
        if (!dirMethodBDT) {
            std::cout << "Directory 'dirMethodBDT' not found in file: " << fileName << std::endl;
            file->Close();
            continue;
        }
        if (!dirFold) {
            std::cout << "Directory 'dirFold' not found in file: " << fileName << std::endl;
            file->Close();
            continue;
        }
        if (!histo) {
            std::cout << "Histogram not found: " << fileName << " -> " << Form("BDTG_fold%d", i) << std::endl;
            file->Close();
            continue;
        }

        // Draw the histogram
        histo->SetLineColor(colors[i-1]);
        histo->SetLineWidth(2);
        if (i == 1){
            histo->Draw("HIST");
            c1->cd();
        }
        else histo->Draw("HIST SAME");
        c1->Update();

        // Add to legend
        legend->AddEntry(histo, Form("Fold %d", i), "l");

        // Close the file
        file->Close();
    }
    std::cout << "TMVA :: Loop completed " << std::endl;
    //legend->Draw();
    c1->SaveAs("roc_curves.png");
}



// On the terminal:
TFile *file_1 = TFile::Open("BDTG_fold1.root");
TFile *file_2 = TFile::Open("BDTG_fold2.root");
TFile *file_3 = TFile::Open("BDTG_fold3.root");
TFile *file_4 = TFile::Open("BDTG_fold4.root");
TFile *file_5 = TFile::Open("BDTG_fold5.root");
//
  TDirectoryFile *dirDataset_1 = (TDirectoryFile*)file_1->Get("dataset");
  TDirectoryFile *dirMethodBDT_1 = (TDirectoryFile*)dirDataset_1->Get("Method_BDT")
  TDirectoryFile *dirFold_1 = (TDirectoryFile*)dirMethodBDT_1->Get(Form("BDTG_fold1"));
  TH1D *histo_1 = (TH1D*)dirFold_1->Get(Form("MVA_BDTG_fold1_rejBvsS"));
//
  TDirectoryFile *dirDataset_2 = (TDirectoryFile*)file_2->Get("dataset");
  TDirectoryFile *dirMethodBDT_2 = (TDirectoryFile*)dirDataset_2->Get("Method_BDT")
  TDirectoryFile *dirFold_2 = (TDirectoryFile*)dirMethodBDT_2->Get(Form("BDTG_fold2"));
  TH1D *histo_2 = (TH1D*)dirFold_2->Get(Form("MVA_BDTG_fold2_rejBvsS"));

  TDirectoryFile *dirDataset_3 = (TDirectoryFile*)file_3->Get("dataset");
  TDirectoryFile *dirMethodBDT_3 = (TDirectoryFile*)dirDataset_3->Get("Method_BDT")
  TDirectoryFile *dirFold_3 = (TDirectoryFile*)dirMethodBDT_3->Get(Form("BDTG_fold3"));
  TH1D *histo_3 = (TH1D*)dirFold_3->Get(Form("MVA_BDTG_fold3_rejBvsS"));
//
  TDirectoryFile *dirDataset_4 = (TDirectoryFile*)file_4->Get("dataset");
  TDirectoryFile *dirMethodBDT_4 = (TDirectoryFile*)dirDataset_4->Get("Method_BDT")
  TDirectoryFile *dirFold_4 = (TDirectoryFile*)dirMethodBDT_4->Get(Form("BDTG_fold4"));
  TH1D *histo_4 = (TH1D*)dirFold_4->Get(Form("MVA_BDTG_fold4_rejBvsS"));
//
  TDirectoryFile *dirDataset_5 = (TDirectoryFile*)file_5->Get("dataset");
  TDirectoryFile *dirMethodBDT_5 = (TDirectoryFile*)dirDataset_5->Get("Method_BDT")
  TDirectoryFile *dirFold_5 = (TDirectoryFile*)dirMethodBDT_5->Get(Form("BDTG_fold5"));
  TH1D *histo_5 = (TH1D*)dirFold_5->Get(Form("MVA_BDTG_fold5_rejBvsS"));

  histo_1->SetLineColor(1);
  histo_2->SetLineColor(2);
  histo_3->SetLineColor(3);
  histo_4->SetLineColor(4);
  histo_5->SetLineColor(5);


  histo_1->SetLineWidth(2);
  histo_2->SetLineWidth(2);
  histo_3->SetLineWidth(2);
  histo_4->SetLineWidth(2);
  histo_5->SetLineWidth(2);


 gROOT->SetStyle("Plain");
 gStyle->SetOptTitle(0);

 histo_1->SetStats(0)
 TCanvas *c1=new TCanvas();
 histo_1->Draw("HIST");
 histo_2->Draw("HIST SAME");
 histo_3->Draw("HIST SAME");
 histo_4->Draw("HIST SAME");
 histo_5->Draw("HIST SAME");

c1->SaveAs("roc_curves.pdf");




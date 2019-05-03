#include <TH1D.h>
#include <TH2D.h>
#include <TH3D.h>
#include <TEfficiency.h>
#include <TFile.h>
#include <TTree.h>
#include "TGraphAsymmErrors.h"
#include <TBranch.h>
#include <TCanvas.h>
#include <TSpectrum.h>
#include <TF1.h>
#include "TLine.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <TLatex.h>
#include <vector>
#include <string>
#include <iostream>
#include <fstream>

using namespace std;

void macro_fast_efficiency(int run, string configDir)
{
	// Setting variables for min and max displayed efficiency (to be tuned in the analysis if things go wrong...)
	const float min_eff = 0.00;
	const float max_eff = 1.00;
	const float targetEfficiency = 0.70;
	
  // Getting the root file
  
  string filename = "fast_efficiency_out_run_";
  for (unsigned int i=0; i<(6-to_string(run).size()); i++)
  {
    filename += "0";
  }
  filename += to_string(run) + ".root";
  const char *file = filename.c_str();
  
  TFile *infile = new TFile(file,"UPDATE");
  if (infile->IsOpen()) cout << "File opened successfully" << endl;
  
  // Getting the tree
  
  TTree *tree = (TTree*)infile->Get("FastEfficiencyQC8/tree");
	
	// Declaration of name variables
	
  char *name = new char[40];
  string namename = "";
	
	// Generating 1D histograms (num, denom, eff) for the chambers
	
  TH1D *num1D = (TH1D*)infile->Get("FastEfficiencyQC8/numerator");
  TH1D *denom1D = (TH1D*)infile->Get("FastEfficiencyQC8/denominator");
	
  TGraphAsymmErrors *eff1D = new TGraphAsymmErrors;
	eff1D->Divide(num1D,denom1D);
	
	// Getting rechHits per layer histrogram
	
	TH3D *recHitsPerLayer = (TH3D*)infile->Get("FastEfficiencyQC8/recHits2DPerLayer");
	
	// rechHits plots per chamber
	
	TH2D *recHits2D[10];
	for (int row=0; row<5; row++)
	{
		namename = "recHits_row_" + to_string(row+1) + "_B";
		recHits2D[row*2] = new TH2D(namename.c_str(),"",400,-100,100,8,-0.5,7.5);
		namename = "recHits_row_" + to_string(row+1) + "_T";
		recHits2D[(row*2)+1] = new TH2D(namename.c_str(),"",400,-100,100,8,-0.5,7.5);
	}
	
	for (int layer=0; layer<10; layer++)
	{
		for (int eta=1; eta<=8; eta++)
		{
			for (int phi=1; phi<=400; phi++)
			{
				recHits2D[layer]->SetBinContent(phi,eta,recHitsPerLayer->GetBinContent(phi,eta,layer+1));
			}
		}
	}
	
	// Getting clusterSize 3D histogram
	
	TH3D *clusterSize3D = (TH3D*)infile->Get("FastEfficiencyQC8/clusterSize");
	
	// cluster size plots per chamber and per eta partition
	
	TH1D *clusterSize1D[30][8];
	
	for (unsigned int ch=0; ch<30; ch++)
	{
		for (unsigned int eta=0; eta<8; eta++)
		{
			sprintf(name,"clusterSize_ch_%u_eta_%u",ch,(eta+1));
			clusterSize1D[ch][eta] = new TH1D(name,"",20,0,20);
			
			for (int cls=0; cls<20; cls++)
			{
				clusterSize1D[ch][eta]->SetBinContent((cls+1),clusterSize3D->GetBinContent(ch+1,eta+1,cls+1));
			}
		}
	}
  
	// Open stand configuration file for present run & get names + positions of chambers
	
	string configName = configDir + "StandGeometryConfiguration_run" + to_string(run) + ".csv";
	ifstream standConfigFile (configName);
	
	string line, split, comma = ",", slash = "/";
	vector<string> chamberName;
	int ChPos = 0;
	vector<int> chamberPos;
	size_t pos = 0;
	
	if (standConfigFile.is_open())
	{
		while (getline(standConfigFile, line))
		{
			pos = line.find(comma);
			split = line.substr(0, pos);
			if (split == "RunNumber" || split == "ChamberName") continue;
			chamberName.push_back(split);
			line.erase(0, pos + comma.length());
			
			pos = line.find(slash);
			split = line.substr(0, pos);
			ChPos = (stoi(split)-1)*2; // (Row-1)*2
			line.erase(0, pos + slash.length());
			
			pos = line.find(slash);
			split = line.substr(0, pos);
			ChPos += (stoi(split)-1)*10; // (Row-1)*2 + (Col-1)*10
			line.erase(0, pos + slash.length());
			
			pos = line.find(comma);
			split = line.substr(0, pos);
			if (split == "B") ChPos += 0; // (Row-1)*2 + (Col-1)*10 + 0
			if (split == "T") ChPos += 1; // (Row-1)*2 + (Col-1)*10 + 1
			line.erase(0, pos + comma.length());
			
			chamberPos.push_back(ChPos);
		}
	}
	else cout << "Error opening file: " << configName << endl;
  
  // Results for the 30 chambers
  
  TCanvas *Canvas = new TCanvas("Canvas","Canvas",0,0,1000,800);
  TF1 *targetLine = new TF1("targetLine",targetEfficiency,0,30);
  targetLine->SetLineColor(kRed);
  
  ofstream outfile;
	
	// Plot Numerator e Denominator
	
	namename = "Denominator";
	denom1D->SetTitle(namename.c_str());
	denom1D->GetXaxis()->SetTitle("Chamber position");
	denom1D->GetYaxis()->SetTitle("Counts");
	denom1D->Write(namename.c_str());
	denom1D->SetLineColor(kRed);
	denom1D->Draw();
	namename = "Numerator";
	num1D->SetTitle(namename.c_str());
	num1D->GetXaxis()->SetTitle("Chamber position");
	num1D->GetYaxis()->SetTitle("Counts");
	num1D->Write(namename.c_str());
	namename = "Num_Denom";
	num1D->SetTitle(namename.c_str());
	num1D->SetLineColor(kBlue);
	num1D->Draw("SAME");
	namename = "Num_Denom_Chambers_Fast_Efficiency.png";
	Canvas->SaveAs(namename.c_str());
	Canvas->Clear();
	
	// Plot Efficiency
	
	namename = "Efficiency";
	eff1D->SetTitle(namename.c_str());
	eff1D->GetXaxis()->SetTitle("Chamber position");
	eff1D->GetYaxis()->SetTitle("Efficiency");
	eff1D->GetYaxis()->SetRangeUser(min_eff,max_eff);
	eff1D->SetMarkerStyle(20);
	eff1D->Draw();
	eff1D->Write(namename.c_str());
	targetLine->Draw("SAME");
	namename = "Efficiency_Chambers_Fast_Efficiency.png";
	Canvas->SaveAs(namename.c_str());
	Canvas->Clear();
  
  for (unsigned int i=0; i<chamberPos.size(); i++)
  {
    int c = chamberPos[i];
		
    // Efficiency results in csv files
    
    string outFileName = "Fast_Efficiency_Ch_Pos_" + to_string(chamberPos[i]) + ".csv";
    outfile.open(outFileName);
		
    string entry = "";
    
    entry = "RunNumber," + to_string(run) + "\n";
    outfile << entry;
    entry = "ChamberName," + chamberName[i] + "\n";
    outfile << entry;
		
		double eff_value = eff1D->GetY()[c];
		double error_value = (eff1D->GetEYhigh()[c] + eff1D->GetEYlow()[c]) / 2.0;
		
		entry = "OverallEfficiency," + to_string(eff_value) + "\n";
		outfile << entry;
		entry = "ErrorEfficiency," + to_string(error_value) + "\n";
		outfile << entry;
		
    outfile.close();
		
		// Plotting clusterSize per chamber per eta
		
		for (unsigned int eta=0; eta<8; eta++)
		{
			namename = "ClusterSize_" + chamberName[i] + "_in_position_" + to_string(chamberPos[i]) + "_eta_" + to_string(eta+1);
			clusterSize1D[c][eta]->SetTitle(namename.c_str());
			clusterSize1D[c][eta]->GetXaxis()->SetTitle("ClusterSize");
			clusterSize1D[c][eta]->GetYaxis()->SetTitle("Counts");
			clusterSize1D[c][eta]->Draw();
			clusterSize1D[c][eta]->Write(namename.c_str());
			namename = "outPlots_Chamber_Pos_" + to_string(chamberPos[i]) + "/ClusterSize_Ch_Pos_" + to_string(chamberPos[i]) + "_eta_" + to_string(eta+1) + ".png";
			Canvas->SaveAs(namename.c_str());
			Canvas->Clear();
		}
  }
  
  standConfigFile.close();
	
	// Plots of recHits per layer
	
	for (int row=0; row<5; row++)
	{
		namename = "recHits_Row_" + to_string(row+1) + "_B";
		recHits2D[row*2]->SetTitle(namename.c_str());
		recHits2D[row*2]->SetStats(0);
		recHits2D[row*2]->GetXaxis()->SetTitle("x [cm]");
		recHits2D[row*2]->GetYaxis()->SetTitle("#eta partition");
		for (int y = 0; y < 8; y++)
		{
			recHits2D[row*2]->GetYaxis()->SetBinLabel(y+1, to_string(y+1).c_str());
		}
		recHits2D[row*2]->Draw("colz");
		namename = "recHits_Row_" + to_string(row+1) + "_B.png";
		Canvas->SaveAs(namename.c_str());
		Canvas->Clear();
		namename = "recHits_Row_" + to_string(row+1) + "_T";
		recHits2D[(row*2)+1]->SetTitle(namename.c_str());
		recHits2D[(row*2)+1]->SetStats(0);
		recHits2D[(row*2)+1]->GetXaxis()->SetTitle("x [cm]");
		recHits2D[(row*2)+1]->GetYaxis()->SetTitle("#eta partition");
		for (int y = 0; y < 8; y++)
		{
			recHits2D[row*2+1]->GetYaxis()->SetBinLabel(y+1, to_string(y+1).c_str());
		}
		recHits2D[(row*2)+1]->Draw("colz");
		namename = "recHits_Row_" + to_string(row+1) + "_T.png";
		Canvas->SaveAs(namename.c_str());
		Canvas->Clear();
	}
	
  infile->Close();
}

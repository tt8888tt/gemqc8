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

void macro_validation(int run, string configDir, string startDateTimeRun)
{
	// Setting variables for min and max displayed efficiency (to be tuned in the analysis if things go wrong...)
	const float min_eff = 0.7;
	const float max_eff = 1.0;

	// Getting the root file

	string filename = "validation_out_run_";
	for (unsigned int i=0; i<(6-to_string(run).size()); i++)
	{
		filename += "0";
	}
	filename += to_string(run) + ".root";
	const char *file = filename.c_str();

	TFile *infile = new TFile(file,"UPDATE");
	if (infile->IsOpen()) cout << "File opened successfully" << endl;

	// Getting the tree

	TTree *tree = (TTree*)infile->Get("ValidationQC8/tree");
	int nTotEvents = tree->GetEntries();

	// Getting the 3D numerator & denominator

	TH3D *num3D = (TH3D*)infile->Get("ValidationQC8/hitsVFATnum");
	TH3D *denom3D = (TH3D*)infile->Get("ValidationQC8/hitsVFATdenom");

	// Generating 1D histograms (num, denom, eff) for the 30 chambers

	char *name = new char[40];
	string namename = "";

	TH1D *num1D[30];
	TH1D *denom1D[30];
	TGraphAsymmErrors *eff1D[30];

	for (int ch=0; ch<30; ch++)
	{
		sprintf(name,"Eff_Numerator_ch_%u",ch);
		num1D[ch] = new TH1D(name,"",24,-0.5,23.5);
		sprintf(name,"Eff_Denominator_ch_%u",ch);
		denom1D[ch] = new TH1D(name,"",24,-0.5,23.5);
		eff1D[ch] = new TGraphAsymmErrors;

		for (int eta=0; eta<8; eta++)
		{
			for (int phi=0; phi<3; phi++)
			{
				num1D[ch]->SetBinContent((8*phi+(7-eta)+1),num3D->GetBinContent(phi+1,eta+1,ch+1));
				denom1D[ch]->SetBinContent((8*phi+(7-eta)+1),denom3D->GetBinContent(phi+1,eta+1,ch+1));
			}
		}
		eff1D[ch]->Divide(num1D[ch],denom1D[ch]);
	}

	// Generating 2D histograms for the 5*2 rows

	TH2D *eff2D[10];
	for (int row=0; row<5; row++)
	{
		namename = "Efficiency_row_" + to_string(row+1) + "_B";
		eff2D[row*2] = new TH2D(namename.c_str(),"",9,-0.5,8.5,8,-0.5,7.5);
		namename = "Efficiency_row_" + to_string(row+1) + "_T";
		eff2D[(row*2)+1] = new TH2D(namename.c_str(),"",9,-0.5,8.5,8,-0.5,7.5);
	}
	for (int layer=0; layer<10; layer++)
	{
		for (int eta=1; eta<=8; eta++)
		{
			for (int phi=1; phi<=3; phi++)
			{
				eff2D[layer]->SetBinContent(phi  ,eta,double(num3D->GetBinContent(phi,eta,layer+1))/
																		double(denom3D->GetBinContent(phi,eta,layer+1)));
				eff2D[layer]->SetBinContent(phi+3,eta,double(num3D->GetBinContent(phi,eta,layer+11))/
																		double(denom3D->GetBinContent(phi,eta,layer+11)));
				eff2D[layer]->SetBinContent(phi+6,eta,double(num3D->GetBinContent(phi,eta,layer+21))/
																		double(denom3D->GetBinContent(phi,eta,layer+21)));
			}
		}
	}

	// Getting 3D digi histogram

	TH3D *digi3D = (TH3D*)infile->Get("ValidationQC8/digiStrips");

	// Digi plots per chamber

	TH2D *digi2D[30];

	for (int ch=0; ch<30; ch++)
	{
		sprintf(name,"Digi_ch_%u",ch);
		digi2D[ch] = new TH2D(name,"",384,0,384,8,-0.5,7.5);

		for (int eta=0; eta<8; eta++)
		{
			for (int phi=0; phi<384; phi++)
			{
				digi2D[ch]->SetBinContent((phi+1),(eta+1),digi3D->GetBinContent(phi+1,eta+1,ch+1));
			}
		}
	}

	// Getting digi multiplicity histogram

	TH2D *digiMultPerCh = (TH2D*)infile->Get("ValidationQC8/digisPerEvtPerCh");

	// Digi plots per chamber

	TH1D *nDigis[30];

	for (int ch=0; ch<30; ch++)
	{
		sprintf(name,"DigiMultiplicity_ch_%u",ch);
		nDigis[ch] = new TH1D(name,"",20,-0.5,19.5);

		for (int mult=1; mult<20; mult++)
		{
			nDigis[ch]->SetBinContent((mult+1),digiMultPerCh->GetBinContent(ch+1,mult+1));
		}
	}

	// Getting rechHits per layer histrogram

	TH3D *recHitsPerLayer = (TH3D*)infile->Get("ValidationQC8/recHits2DPerLayer");

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

	TH3D *clusterSize3D = (TH3D*)infile->Get("ValidationQC8/clusterSize");

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

	// Calculate endDateTimeRun

	int NumberOfEvents = 0;
	tree->SetBranchAddress("ev",&NumberOfEvents);
	tree->GetEntry(nTotEvents-1);

	string endDateTimeRun = startDateTimeRun;
	string delimiter = "";
	float avgCosmicRate = 100.0;
	int approxRunningTimeInMinutes = int((double(NumberOfEvents)/avgCosmicRate)/60.0);

	delimiter = "-";
	int year = stoi(endDateTimeRun.substr(0, endDateTimeRun.find(delimiter)));
	endDateTimeRun.erase(0, endDateTimeRun.find(delimiter) + delimiter.length());
	delimiter = "-";
	int month = stoi(endDateTimeRun.substr(0, endDateTimeRun.find(delimiter)));
	endDateTimeRun.erase(0, endDateTimeRun.find(delimiter) + delimiter.length());
	delimiter = "_";
	int day = stoi(endDateTimeRun.substr(0, endDateTimeRun.find(delimiter)));
	endDateTimeRun.erase(0, endDateTimeRun.find(delimiter) + delimiter.length());
	delimiter = ":";
	int hour = stoi(endDateTimeRun.substr(0, endDateTimeRun.find(delimiter)));
	endDateTimeRun.erase(0, endDateTimeRun.find(delimiter) + delimiter.length());
	int minutes = stoi(endDateTimeRun);

	startDateTimeRun = to_string(year) + "-" + string(2-to_string(month).length(),'0').append(to_string(month)) + "-" + string(2-to_string(day).length(),'0').append(to_string(day)) + " " + string(2-to_string(hour).length(),'0').append(to_string(hour)) + ":" + string(2-to_string(minutes).length(),'0').append(to_string(minutes));

	int plus_hours = int((minutes + approxRunningTimeInMinutes)/60);
	minutes = (minutes + approxRunningTimeInMinutes)%60;
	int plus_days = int((hour + plus_hours)/24);
	hour = (hour + plus_hours)%24;
	int plus_months = 0;
	if (month <= 7 && month%2 == 1) {
		plus_months = int((day + plus_days)/31);
		day = (day + plus_days)%31;
	}
	if (month == 2) {
		plus_months = int((day + plus_days)/28);
		day = (day + plus_days)%28;
	}
	if (month != 2 && month <= 7 && month%2 == 0) {
		plus_months = int((day + plus_days)/30);
		day = (day + plus_days)%30;
	}
	if (month >= 8 && month%2 == 0) {
		plus_months = int((day + plus_days)/31);
		day = (day + plus_days)%31;
	}
	if (month >= 8 && month%2 == 1) {
		plus_months = int((day + plus_days)/30);
		day = (day + plus_days)%30;
	}

	month = month + plus_months;

	endDateTimeRun = to_string(year) + "-" + string(2-to_string(month).length(),'0').append(to_string(month)) + "-" + string(2-to_string(day).length(),'0').append(to_string(day)) + " " + string(2-to_string(hour).length(),'0').append(to_string(hour)) + ":" + string(2-to_string(minutes).length(),'0').append(to_string(minutes));

	// Results for the 30 chambers

	TCanvas *Canvas = new TCanvas("Canvas","Canvas",0,0,1000,800);
	TF1 *target97 = new TF1("target97","0.97",0,24);
	target97->SetLineColor(kRed);

	ofstream outfile;

	for (unsigned int i=0; i<chamberPos.size(); i++)
	{
		int c = chamberPos[i];

		// Plot num e denom per chamber

		namename = "Denom_" + chamberName[i] + "_in_position_" + to_string(chamberPos[i]) + "_run_" + to_string(run);
		denom1D[c]->SetTitle(namename.c_str());
		denom1D[c]->GetXaxis()->SetTitle("VFAT");
		denom1D[c]->GetYaxis()->SetTitle("Counts");
		denom1D[c]->Write(namename.c_str());
		denom1D[c]->SetLineColor(kRed);
		denom1D[c]->Draw();
		namename = "Num_" + chamberName[i] + "_in_position_" + to_string(chamberPos[i]);
		num1D[c]->SetTitle(namename.c_str());
		num1D[c]->GetXaxis()->SetTitle("VFAT");
		num1D[c]->GetYaxis()->SetTitle("Counts");
		num1D[c]->Write(namename.c_str());
		namename = "Num_Denom_" + chamberName[i] + "_in_position_" + to_string(chamberPos[i]) + "_run_" + to_string(run);
		num1D[c]->SetTitle(namename.c_str());
		num1D[c]->SetLineColor(kBlue);
		num1D[c]->Draw("SAME");
		num1D[c]->SetTitle(namename.c_str());
		namename = "outPlots_Chamber_Pos_" + to_string(chamberPos[i]) + "/Num_Denom_Ch_Pos_" + to_string(chamberPos[i]) + ".png";
		Canvas->SaveAs(namename.c_str());
		Canvas->Clear();

		// Plot efficiency per chamber

		namename = "Efficiency_" + chamberName[i] + "_in_position_" + to_string(chamberPos[i]) + "_run_" + to_string(run);
		eff1D[c]->SetTitle(namename.c_str());
		eff1D[c]->GetXaxis()->SetTitle("VFAT");
		eff1D[c]->GetYaxis()->SetTitle("Efficiency");
		eff1D[c]->GetYaxis()->SetRangeUser(min_eff,max_eff);
		eff1D[c]->SetMarkerStyle(20);
		eff1D[c]->Draw();
		eff1D[c]->Write(namename.c_str());
		target97->Draw("SAME");
		namename = "outPlots_Chamber_Pos_" + to_string(chamberPos[i]) + "/Efficiency_Ch_Pos_" + to_string(chamberPos[i]) + ".png";
		Canvas->SaveAs(namename.c_str());
		Canvas->Clear();

		// Efficiency results in csv files

		string outFileName = "Efficiency_Ch_Pos_" + to_string(chamberPos[i]) + ".csv";
		outfile.open(outFileName);
		double eff_value, error_value;
		string entry = "";

		entry = "RunNumber," + to_string(run) + "\n";
		outfile << entry;
		entry = "ChamberName," + chamberName[i] + "\n";
		outfile << entry;
		entry = "BeginTime," + startDateTimeRun + "\n";
		outfile << entry;
		entry = "EndTime," + endDateTimeRun + "\n";
		outfile << entry;
		entry = "VFAT,EFFICIENCY,EFFICIENCY_ERROR,CLUSTER_SIZE_AVG,CLUSTER_SIZE_SIGMA,PERCENT_MASKED\n";
		outfile << entry;

		for (int vfat=0; vfat<24; vfat++)
		{
			int pointIndex = 999;
	    for (int j = 0; j < 24 ; j++)
	    {
	    	if ((eff1D[c]->GetX()[j] - vfat) == 0)
	    	{
	    		pointIndex = j;
	    		break;
	    	}
	    }
			eff_value = eff1D[c]->GetY()[pointIndex];
			error_value = (eff1D[c]->GetEYhigh()[pointIndex] + eff1D[c]->GetEYlow()[pointIndex]) / 2.0;
			int eta_partition = 7 - (vfat % 8);
			double cls_mean = clusterSize1D[c][eta_partition]->GetMean();
			double cls_sigma = clusterSize1D[c][eta_partition]->GetStdDev();
			entry = to_string(vfat) + "," + to_string(eff_value) + "," + to_string(error_value) + "," + to_string(cls_mean) + "," + to_string(cls_sigma) + "\n"; // here we have to insert the values of percent_masked
			outfile << entry;
		}
		outfile.close();

		// Plotting clusterSize per chamber per eta

		for (unsigned int eta=0; eta<8; eta++)
		{
			namename = "ClusterSize_" + chamberName[i] + "_in_position_" + to_string(chamberPos[i]) + "_eta_" + to_string(eta+1) + "_run_" + to_string(run);
			clusterSize1D[c][eta]->SetTitle(namename.c_str());
			clusterSize1D[c][eta]->GetXaxis()->SetTitle("ClusterSize");
			clusterSize1D[c][eta]->GetYaxis()->SetTitle("Counts");
			clusterSize1D[c][eta]->Draw();
			clusterSize1D[c][eta]->Write(namename.c_str());
			namename = "outPlots_Chamber_Pos_" + to_string(chamberPos[i]) + "/ClusterSize_Ch_Pos_" + to_string(chamberPos[i]) + "_eta_" + to_string(eta+1) + ".png";
			Canvas->SaveAs(namename.c_str());
			Canvas->Clear();
		}

		// Plotting digi per chamber

		namename = "Digi_" + chamberName[i] + "_in_position_" + to_string(chamberPos[i]) + "_run_" + to_string(run);
		digi2D[c]->SetTitle(namename.c_str());
		digi2D[c]->GetXaxis()->SetTitle("Strip Number");
		digi2D[c]->GetYaxis()->SetTitle("ieta");
		Canvas->SetLogz();
		for (int y = 0; y < 8; y++)
		{
			digi2D[c]->GetYaxis()->SetBinLabel(y+1, to_string(y+1).c_str());
		}
		digi2D[c]->Draw("colz");
		digi2D[c]->Write(namename.c_str());
		namename = "outPlots_Chamber_Pos_" + to_string(chamberPos[i]) + "/Digi_Ch_Pos_" + to_string(chamberPos[i]) + ".png";
		Canvas->SaveAs(namename.c_str());
		Canvas->Clear();
		Canvas->SetLogz(0);

		// Plotting number of digis per chamber

		namename = "NumberOfDigis_" + chamberName[i] + "_in_position_" + to_string(chamberPos[i]) + "_run_" + to_string(run);
		nDigis[c]->SetTitle(namename.c_str());
		nDigis[c]->GetXaxis()->SetTitle("Digi Multiplicity");
		nDigis[c]->GetYaxis()->SetTitle("Counts");
		nDigis[c]->Draw();
		nDigis[c]->Write(namename.c_str());
		namename = "outPlots_Chamber_Pos_" + to_string(chamberPos[i]) + "/NumberOfDigis_Ch_Pos_" + to_string(chamberPos[i]) + ".png";
		Canvas->SaveAs(namename.c_str());
		Canvas->Clear();

	}

	// Plots of recHits per layer

	for (int row=0; row<5; row++)
	{
		namename = "recHits_Row_" + to_string(row+1) + "_B" + "_run_" + to_string(run);
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
		namename = "recHits_Row_" + to_string(row+1) + "_T" + "_run_" + to_string(run);
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

	// Plots of efficiency per layer

	for (int row=0; row<5; row++)
	{
		TLine *col_1_2 = new TLine(2.5,-0.5,2.5,7.5);
		TLine *col_2_3 = new TLine(5.5,-0.5,5.5,7.5);
		namename = "Efficiency_Row_" + to_string(row+1) + "_B" + "_run_" + to_string(run);
		eff2D[row*2]->SetTitle(namename.c_str());
		eff2D[row*2]->SetMinimum(min_eff);
		eff2D[row*2]->SetMaximum(max_eff);
		eff2D[row*2]->SetStats(0);
		eff2D[row*2]->GetXaxis()->SetTitle("#phi partition");
		eff2D[row*2]->GetYaxis()->SetTitle("#eta partition");
		for (int x = 0; x < 9; x++)
		{
			eff2D[row*2]->GetXaxis()->SetBinLabel(x+1, to_string((x%3)+1).c_str());
		}
		for (int y = 0; y < 8; y++)
		{
			eff2D[row*2]->GetYaxis()->SetBinLabel(y+1, to_string(y+1).c_str());
		}
		eff2D[row*2]->Draw("colz TEXT0");
		col_1_2->Draw("SAME");
		col_2_3->Draw("SAME");
		namename = "Efficiency_Row_" + to_string(row+1) + "_B.png";
		Canvas->SaveAs(namename.c_str());
		Canvas->Clear();
		namename = "Efficiency_Row_" + to_string(row+1) + "_T" + "_run_" + to_string(run);
		eff2D[(row*2)+1]->SetTitle(namename.c_str());
		eff2D[(row*2)+1]->SetMinimum(min_eff);
		eff2D[(row*2)+1]->SetMaximum(max_eff);
		eff2D[(row*2)+1]->SetStats(0);
		eff2D[(row*2)+1]->GetXaxis()->SetTitle("#phi partition");
		eff2D[(row*2)+1]->GetYaxis()->SetTitle("#eta partition");
		for (int x = 0; x < 9; x++)
		{
			eff2D[row*2+1]->GetXaxis()->SetBinLabel(x+1, to_string((x%3)+1).c_str());
		}
		for (int y = 0; y < 8; y++)
		{
			eff2D[row*2+1]->GetYaxis()->SetBinLabel(y+1, to_string(y+1).c_str());
		}
		eff2D[(row*2)+1]->Draw("colz TEXT0");
		col_1_2->Draw("SAME");
		col_2_3->Draw("SAME");
		namename = "Efficiency_Row_" + to_string(row+1) + "_T.png";
		Canvas->SaveAs(namename.c_str());
		Canvas->Clear();
	}

	standConfigFile.close();
	infile->Close();
}

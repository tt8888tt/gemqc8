
#include <TH1F.h>
#include <TFile.h>
#include <TTree.h>
#include "TGraphErrors.h"
#include <TBranch.h>
#include <TCanvas.h>
#include <TSpectrum.h>
#include <TF1.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

using namespace std;

void macro_alignment(int run, string runPath, TString AlignTablePath, int step){
	// Getting the file
	TString filename = "temp_out_reco_MC_3_0.root";
	TFile *infile = TFile::Open(filename, "UPDATE");
	bool opened = infile->IsOpen();
	if(opened == true)
	{
		cout << "---ROOT file " << filename << " successfully opened...Loading" << endl;
	}
	else
	{
		cout << "ERROR: ROOT file " << filename << " does not exist!" << endl;
		exit(EXIT_FAILURE);
	}

	//USeful variable declaration
	int i_Eta = 8, i_maxSC = 15, i_maxC = 30;
	int chidx[i_maxSC];
	double Ypos[3][8] = {
		{72.747497,53.292499,35.486499,19.329500,4.4980001,-9.008000,-21.43950,-32.79650}, // zero is for long chambers
		{74.7225,58.0175,42.6115,28.5045,15.4475,3.4405,-7.6910,-17.9470}, // one is for short chambers
		{-999.,-999.,-999.,-999.,-999.,-999.,-999.,-999.}
	};

	// Getting the TTree
	TString direc = "AlignmentQC8/";
	TTree *datatree = (TTree*)infile->Get(direc+"tree");

	//  infile->ls();

	// Getting the information on chamber type
	string infilename = runPath+"/configureRun_cfi.py";
	ifstream standConfigFile(infilename);
	string line, split, equal = " = ";
	vector<string> chType;
	char comma = ',';
	size_t pos;
	if(standConfigFile.is_open())
	{
		while (getline(standConfigFile, line))
		{
			pos = line.find(equal);
			split = line.substr(0, pos);
			if (split != "StandConfiguration" || pos == string::npos) continue;
			else if (split == "StandConfiguration")
			{
				while (getline(standConfigFile, line))
				{
					stringstream linestream(line);
					for (string each; getline(linestream, each, comma); chType.push_back(each));
					if(chType.at(chType.size()-1)== "\\") chType.pop_back();
					if(chType.size()==15) continue;
				}
			}
		}
	}
	else
	{
		cerr << infilename << " is not correctly opened" << endl;
		exit(EXIT_FAILURE);
	}

	for(int i_SC=0; i_SC<i_maxSC; i_SC++)
	{
		if(chType.at(i_SC).substr(0,1)=='0') chidx[i_SC]=2;
		else if(chType.at(i_SC).substr(0,1)=='S') chidx[i_SC]=1;
		else  chidx[i_SC]=0;
		cout << chType.at(i_SC) << "    " <<  chidx[i_SC] << endl;
	}

	// Getting the number of events
	TH1D *hevt = (TH1D*)infile->Get(direc+"hev");
	int evt_tot_number = hevt->GetBinContent(1);

	cout << "Number of events = " << evt_tot_number << endl;

	// Histogram declaration
	char *histname = new char[20];
	char *histoname = new char[20];
	TH1D *resXperSC[i_maxSC][i_Eta];
	for (int i_SC=0; i_SC<i_maxSC; i_SC++)
	{
		for (int i_eta=0; i_eta<i_Eta; i_eta++)
		{
			sprintf(histname,"resX_SC_%u_%u_eta_%u",(i_SC%5)+1,(i_SC/5)+1,i_eta+1); //Convention for position of the SuperChamber row[1-5]/column[1-3]_ieta[1-8]
			resXperSC[i_SC][i_eta] = new TH1D(histname,"",300,-3,3);
		}
	}

	double resEtaY[i_Eta];
	double resEtaYError[i_Eta];
	int dx_fail=0;
	int rz_fail=0;
	char *cnvname = new char[20];
	TCanvas *cnvResX[i_maxSC];
	TCanvas *cnvResCorrPlot[i_maxSC];

	double dx[i_maxSC], dx_prev[i_maxSC];
	double rz[i_maxSC], rz_prev[i_maxSC];
	Float_t dx_pre[i_maxC], rz_pre[i_maxC];
	for (int i_SC=0; i_SC<i_maxC; i_SC++)
	{
		dx_pre[i_SC]=90000.;
		rz_pre[i_SC]=90000.;
	}
	// Getting the dx and rz at the previous step
	datatree->SetBranchAddress("dx", &dx_pre);
	datatree->SetBranchAddress("rz", &rz_pre);

	for(int i=0; i<1; i++)
	{
		datatree->GetEntry(i);
		for (int i_SC=0; i_SC<i_maxSC; i_SC++)
		{
			dx_prev[i_SC] = dx_pre[i_SC*2];
			rz_prev[i_SC] = rz_pre[i_SC*2];
			cout << "prev dx " <<  dx_prev[i_SC];
			cout << " prev rz " <<  rz_prev[i_SC] << endl;
		}
	}

	// Residuals per SC
	cout << "Starting the analysis of run " << run << endl;

	for (int i_SC=0; i_SC<i_maxSC; i_SC++)
	{
		sprintf(cnvname,"cnv_SC_%u_%u",(i_SC%5)+1,(i_SC/5)+1);
		cnvResX[i_SC] = new TCanvas(cnvname,cnvname,0,0,1000,600);
		cnvResX[i_SC]->Divide(4,2);
		for (int i_eta=0; i_eta<i_Eta; i_eta++)
		{
			cnvResX[i_SC]->cd(i_eta+1);
			sprintf(histoname,"hchEtaResidualX_%d_%d", i_SC+1, i_eta+1);
			resXperSC[i_SC][i_eta]=(TH1D*)infile->Get(direc+histoname);
			resXperSC[i_SC][i_eta]->Draw();
			TF1 *GaussFit = new TF1("GaussFit","gaus",-3,3);
			resXperSC[i_SC][i_eta]->Fit(GaussFit,"Q");
			GaussFit->Draw("SAME");
			resEtaY[i_eta] = GaussFit->GetParameter(1);
			resEtaYError[i_eta] = GaussFit->GetParError(1);
			delete GaussFit;
		}

		cnvResCorrPlot[i_SC] = new TCanvas(cnvname,cnvname,0,0,1000,600);
		sprintf(histname,"resCorrPlot_SC_%u_%u",(i_SC%5)+1,(i_SC/5)+1);
		TGraphErrors *resCorrPlotSC = new TGraphErrors(i_Eta,Ypos[chidx[i_SC]],resEtaY,0,resEtaYError);
		resCorrPlotSC->SetTitle(histname);
		resCorrPlotSC->SetMarkerSize(1.5);
		resCorrPlotSC->SetMarkerStyle(21);
		resCorrPlotSC->Draw("ap");
		TF1 *LinFit = new TF1("LinFit","pol1",Ypos[chidx[i_SC]][i_Eta-1]-2,Ypos[chidx[i_SC]][0]+2);
		resCorrPlotSC->Fit(LinFit,"Q");
		resCorrPlotSC->Write(histname);
		dx[i_SC] = -LinFit->GetParameter(0);
		rz[i_SC] = -LinFit->GetParameter(1);
		delete LinFit;
	}

	cout << "shiftX = [";
	for (int i_SC=0; i_SC<i_maxSC; i_SC++)
	{
		cout << dx[i_SC] << ",";
		if (i_SC == 14) cout << dx[i_SC];
		if (i_SC == 4 || i_SC == 9) cout << "\\" << endl;
		if (i_SC == 14) cout << "]\n" << endl;
	}

	cout << "rotationZ = [";
	for (int i_SC=0; i_SC<i_maxSC; i_SC++)
	{
		cout << rz[i_SC] << ",";
		if (i_SC == 14) cout << rz[i_SC];
		if (i_SC == 4 || i_SC == 9) cout << "\\" << endl;
		if (i_SC == 14) cout << "]\n" << endl;
	}
	// Writing the output in csv format
	char *partialoutfilename = new char[70];
	sprintf(partialoutfilename,AlignTablePath+"StandAlignmentValues_run%d_step%d.csv", run, step);
	ofstream partialFile(partialoutfilename, std::ios_base::out | std::ios_base::trunc);
	if(partialFile.is_open())
	{
		cout << "Writing the new alignment factors in " << partialoutfilename << endl;
		partialFile << "RunNumber,"<< run <<",,,,,\n";
		partialFile << "Position,dx(cm),dy(cm),dz(cm),rx(deg),ry(deg),rz(deg)\n";
		for (int i_SC=0; i_SC<i_maxSC; i_SC++)
		{
			partialFile << (i_SC%5)+1 << "/" << (i_SC/5)+1 << "," << dx[i_SC] << ",0" << ",0," << rz[i_SC] << ",0" << ",0\n";
		}
		partialFile.close();
	}
	else
	{
		cerr << partialoutfilename << " is not correctly opened" << endl;
		exit(EXIT_FAILURE);
	}

	for (int i_SC=0; i_SC<i_maxSC; i_SC++)
	{
		if(fabs(dx[i_SC])>0.03) dx_fail+=1;
		if(fabs(rz[i_SC])>0.03) rz_fail+=1;
	}
	if(dx_fail>1)
	{
		for (int i_SC=0; i_SC<i_maxSC; i_SC++)
		{
			dx[i_SC] += dx_prev[i_SC];
			rz[i_SC] += rz_prev[i_SC];
		}
	}
	// Writing the output in csv format
	char *totaloutfilename = new char[70];
	sprintf(totaloutfilename,AlignTablePath+"/StandAlignmentValues_run%d.csv", run);
	ofstream totalFile(totaloutfilename, std::ios_base::out | std::ios_base::trunc);
	if(totalFile.is_open())
	{
		totalFile << "RunNumber,"<< run <<",,,,,\n";
		totalFile << "Position,dx(cm),dy(cm),dz(cm),rx(deg),ry(deg),rz(deg)\n";
		for (int i_SC=0; i_SC<i_maxSC; i_SC++)
		{
			totalFile << (i_SC%5)+1 << "/" << (i_SC/5)+1 << "," << dx[i_SC] << ",0" << ",0," << rz[i_SC] << ",0" << ",0\n";
		}
		totalFile.close();
	}
	else
	{
		cerr << totaloutfilename << " is not correctly opened" << endl;
		exit(EXIT_FAILURE);
	}
}

#include "Analysis/GEMQC8/interface/FastEfficiencyQC8.h"

#include <iomanip>

#include <TCanvas.h>

using namespace std;
using namespace edm;

FastEfficiencyQC8::FastEfficiencyQC8(const edm::ParameterSet& cfg): GEMBaseValidation(cfg)
{
	time_t rawTime;
	time(&rawTime);
	printf("Begin of FastEfficiencyQC8::FastEfficiencyQC8() at %s\n", asctime(localtime(&rawTime)));
	InputTagToken_RH = consumes<GEMRecHitCollection>(cfg.getParameter<edm::InputTag>("recHitsInputLabel"));
	edm::ParameterSet serviceParameters = cfg.getParameter<edm::ParameterSet>("ServiceParameters");
	theService = new MuonServiceProxy(serviceParameters);
	minCLS = cfg.getParameter<double>("minClusterSize");
	maxCLS = cfg.getParameter<double>("maxClusterSize");
	theUpdator = new KFUpdator();
	time(&rawTime);
	
	edm::Service<TFileService> fs;
	
	// Histograms declaration
	
	recHits3D = fs->make<TH3D>("recHits3D","recHits 3D map",200,-100,100,156,-61,95,83,-12,154); // volume defined by the scintillators
  recHits2DPerLayer = fs->make<TH3D>("recHits2DPerLayer","recHits per layer",400,-100,100,8,0,8,10,0,10);
  clusterSize = fs->make<TH3D>("clusterSize","clusterSize per chamber per eta partition",30,0,30,8,0,8,20,0,20);
	
	numerator = fs->make<TH1D>("numerator","numerator",30,0,30);
	denominator = fs->make<TH1D>("denominator","denominator",30,0,30);
	
	// Tree branches declaration
	
	tree = fs->make<TTree>("tree", "Tree for QC8");
	tree->Branch("run",&run,"run/I");
	tree->Branch("lumi",&lumi,"lumi/I");
	tree->Branch("ev",&nev,"ev/I");
	
	printf("End of FastEfficiencyQC8::FastEfficiencyQC8() at %s\n", asctime(localtime(&rawTime)));
}

void FastEfficiencyQC8::bookHistograms(DQMStore::IBooker & ibooker, edm::Run const & Run, edm::EventSetup const & iSetup )
{
	time_t rawTime;
	time(&rawTime);
	printf("Begin of FastEfficiencyQC8::bookHistograms() at %s\n", asctime(localtime(&rawTime)));
	GEMGeometry_ = initGeometry(iSetup);
	if ( GEMGeometry_ == nullptr) return ;
	
	const std::vector<const GEMSuperChamber*>& superChambers_ = GEMGeometry_->superChambers();
	for (auto sch : superChambers_)
	{
		int n_lay = sch->nChambers();
		for (int l=0;l<n_lay;l++)
		{
			gemChambers.push_back(*sch->chamber(l+1));
		}
	}
	n_ch = gemChambers.size();
	
	time(&rawTime);
	
	printf("End of FastEfficiencyQC8::bookHistograms() at %s\n", asctime(localtime(&rawTime)));
}

const GEMGeometry* FastEfficiencyQC8::initGeometry(edm::EventSetup const & iSetup)
{
	const GEMGeometry* GEMGeometry_ = nullptr;
	try {
		edm::ESHandle<GEMGeometry> hGeom;
		iSetup.get<MuonGeometryRecord>().get(hGeom);
		GEMGeometry_ = &*hGeom;
	}
	catch( edm::eventsetup::NoProxyException<GEMGeometry>& e) {
		edm::LogError("MuonGEMBaseValidation") << "+++ Error : GEM geometry is unavailable on event loop. +++\n";
		return nullptr;
	}
	return GEMGeometry_;
}

FastEfficiencyQC8::~FastEfficiencyQC8() {
	printf("Done!");
}

void FastEfficiencyQC8::analyze(const edm::Event& e, const edm::EventSetup& iSetup)
{
	run = e.id().run();
	lumi = e.id().luminosityBlock();
	nev = e.id().event();
	
	theService->update(iSetup);
	
	edm::Handle<GEMRecHitCollection> gemRecHits;
	e.getByToken(this->InputTagToken_RH, gemRecHits);
	if (!gemRecHits.isValid())
	{
		edm::LogError("gemcrValidation") << "Cannot get strips by Token RecHits Token.\n";
		return ;
	}
	
	// Arrays: have a chamber fired?
	bool fired_ch_evt[30];
	for (int ch=0; ch<30; ch++) {fired_ch_evt[ch] = false;}
	
	// recHits loop
	for (GEMRecHitCollection::const_iterator rechit = gemRecHits->begin(); rechit != gemRecHits->end(); ++rechit)
	{
		// calculation of chamber id
		GEMDetId hitID((*rechit).rawId());
		int chIdRecHit = hitID.chamberId().chamber() + hitID.chamberId().layer() - 2;
		
		// cluster size plot and selection
		clusterSize->Fill(chIdRecHit,hitID.roll()-1,(*rechit).clusterSize());
		if ((*rechit).clusterSize()<minCLS) continue;
		if ((*rechit).clusterSize()>maxCLS) continue;
		
		// fired chambers
		fired_ch_evt[chIdRecHit] = true;
		
		// recHits plots
		GlobalPoint recHitGP = GEMGeometry_->idToDet((*rechit).gemId())->surface().toGlobal(rechit->localPosition());
    recHits3D->Fill(recHitGP.x(),recHitGP.y(),recHitGP.z());
    recHits2DPerLayer->Fill(recHitGP.x(),hitID.roll()-1,chIdRecHit % 10);		
	}
	
	// Reference: even chambers, Under test: odd chambers
	for (int ch=0; ch<=28; ch+=2)
	{
		if (fired_ch_evt[ch] == true) // We see hits in even chamber
		{
			denominator->Fill(ch+1); // Denominator of corresponding odd chamber +1
			if (fired_ch_evt[ch+1] == true) // We see hits in the corresponding odd chamber
			{
				numerator->Fill(ch+1); // Numberator of corresponding odd chamber +1
			}
		}
	}
	
	// Reference: odd chambers, Under test: even chambers
	for (int ch=1; ch<=29; ch+=2)
	{
		if (fired_ch_evt[ch] == true) // We see hits in odd chamber
		{
			denominator->Fill(ch-1); // Denominator of corresponding even chamber +1
			if (fired_ch_evt[ch-1] == true) // We see hits in the corresponding even chamber
			{
				numerator->Fill(ch-1); // Numberator of corresponding even chamber +1
			}
		}
	}
	
	tree->Fill();
}


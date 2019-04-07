#include "Analysis/GEMQC8/interface/HotDeadStripsQC8.h"

#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "Geometry/GEMGeometry/interface/GEMSuperChamber.h"
#include <Geometry/GEMGeometry/interface/GEMGeometry.h>
#include <Geometry/Records/interface/MuonGeometryRecord.h>

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/GeometrySurface/interface/Bounds.h"
#include "DataFormats/GeometryVector/interface/LocalPoint.h"
#include "DataFormats/GeometryVector/interface/GlobalPoint.h"
#include "DataFormats/Math/interface/Vector.h"
#include "DataFormats/Math/interface/Point3D.h"
#include "DataFormats/Common/interface/RefToBase.h"

#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "DataFormats/GEMDigi/interface/GEMDigiCollection.h"

#include "SimDataFormats/GeneratorProducts/interface/HepMCProduct.h"

#include <iomanip>

#include <TCanvas.h>

using namespace std;
using namespace edm;

HotDeadStripsQC8::HotDeadStripsQC8(const edm::ParameterSet& cfg): GEMBaseValidation(cfg)
{
  time_t rawTime;
  time(&rawTime);
  printf("Begin of HotDeadStripsQC8::HotDeadStripsQC8() at %s\n", asctime(localtime(&rawTime)));
  InputTagToken_DG = consumes<GEMDigiCollection>(cfg.getParameter<edm::InputTag>("gemDigiLabel"));
  edm::ParameterSet serviceParameters = cfg.getParameter<edm::ParameterSet>("ServiceParameters");
  theService = new MuonServiceProxy(serviceParameters);
  time(&rawTime);
  
  edm::Service<TFileService> fs;
  
  // Histograms declaration
  
  digiStrips = fs->make<TH3D>("digiStrips","digi per strip",384,0,384,8,0,8,30,0,30);
  
  // Geometry definition
  
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
  
  printf("End of HotDeadStripsQC8::HotDeadStripsQC8() at %s\n", asctime(localtime(&rawTime)));
}

const GEMGeometry* HotDeadStripsQC8::initGeometry(edm::EventSetup const & iSetup) {
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

HotDeadStripsQC8::~HotDeadStripsQC8() {
  printf("Successfully done!");
}

void HotDeadStripsQC8::analyze(const edm::Event& e, const edm::EventSetup& iSetup){
  
  g_nEvt++;
  
  run = e.id().run();
  lumi = e.id().luminosityBlock();
  nev = e.id().event();
  
  theService->update(iSetup);
  
  // digis

  edm::Handle<GEMDigiCollection> digis;
  e.getByToken( this->InputTagToken_DG, digis);
  int nNumDigi = 0;
  for (GEMDigiCollection::DigiRangeIterator gemdgIt = digis->begin(); gemdgIt != digis->end(); ++gemdgIt)
  {
    nNumDigi++;
    const GEMDetId& gemId = (*gemdgIt).first;
    const GEMDigiCollection::Range& range = (*gemdgIt).second;
    for ( auto digi = range.first; digi != range.second; ++digi )
    {
      digiStrips->Fill(digi->strip(),gemId.roll()-1,(gemId.chamberId().chamber()+gemId.chamberId().layer()-2)); // Strip#=[0,383] -> OK , Eta#=[1,8] -> -1
    }
  }
  
  tree->Fill();
}

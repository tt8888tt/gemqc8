#ifndef HotDeadStripsQC8_H
#define HotDeadStripsQC8_H

#include "Validation/MuonGEMHits/interface/GEMBaseValidation.h"
#include <DataFormats/GEMRecHit/interface/GEMRecHit.h>
#include <DataFormats/GEMRecHit/interface/GEMRecHitCollection.h>
#include <DataFormats/TrackReco/interface/Track.h>
#include <DataFormats/TrackingRecHit/interface/TrackingRecHit.h>
#include "RecoMuon/TrackingTools/interface/MuonServiceProxy.h"
#include "DataFormats/MuonDetId/interface/GEMDetId.h"
#include "Geometry/GEMGeometry/interface/GEMChamber.h"

#include "Geometry/GEMGeometry/interface/GEMGeometry.h"
#include "Geometry/Records/interface/MuonGeometryRecord.h"

#include "RecoMuon/CosmicMuonProducer/interface/CosmicMuonSmoother.h"
#include "TrackingTools/KalmanUpdators/interface/KFUpdator.h"

#include "RecoMuon/TransientTrackingRecHit/interface/MuonTransientTrackingRecHit.h"
#include "RecoMuon/StandAloneTrackFinder/interface/StandAloneMuonSmoother.h"
#include "TrackingTools/TrajectoryState/interface/TrajectoryStateTransform.h"

#include "SimDataFormats/Track/interface/SimTrack.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include <TFile.h>
#include <TTree.h>

class HotDeadStripsQC8 : public GEMBaseValidation
{
public:
  explicit HotDeadStripsQC8( const edm::ParameterSet& );
  ~HotDeadStripsQC8();
  void analyze(const edm::Event& e, const edm::EventSetup&) override;
  const GEMGeometry* initGeometry(edm::EventSetup const & iSetup);
private:
  const GEMGeometry* GEMGeometry_;
  
  std::vector<GEMChamber> gemChambers;
  int n_ch;
  
  edm::EDGetToken InputTagToken_, InputTagToken_DG;
  
  TH3D *digiStrips;
  
  TTree *tree;
  int run;
  int lumi;
  int nev;
};

#endif

////////////////////////////// ZToPsi2MuBuilder //////////////////////////////
/// authors: Meng Lu
/// takes the Psi(2S) (J/psi->2mu + 2pi) and a di-muon collection and produce Z
/// candidates using a six-track vertex fit
/// based on Yihui code and PsiToJpsi2PiBuilder pattern

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"

#include <vector>
#include <memory>
#include <map>
#include <string>
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/PatCandidates/interface/CompositeCandidate.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "CommonTools/Statistics/interface/ChiSquaredProbability.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "helper.h"
#include <limits>
#include <algorithm>
#include "KinVtxFitter.h"

class ZToPsi2MuBuilder : public edm::global::EDProducer<> {

public:
  typedef std::vector<reco::TransientTrack> TransientTrackCollection;

  explicit ZToPsi2MuBuilder(const edm::ParameterSet &cfg):
    bFieldToken_{esConsumes<MagneticField, IdealMagneticFieldRecord>()},
    // selections
    l3_selection_{cfg.getParameter<std::string>("lep3Selection")},
    l4_selection_{cfg.getParameter<std::string>("lep4Selection")},
    pre_vtx_selection_{cfg.getParameter<std::string>("preVtxSelection")},
    post_vtx_selection_{cfg.getParameter<std::string>("postVtxSelection")},
    //inputs
    psi2s_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("PsiToJpsi2Pi") )},
    leptonsrc_{consumes<pat::MuonCollection>( cfg.getParameter<edm::InputTag>("leptonsrc") )},
    leptons_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("leptonTransientTracks"))},
    tracks_{consumes<pat::CompositeCandidateCollection>(cfg.getParameter<edm::InputTag>("tracks"))},
    ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("transientTracks") )},
    beamspot_{consumes<reco::BeamSpot>( cfg.getParameter<edm::InputTag>("beamSpot") )}
  {
    //output
    produces<pat::CompositeCandidateCollection>();
  }

  ~ZToPsi2MuBuilder() override {}

  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions &descriptions) {}

private:

  const edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> bFieldToken_;

  // selections
  const StringCutObjectSelector<pat::Muon> l3_selection_;
  const StringCutObjectSelector<pat::Muon> l4_selection_;
  const StringCutObjectSelector<pat::CompositeCandidate> pre_vtx_selection_; 
  const StringCutObjectSelector<pat::CompositeCandidate> post_vtx_selection_; 
  // inputs
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> psi2s_;
  const edm::EDGetTokenT<pat::MuonCollection> leptonsrc_;
  const edm::EDGetTokenT<TransientTrackCollection> leptons_ttracks_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> tracks_;
  const edm::EDGetTokenT<TransientTrackCollection> ttracks_;
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_;

};

void ZToPsi2MuBuilder::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &iSetup) const {

  //input
  edm::Handle<pat::CompositeCandidateCollection> psi2s;
  evt.getByToken(psi2s_, psi2s);

  edm::Handle<pat::MuonCollection> leptons;
  evt.getByToken(leptonsrc_, leptons);
  
  edm::Handle<TransientTrackCollection> leptons_ttracks;
  evt.getByToken(leptons_ttracks_, leptons_ttracks);

  edm::Handle<pat::CompositeCandidateCollection> tracks;
  evt.getByToken(tracks_, tracks);
  edm::Handle<TransientTrackCollection> ttracks;
  evt.getByToken(ttracks_, ttracks);
  
  edm::Handle<reco::BeamSpot> beamspot;
  evt.getByToken(beamspot_, beamspot);

  edm::ESHandle<MagneticField> fieldHandle;
  const auto& bField = iSetup.getData(bFieldToken_);
  AnalyticalImpactPointExtrapolator extrapolator(&bField);

  // output
  std::unique_ptr<pat::CompositeCandidateCollection> ret_val(new pat::CompositeCandidateCollection());

  // loop over Psi(2S) candidates
  for (size_t psi_idx = 0; psi_idx < psi2s->size(); ++psi_idx) {
    edm::Ptr<pat::CompositeCandidate> psi_ptr(psi2s, psi_idx);

    // get the Psi(2S) daughter indices (from J/psi->2mu + 2pi)
    edm::Ptr<reco::Candidate> l1_ptr = psi_ptr->userCand("l1");
    edm::Ptr<reco::Candidate> l2_ptr = psi_ptr->userCand("l2");
    edm::Ptr<reco::Candidate> trk1_ptr = psi_ptr->userCand("trk1");
    edm::Ptr<reco::Candidate> trk2_ptr = psi_ptr->userCand("trk2");

    int l1_idx = psi_ptr->userInt("l1_idx");   // first muon from J/psi
    int l2_idx = psi_ptr->userInt("l2_idx");   // second muon from J/psi
    int trk1_idx = psi_ptr->userInt("trk1_idx"); // first pion
    int trk2_idx = psi_ptr->userInt("trk2_idx"); // second pion

    pat::CompositeCandidate cand;
    math::PtEtaPhiMLorentzVector l1_p4(
            l1_ptr->pt(),
            l1_ptr->eta(),
            l1_ptr->phi(),
            MUON_MASS
        );

    math::PtEtaPhiMLorentzVector l2_p4(
            l2_ptr->pt(),
            l2_ptr->eta(),
            l2_ptr->phi(),
            MUON_MASS
        );

    math::PtEtaPhiMLorentzVector trk1_p4(
            trk1_ptr->pt(),
            trk1_ptr->eta(),
            trk1_ptr->phi(),
            PI_MASS
        );
    math::PtEtaPhiMLorentzVector trk2_p4(
            trk2_ptr->pt(),
            trk2_ptr->eta(),
            trk2_ptr->phi(),
            PI_MASS
        );


    // loop over muon candidates (select extra 2 muons)
    for (size_t l3_idx = 0; l3_idx < leptons->size(); ++l3_idx) {
      if (l3_idx == static_cast<size_t>(l1_idx) || l3_idx == static_cast<size_t>(l2_idx)) continue; // skip the muons from Psi(2S)
      edm::Ptr<pat::Muon> l3_ptr(leptons, l3_idx);
      if (!l3_selection_(*l3_ptr)) continue;

      for (size_t l4_idx = l3_idx + 1; l4_idx < leptons->size(); ++l4_idx) {
        if (l4_idx == static_cast<size_t>(l1_idx) || l4_idx == static_cast<size_t>(l2_idx)) continue; // skip the muons from Psi(2S)
        edm::Ptr<pat::Muon> l4_ptr(leptons, l4_idx);
        if (!l4_selection_(*l4_ptr)) continue;
        if ((l3_ptr->charge() + l4_ptr->charge())!=0) continue;


        math::PtEtaPhiMLorentzVector l3_p4(
          l3_ptr->pt(),
          l3_ptr->eta(),
          l3_ptr->phi(),
          MUON_MASS
        );
        math::PtEtaPhiMLorentzVector l4_p4(
          l4_ptr->pt(),
          l4_ptr->eta(),
          l4_ptr->phi(),
          MUON_MASS
        );

      auto zp4 = l1_p4 + l2_p4 + trk1_p4 + trk2_p4 + l3_p4 + l4_p4;
      cand.setP4(zp4);
      cand.setCharge(psi_ptr->charge() + l3_ptr->charge() + l4_ptr->charge());

      // save daughters - unfitted
      cand.addUserCand("l1", psi_ptr->userCand("l1"));   // mu1 from J/psi
      cand.addUserCand("l2", psi_ptr->userCand("l2"));   // mu2 from J/psi
      cand.addUserCand("trk1", psi_ptr->userCand("trk1")); // pi1
      cand.addUserCand("trk2", psi_ptr->userCand("trk2")); // pi2
      cand.addUserCand("l3", l3_ptr);   // mu3 from Z directly
      cand.addUserCand("l4", l4_ptr);   // mu4 from Z directly
      cand.addUserCand("psi2s", psi_ptr);

      // save indices
      cand.addUserInt("l1_idx", l1_idx);
      cand.addUserInt("l2_idx", l2_idx);
      cand.addUserInt("trk1_idx", trk1_idx);
      cand.addUserInt("trk2_idx", trk2_idx);
      cand.addUserInt("l3_idx", l3_idx);
      cand.addUserInt("l4_idx", l4_idx);
      cand.addUserInt("psi2s_idx", psi_idx);

      cand.addUserFloat("trk1_mass", psi_ptr->userCand("trk1")->mass());
      cand.addUserFloat("trk2_mass", psi_ptr->userCand("trk2")->mass());

      // save the Psi(2S) fitted quantities
      cand.addUserFloat("psi2s_fitted_mass", psi_ptr->userFloat("fitted_mass"));
      cand.addUserFloat("psi2s_fitted_pt", psi_ptr->userFloat("fitted_pt"));
      cand.addUserFloat("psi2s_fitted_eta", psi_ptr->userFloat("fitted_eta"));
      cand.addUserFloat("psi2s_fitted_phi", psi_ptr->userFloat("fitted_phi"));

      auto dr_info = min_max_dr({psi_ptr->userCand("l1"), psi_ptr->userCand("l2"),
                                  psi_ptr->userCand("trk1"), psi_ptr->userCand("trk2"),
                                  l3_ptr, l4_ptr});
      cand.addUserFloat("min_dr", dr_info.first);
      cand.addUserFloat("max_dr", dr_info.second);

      // check if pass pre vertex cut
      if ( !pre_vtx_selection_(cand) ) continue;

      // six-track vertex fit: [mu1, mu2, pi1, pi2, mu3, mu4]
      KinVtxFitter fitter(
        { leptons_ttracks->at(l1_idx),
          leptons_ttracks->at(l2_idx),
          ttracks->at(trk1_idx),
          ttracks->at(trk2_idx),
          leptons_ttracks->at(l3_idx),
          leptons_ttracks->at(l4_idx) },
        { MUON_MASS, MUON_MASS, PI_MASS, PI_MASS, MUON_MASS, MUON_MASS },
        { LEP_SIGMA, LEP_SIGMA, PI_SIGMA, PI_SIGMA, LEP_SIGMA, LEP_SIGMA }
      );

      if (!fitter.success()) continue;

      // Z vertex
      cand.setVertex(
        reco::Candidate::Point(
          fitter.fitted_vtx().x(),
          fitter.fitted_vtx().y(),
          fitter.fitted_vtx().z()
        )
      );

      // vertex vars
      cand.addUserFloat("sv_chi2", fitter.chi2());
      cand.addUserFloat("sv_ndof", fitter.dof());
      cand.addUserFloat("sv_prob", fitter.prob());

      // refitted kinematic vars
      cand.addUserFloat("fitted_dilepton_mass",
                        (fitter.daughter_p4(4) + fitter.daughter_p4(5)).mass());
      cand.addUserFloat("fitted_psi2s_mass",
                        (fitter.daughter_p4(0) + fitter.daughter_p4(1) +
                         fitter.daughter_p4(2) + fitter.daughter_p4(3)).mass());
      cand.addUserFloat("fitted_mll_jpsi",
                        (fitter.daughter_p4(0) + fitter.daughter_p4(1)).mass());
      cand.addUserFloat("fitted_ditrack_mass",
                        (fitter.daughter_p4(2) + fitter.daughter_p4(3)).mass());

      auto fit_p4 = fitter.fitted_p4();
      cand.addUserFloat("fitted_pt"  , fit_p4.pt());
      cand.addUserFloat("fitted_eta" , fit_p4.eta());
      cand.addUserFloat("fitted_phi" , fit_p4.phi());
      cand.addUserFloat("fitted_mass", fit_p4.mass());
      cand.addUserFloat("fitted_massErr",
                        sqrt(fitter.fitted_candidate().kinematicParametersError().matrix()(6, 6)));
      cand.addUserFloat("fitted_rapidity", fit_p4.Rapidity());

      // other vars
      cand.addUserFloat("cos_theta_2D",
                        cos_theta_2D(fitter, *beamspot, cand.p4()));

      cand.addUserFloat("fitted_cos_theta_2D",
                        cos_theta_2D(fitter, *beamspot, fit_p4));

      auto lxy = l_xy(fitter, *beamspot);
      cand.addUserFloat("l_xy", lxy.value());
      cand.addUserFloat("l_xy_unc", lxy.error());

      // post fit selection
      if ( !post_vtx_selection_(cand) ) continue;

      cand.addUserFloat("vtx_x", cand.vx());
      cand.addUserFloat("vtx_y", cand.vy());
      cand.addUserFloat("vtx_z", cand.vz());

      const auto& covMatrix = fitter.fitted_vtx_uncertainty();
      cand.addUserFloat("vtx_cxx", covMatrix.cxx());
      cand.addUserFloat("vtx_cyy", covMatrix.cyy());
      cand.addUserFloat("vtx_czz", covMatrix.czz());
      cand.addUserFloat("vtx_cyx", covMatrix.cyx());
      cand.addUserFloat("vtx_czx", covMatrix.czx());
      cand.addUserFloat("vtx_czy", covMatrix.czy());

      // refitted daughters
      std::vector<std::string> dnames{ "l1", "l2", "trk1", "trk2", "l3", "l4" };

      for (size_t idaughter = 0; idaughter < dnames.size(); idaughter++) {
        cand.addUserFloat("fitted_" + dnames[idaughter] + "_pt" , fitter.daughter_p4(idaughter).pt() );
        cand.addUserFloat("fitted_" + dnames[idaughter] + "_eta", fitter.daughter_p4(idaughter).eta() );
        cand.addUserFloat("fitted_" + dnames[idaughter] + "_phi", fitter.daughter_p4(idaughter).phi() );
      }

      // track impact parameter from Z SV
      TrajectoryStateOnSurface tsos1 = extrapolator.extrapolate(ttracks->at(trk1_idx).impactPointState(), fitter.fitted_vtx());
      std::pair<bool, Measurement1D> cur2DIP1 = signedTransverseImpactParameter(tsos1, fitter.fitted_refvtx(), *beamspot);
      cand.addUserFloat("trk1_svip2d" , cur2DIP1.second.value());
      cand.addUserFloat("trk1_svip2d_err" , cur2DIP1.second.error());

      TrajectoryStateOnSurface tsos2 = extrapolator.extrapolate(ttracks->at(trk2_idx).impactPointState(), fitter.fitted_vtx());
      std::pair<bool, Measurement1D> cur2DIP2 = signedTransverseImpactParameter(tsos2, fitter.fitted_refvtx(), *beamspot);
      cand.addUserFloat("trk2_svip2d" , cur2DIP2.second.value());
      cand.addUserFloat("trk2_svip2d_err" , cur2DIP2.second.error());

      //compute isolation
      std::vector<float> isos = TrackerIsolation(tracks, cand, dnames );
      for (size_t idaughter = 0; idaughter < dnames.size(); idaughter++) {
        cand.addUserFloat(dnames[idaughter] + "_iso04", isos[idaughter]);
      }

      ret_val->push_back(cand);

      } // for (size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx) {
    } // for (size_t psi_idx = 0; psi_idx < psi2s->size(); ++psi_idx) {
  }
  evt.put(std::move(ret_val));
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(ZToPsi2MuBuilder);


import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *

########################### Z -> Psi(2S) + 2mu -> (J/psi -> 2mu) + 2pi + 2mu ###########################

ZToPsi2Mu = cms.EDProducer(
    'ZToPsi2MuBuilder',
    PsiToJpsi2Pi = cms.InputTag("PsiToJpsi2Pi"),
    leptonsrc = cms.InputTag('muonBPH', 'AllMuons'),
    leptonTransientTracks = cms.InputTag('muonBPH', 'AllTransientMuons'),
    tracks = cms.InputTag('tracksBPH', 'SelectedTracks'),
    transientTracks = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    beamSpot = cms.InputTag("offlineBeamSpot"),
    lep3Selection = cms.string('pt > 2 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon '),
    lep4Selection = cms.string('pt > 2 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon '),
    preVtxSelection  = cms.string('pt > 10. && charge() == 0 && ((mass > 40. && mass < 140.)) '),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.0 && userFloat("fitted_mass") > 40. && userFloat("fitted_mass") < 140.'),
)

########################### Tables ###########################

ZToPsi2MuTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag("ZToPsi2Mu"),
    cut       = cms.string(""),
    name      = cms.string("ZToPsi2Mu"),
    doc       = cms.string("ZToPsi2Mu Variables"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        # pre-fit quantities
        CandVars,
        l1_idx      = uint('l1_idx'),
        l2_idx      = uint('l2_idx'),
        trk1_idx    = uint('trk1_idx'),
        trk2_idx    = uint('trk2_idx'),
        l3_idx      = uint('l3_idx'),
        l4_idx      = uint('l4_idx'),
        psi2s_idx   = uint('psi2s_idx'),
        trk1_mass   = ufloat('trk1_mass'),
        trk2_mass   = ufloat('trk2_mass'),
        min_dr      = ufloat('min_dr'),
        max_dr      = ufloat('max_dr'),
        # Psi(2S) fitted quantities
        psi2s_fitted_mass = ufloat('psi2s_fitted_mass'),
        psi2s_fitted_pt   = ufloat('psi2s_fitted_pt'),
        psi2s_fitted_eta  = ufloat('psi2s_fitted_eta'),
        psi2s_fitted_phi  = ufloat('psi2s_fitted_phi'),
        # vtx info
        chi2      = ufloat('sv_chi2'),
        svprob    = ufloat('sv_prob'),
        sv_ndof   = ufloat('sv_ndof'),
        cos2D     = ufloat('cos_theta_2D'),
        fit_cos2D = ufloat('fitted_cos_theta_2D'),
        l_xy      = ufloat('l_xy'),
        l_xy_unc  = ufloat('l_xy_unc'),
        # post-fit masses
        mll_dilepton_fullfit = ufloat('fitted_dilepton_mass'),
        mpsi2s_fullfit       = ufloat('fitted_psi2s_mass'),
        mll_jpsi_fullfit     = ufloat('fitted_mll_jpsi'),
        mtrktrk_fullfit      = ufloat('fitted_ditrack_mass'),
        fitted_mass       = ufloat('fitted_mass'),
        fitted_massErr    = ufloat('fitted_massErr'),
        fitted_pt         = ufloat('fitted_pt'),
        fitted_eta        = ufloat('fitted_eta'),
        fitted_phi        = ufloat('fitted_phi'),
        fitted_rapidity   = ufloat('fitted_rapidity'),
        # vertex
        vtx_x   = ufloat('vtx_x'),
        vtx_y   = ufloat('vtx_y'),
        vtx_z   = ufloat('vtx_z'),
        vtx_cxx = ufloat('vtx_cxx'),
        vtx_cyy = ufloat('vtx_cyy'),
        vtx_czz = ufloat('vtx_czz'),
        vtx_cyx = ufloat('vtx_cyx'),
        vtx_czx = ufloat('vtx_czx'),
        vtx_czy = ufloat('vtx_czy'),
        # post-fit tracks/leptons (daughters 0-5: l1,l2,trk1,trk2,l3,l4)
        fit_l1_pt  = ufloat('fitted_l1_pt'),
        fit_l1_eta = ufloat('fitted_l1_eta'),
        fit_l1_phi = ufloat('fitted_l1_phi'),
        fit_l2_pt  = ufloat('fitted_l2_pt'),
        fit_l2_eta = ufloat('fitted_l2_eta'),
        fit_l2_phi = ufloat('fitted_l2_phi'),
        fit_trk1_pt  = ufloat('fitted_trk1_pt'),
        fit_trk1_eta = ufloat('fitted_trk1_eta'),
        fit_trk1_phi = ufloat('fitted_trk1_phi'),
        fit_trk2_pt  = ufloat('fitted_trk2_pt'),
        fit_trk2_eta = ufloat('fitted_trk2_eta'),
        fit_trk2_phi = ufloat('fitted_trk2_phi'),
        fit_l3_pt  = ufloat('fitted_l3_pt'),
        fit_l3_eta = ufloat('fitted_l3_eta'),
        fit_l3_phi = ufloat('fitted_l3_phi'),
        fit_l4_pt  = ufloat('fitted_l4_pt'),
        fit_l4_eta = ufloat('fitted_l4_eta'),
        fit_l4_phi = ufloat('fitted_l4_phi'),
        # isolation
        l1_iso04   = ufloat('l1_iso04'),
        l2_iso04   = ufloat('l2_iso04'),
        trk1_iso04 = ufloat('trk1_iso04'),
        trk2_iso04 = ufloat('trk2_iso04'),
        l3_iso04   = ufloat('l3_iso04'),
        l4_iso04   = ufloat('l4_iso04'),
        trk1_svip2d     = ufloat('trk1_svip2d'),
        trk1_svip2d_err = ufloat('trk1_svip2d_err'),
        trk2_svip2d     = ufloat('trk2_svip2d'),
        trk2_svip2d_err = ufloat('trk2_svip2d_err'),
    )
)

CountZToPsi2Mu = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag("ZToPsi2Mu")
)

ZToPsi2MuBPHMCMatch = cms.EDProducer("MCMatcher",                  # cut on deltaR, deltaPt/Pt; pick best by deltaR
    src         = ZToPsi2MuTable.src,                           # final reco collection
    matched     = cms.InputTag("finalGenParticlesBPH"),       # final mc-truth particle collection
    mcPdgId     = cms.vint32(23),                             # one or more PDG ID (23 = Z boson)
    checkCharge = cms.bool(False),                            # True = require RECO and MC objects to have the same charge
    mcStatus    = cms.vint32(22),                              # PYTHIA status code (1 = stable, 2 = shower, 3 = hard scattering)
    maxDeltaR   = cms.double(0.1),                           # Minimum deltaR for the match
    maxDPtRel   = cms.double(0.5),                            # Minimum deltaPt/Pt for the match
    resolveAmbiguities    = cms.bool(True),                   # Forbid two RECO objects to match to the same GEN object
    resolveByMatchQuality = cms.bool(True),                   # False = just match input in order; True = pick lowest deltaR pair first
)

ZToPsi2MuBPHMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects = ZToPsi2MuTable.src,
    genParts    = cms.InputTag("finalGenParticlesBPH"),
    mcMap       = cms.InputTag("ZToPsi2MuBPHMCMatch"),
    objName     = ZToPsi2MuTable.name,
    objType     = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("ZToPsi2Mu"),
    docString   = cms.string("MC matching to status==2 Z boson"),
)

########################### Sequences  ############################
ZToPsi2MuSequence = cms.Sequence( ZToPsi2Mu  )
ZToPsi2MuTables   = cms.Sequence( ZToPsi2MuTable )
ZToPsi2MuMCSequence = cms.Sequence( ZToPsi2Mu + ZToPsi2MuBPHMCMatch )
ZToPsi2MuMCTables   = cms.Sequence( ZToPsi2MuTable + ZToPsi2MuBPHMCTable )
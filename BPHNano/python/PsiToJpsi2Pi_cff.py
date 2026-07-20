import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *

########################### Psi(2S) -> Jpsi + 2pion ###########################

PsiToJpsi2Pi = cms.EDProducer(
    'PsiToJpsi2PiBuilder',
    dileptons = cms.InputTag("JpsiMuMu:SelectedDiLeptons"),
    leptonTransientTracks = cms.InputTag('muonBPH', 'AllTransientMuons'),
    tracks = cms.InputTag('tracksBPH', 'SelectedTracks'),
    transientTracks = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    beamSpot = cms.InputTag("offlineBeamSpot"),
    trk1Selection   = cms.string('pt > 1.0 && abs(eta) < 2.5 '),
    trk2Selection   = cms.string('pt > 1.0 && abs(eta) < 2.5 '),
    preVtxSelection  = cms.string('pt > 5. && charge() == 0 && ((mass > 3.0 && mass < 4.4)) '),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.0 && userFloat("fitted_mass") > 3.0 && userFloat("fitted_mass") < 4.4'),
)

########################### Tables ###########################

PsiToJpsi2PiTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag("PsiToJpsi2Pi"),
    cut       = cms.string(""),
    name      = cms.string("PsiToJpsi2Pi"),
    doc       = cms.string("PsiToJpsi2Pi Variables"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        # pre-fit quantities
        CandVars,
        l1_idx      = uint('l1_idx'),
        l2_idx      = uint('l2_idx'),
        ll_idx   = uint('ll_idx'),
        trk1_idx    = uint('trk1_idx'),
        trk2_idx    = uint('trk2_idx'),
        trk1_mass   = ufloat('trk1_mass'),
        trk2_mass   = ufloat('trk2_mass'),
        min_dr      = ufloat('min_dr'),
        max_dr      = ufloat('max_dr'),
        # vtx info
        chi2      = ufloat('sv_chi2'),
        svprob    = ufloat('sv_prob'),
        cos2D     = ufloat('cos_theta_2D'),
        fit_cos2D = ufloat('fitted_cos_theta_2D'),
        l_xy      = ufloat('l_xy'),
        l_xy_unc  = ufloat('l_xy_unc'),
        # post-fit momentum /masses
        mll_fullfit    = ufloat('fitted_mll'),
        mtrktrk_fullfit = ufloat('fitted_ditrack_mass'),
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
        # post-fit tracks/leptons
        #l1
        fit_l1_pt  = ufloat('fitted_l1_pt'),
        fit_l1_eta = ufloat('fitted_l1_eta'),
        fit_l1_phi = ufloat('fitted_l1_phi'),
        #l2
        fit_l2_pt  = ufloat('fitted_l2_pt'),
        fit_l2_eta = ufloat('fitted_l2_eta'),
        fit_l2_phi = ufloat('fitted_l2_phi'),
        #lambda
        fit_trk1_pt  = ufloat('fitted_trk1_pt'),
        fit_trk1_eta = ufloat('fitted_trk1_eta'),
        fit_trk1_phi = ufloat('fitted_trk1_phi'),
        fit_trk2_pt  = ufloat('fitted_trk2_pt'),
        fit_trk2_eta = ufloat('fitted_trk2_eta'),
        fit_trk2_phi = ufloat('fitted_trk2_phi'),
        # isolation 
        l1_iso04   = ufloat('l1_iso04'),
        l2_iso04   = ufloat('l2_iso04'),
        trk1_iso04 = ufloat('trk1_iso04'),
        trk2_iso04 = ufloat('trk2_iso04'),
        trk1_svip2d     = ufloat('trk1_svip2d'),
        trk1_svip2d_err = ufloat('trk1_svip2d_err'),
        trk2_svip2d     = ufloat('trk2_svip2d'),
        trk2_svip2d_err = ufloat('trk2_svip2d_err'),
    )
)

CountPsiToJpsi2Pi = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag("PsiToJpsi2Pi")
)

PsiToJpsi2PiBPHMCMatch = cms.EDProducer("MCMatcher",                  # cut on deltaR, deltaPt/Pt; pick best by deltaR
    src         = PsiToJpsi2PiTable.src,                           # final reco collection
    matched     = cms.InputTag("finalGenParticlesBPH"),       # final mc-truth particle collection
    mcPdgId     = cms.vint32(443, 100443),                             # one or more PDG ID (443 = J/psi); absolute values (see below)
    checkCharge = cms.bool(False),                            # True = require RECO and MC objects to have the same charge
    mcStatus    = cms.vint32(22),                              # PYTHIA status code (1 = stable, 2 = shower, 3 = hard scattering)
    maxDeltaR   = cms.double(0.1),                           # Minimum deltaR for the match
    maxDPtRel   = cms.double(0.5),                            # Minimum deltaPt/Pt for the match
    resolveAmbiguities    = cms.bool(True),                   # Forbid two RECO objects to match to the same GEN object
    resolveByMatchQuality = cms.bool(True),                   # False = just match input in order; True = pick lowest deltaR pair first
)

PsiToJpsi2PiBPHMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects = PsiToJpsi2PiTable.src,
    genParts    = cms.InputTag("finalGenParticlesBPH"),
    mcMap       = cms.InputTag("PsiToJpsi2PiBPHMCMatch"),
    objName     = PsiToJpsi2PiTable.name,
    objType     = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("PsiToJpsi2Pi"),
    docString   = cms.string("MC matching to status==2 eta or eta'"),
)

########################### Sequencies  ############################
PsiToJpsi2PiSequence = cms.Sequence( PsiToJpsi2Pi  )
PsiToJpsi2PiTables   = cms.Sequence( PsiToJpsi2PiTable )
PsiToJpsi2PiMCSequence = cms.Sequence( PsiToJpsi2Pi + PsiToJpsi2PiBPHMCMatch )
PsiToJpsi2PiMCTables   = cms.Sequence( PsiToJpsi2PiTable + PsiToJpsi2PiBPHMCTable )

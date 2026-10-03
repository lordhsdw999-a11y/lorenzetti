#include "ElectronMaker.h"
#include "G4Kernel/CaloPhiRange.h"
#include "CaloCell/CaloCell.h"
#include "CaloCluster/CaloCluster.h"
#include "G4PhysicalConstants.hh"
#include "G4SystemOfUnits.hh"
#include "TH1F.h"
#include "TMath.h"

using namespace SG;
using namespace Gaugi;

/**
 * @class ElectronMaker
 * @brief Reconstructs Electron objects from CaloClusters.
 * 
 * Creates electron candidates by iterating over calorimeter clusters.
 * Performs PID (particle identification) evaluation using "IsEM" style
 * rectangular cuts (Very Loose, Loose, Medium, Tight).
 */
ElectronMaker::ElectronMaker(std::string name) : 
  IMsgService(name),
  Algorithm(),
  m_outputLevel(1),
  m_clusterKey("Clusters"),
  m_electronKey("Electrons"),
  m_histPath("Expert/Electrons"),
  m_tightCuts(),
  m_mediumCuts(),
  m_looseCuts(),
  m_vlooseCuts(),
  m_secondLambdaCuts(),
  m_lateralMomCuts(),
  m_longMomCuts(),
  m_fracMaxCuts(),
  m_secondRCuts(),
  m_lambdaCenterCuts()
{
  declareProperty("InputClusterKey",   m_clusterKey);
  declareProperty("OutputElectronKey", m_electronKey);
  declareProperty("OutputLevel",       m_outputLevel);
  declareProperty("HistogramPath",     m_histPath);
  declareProperty("TightCuts",         m_tightCuts);
  declareProperty("MediumCuts",        m_mediumCuts);
  declareProperty("LooseCuts",         m_looseCuts);
  declareProperty("VLooseCuts",        m_vlooseCuts);
  declareProperty("SecondLambdaCuts",  m_secondLambdaCuts);
  declareProperty("LateralMomCuts",    m_lateralMomCuts);
  declareProperty("LongMomCuts",       m_longMomCuts);
  declareProperty("FracMaxCuts",       m_fracMaxCuts);
  declareProperty("SecondRCuts",       m_secondRCuts);
  declareProperty("LambdaCenterCuts",  m_lambdaCenterCuts);
}

//!=====================================================================

ElectronMaker::~ElectronMaker()
{
}

//!=====================================================================

StatusCode ElectronMaker::initialize()
{
  CHECK_INIT();
  setMsgLevel(m_outputLevel);

  // Validate central cut vector dimensions if provided
  if (!m_tightCuts.empty() && m_tightCuts.size() < 3) {
    MSG_FATAL("TightCuts vector must have at least 3 elements (rhad, reta, eratio). Found: " << m_tightCuts.size());
    return StatusCode::FAILURE;
  }
  if (!m_mediumCuts.empty() && m_mediumCuts.size() < 3) {
    MSG_FATAL("MediumCuts vector must have at least 3 elements (rhad, reta, eratio). Found: " << m_mediumCuts.size());
    return StatusCode::FAILURE;
  }
  if (!m_looseCuts.empty() && m_looseCuts.size() < 3) {
    MSG_FATAL("LooseCuts vector must have at least 3 elements (rhad, reta, eratio). Found: " << m_looseCuts.size());
    return StatusCode::FAILURE;
  }
  if (!m_vlooseCuts.empty() && m_vlooseCuts.size() < 3) {
    MSG_FATAL("VLooseCuts vector must have at least 3 elements (rhad, reta, eratio). Found: " << m_vlooseCuts.size());
    return StatusCode::FAILURE;
  }

  // Validate forward moment cut vectors (expect 3 working points: loose, medium, tight)
  if (!m_secondLambdaCuts.empty() && m_secondLambdaCuts.size() < 3) {
    MSG_FATAL("SecondLambdaCuts must have at least 3 elements. Found: " << m_secondLambdaCuts.size());
    return StatusCode::FAILURE;
  }
  if (!m_lateralMomCuts.empty() && m_lateralMomCuts.size() < 3) {
    MSG_FATAL("LateralMomCuts must have at least 3 elements. Found: " << m_lateralMomCuts.size());
    return StatusCode::FAILURE;
  }
  if (!m_longMomCuts.empty() && m_longMomCuts.size() < 3) {
    MSG_FATAL("LongMomCuts must have at least 3 elements. Found: " << m_longMomCuts.size());
    return StatusCode::FAILURE;
  }
  if (!m_fracMaxCuts.empty() && m_fracMaxCuts.size() < 3) {
    MSG_FATAL("FracMaxCuts must have at least 3 elements. Found: " << m_fracMaxCuts.size());
    return StatusCode::FAILURE;
  }
  if (!m_secondRCuts.empty() && m_secondRCuts.size() < 3) {
    MSG_FATAL("SecondRCuts must have at least 3 elements. Found: " << m_secondRCuts.size());
    return StatusCode::FAILURE;
  }
  if (!m_lambdaCenterCuts.empty() && m_lambdaCenterCuts.size() < 3) {
    MSG_FATAL("LambdaCenterCuts must have at least 3 elements. Found: " << m_lambdaCenterCuts.size());
    return StatusCode::FAILURE;
  }

  return StatusCode::SUCCESS;
}

//!=====================================================================

StatusCode ElectronMaker::bookHistograms(SG::EventContext &ctx) const
{
  auto store = ctx.getStoreGateSvc();
  store->mkdir(m_histPath);
  store->cd(m_histPath);

  store->add(new TH1F("el_e", "Electron Energy;E [GeV];Count", 100, 0.0, 100.0));
  store->add(new TH1F("el_et", "Electron Transverse Energy;E_{T} [GeV];Count", 100, 0.0, 100.0));
  store->add(new TH1F("el_eta", "Electron #eta;#eta;Count", 100, -5.0, 5.0));
  store->add(new TH1F("el_phi", "Electron #phi;#phi;Count", 64, -TMath::Pi(), TMath::Pi()));
  store->add(new TH1F("el_pid", "Electron PID Selection;Working Point;Count", 4, 0.0, 4.0));

  return StatusCode::SUCCESS;
}

//!=====================================================================

StatusCode ElectronMaker::pre_execute(EventContext &/*ctx*/) const
{
  return StatusCode::SUCCESS;
}

//!=====================================================================

StatusCode ElectronMaker::execute(EventContext &/*ctx*/, const G4Step * /*step*/) const
{
  return StatusCode::SUCCESS;
}

//!=====================================================================

StatusCode ElectronMaker::execute(EventContext &ctx, int /*evt*/) const
{
  return post_execute(ctx);
}

//!=====================================================================

StatusCode ElectronMaker::finalize()
{
  return StatusCode::SUCCESS;
}

//!=====================================================================

/**
 * @brief Executes the electron creation.
 * 
 * Iterates over the CaloCluster container. For each cluster, creates a new
 * `xAOD::Electron`, links it to the cluster, and calculates the PID decisions
 * (Very Loose, Loose, Medium, Tight).
 */
StatusCode ElectronMaker::post_execute(EventContext &ctx) const
{
  SG::WriteHandle<xAOD::ElectronContainer> electron(m_electronKey, ctx);
  electron.record(std::unique_ptr<xAOD::ElectronContainer>(new xAOD::ElectronContainer()));
  SG::ReadHandle<xAOD::CaloClusterContainer> clusters(m_clusterKey, ctx);

  if (!clusters.isValid()) {
    MSG_ERROR("Could not retrieve CaloClusterContainer with key: " << m_clusterKey);
    return StatusCode::FAILURE;
  }

  uint32_t clus_idx = 0;
  for (const auto clus : *clusters) {
    if (!clus) {
      clus_idx++;
      continue;
    }
    auto el = new xAOD::Electron();
    el->setEta(clus->eta());
    el->setPhi(clus->phi());
    el->setEt(clus->et());
    el->setE(clus->e());
    MSG_INFO("Cluster eta: " << el->eta() << " phi: " << el->phi() << " et: " << el->et() << " e: " << el->e());
    el->setCaloCluster(m_clusterKey, clus_idx, clus);

    bool isTight = false;
    bool isMedium = false;
    bool isLoose = false;
    bool isVeryLoose = false;

    evaluatePID(clus, isTight, isMedium, isLoose, isVeryLoose);

    el->setIsTight(isTight);
    el->setIsMedium(isMedium);
    el->setIsLoose(isLoose);
    el->setIsVeryLoose(isVeryLoose);

    electron->push_back(el);
    clus_idx++;
  }
  return StatusCode::SUCCESS;
}

//!=====================================================================

StatusCode ElectronMaker::fillHistograms(EventContext &ctx) const
{
  auto store = ctx.getStoreGateSvc();
  SG::ReadHandle<xAOD::ElectronContainer> electrons(m_electronKey, ctx);

  if (!electrons.isValid()) {
    MSG_WARNING("Could not read ElectronContainer with key: " << m_electronKey);
    return StatusCode::SUCCESS;
  }

  store->cd(m_histPath);
  for (const auto el : *electrons) {
    if (!el) continue;
    store->hist1("el_e")->Fill(el->e() / GeV);
    store->hist1("el_et")->Fill(el->et() / GeV);
    store->hist1("el_eta")->Fill(el->eta());
    store->hist1("el_phi")->Fill(el->phi());

    if (el->isVeryLoose()) store->hist1("el_pid")->Fill(0.5);
    if (el->isLoose())     store->hist1("el_pid")->Fill(1.5);
    if (el->isMedium())    store->hist1("el_pid")->Fill(2.5);
    if (el->isTight())     store->hist1("el_pid")->Fill(3.5);
  }

  return StatusCode::SUCCESS;
}

//!=====================================================================

void ElectronMaker::evaluatePID(const xAOD::CaloCluster* cluster,
                                bool &isTight,
                                bool &isMedium,
                                bool &isLoose,
                                bool &isVeryLoose) const
{
  isTight = false;
  isMedium = false;
  isLoose = false;
  isVeryLoose = false;

  if (!cluster) return;

  if (cluster->isForward()) {
    // Forward region selection using shower moments
    if (m_secondLambdaCuts.size() >= 3 &&
        m_lateralMomCuts.size() >= 3 &&
        m_longMomCuts.size() >= 3 &&
        m_fracMaxCuts.size() >= 3 &&
        m_secondRCuts.size() >= 3 &&
        m_lambdaCenterCuts.size() >= 3)
    {
      // Index 0: Loose / VLoose
      bool passLoose = (cluster->secondLambda() <= m_secondLambdaCuts[0]) &&
                       (cluster->lateralMom() <= m_lateralMomCuts[0]) &&
                       (cluster->longitudinalMom() <= m_longMomCuts[0]) &&
                       (cluster->fracMax() >= m_fracMaxCuts[0]) &&
                       (cluster->secondR() <= m_secondRCuts[0]) &&
                       (cluster->lambdaCenter() <= m_lambdaCenterCuts[0]);

      // Index 1: Medium
      bool passMedium = (cluster->secondLambda() <= m_secondLambdaCuts[1]) &&
                        (cluster->lateralMom() <= m_lateralMomCuts[1]) &&
                        (cluster->longitudinalMom() <= m_longMomCuts[1]) &&
                        (cluster->fracMax() >= m_fracMaxCuts[1]) &&
                        (cluster->secondR() <= m_secondRCuts[1]) &&
                        (cluster->lambdaCenter() <= m_lambdaCenterCuts[1]);

      // Index 2: Tight
      bool passTight = (cluster->secondLambda() <= m_secondLambdaCuts[2]) &&
                       (cluster->lateralMom() <= m_lateralMomCuts[2]) &&
                       (cluster->longitudinalMom() <= m_longMomCuts[2]) &&
                       (cluster->fracMax() >= m_fracMaxCuts[2]) &&
                       (cluster->secondR() <= m_secondRCuts[2]) &&
                       (cluster->lambdaCenter() <= m_lambdaCenterCuts[2]);

      isVeryLoose = passLoose;
      isLoose = passLoose;
      isMedium = passMedium;
      isTight = passTight;
    }
  } else {
    // Central region selection using rhad, reta, eratio
    if (m_vlooseCuts.size() >= 3) {
      isVeryLoose = (cluster->rhad() <= m_vlooseCuts[0]) &&
                    (cluster->reta() >= m_vlooseCuts[1]) &&
                    (cluster->eratio() >= m_vlooseCuts[2]);
    }
    if (m_looseCuts.size() >= 3) {
      isLoose = (cluster->rhad() <= m_looseCuts[0]) &&
                (cluster->reta() >= m_looseCuts[1]) &&
                (cluster->eratio() >= m_looseCuts[2]);
    }
    if (m_mediumCuts.size() >= 3) {
      isMedium = (cluster->rhad() <= m_mediumCuts[0]) &&
                 (cluster->reta() >= m_mediumCuts[1]) &&
                 (cluster->eratio() >= m_mediumCuts[2]);
    }
    if (m_tightCuts.size() >= 3) {
      isTight = (cluster->rhad() <= m_tightCuts[0]) &&
                (cluster->reta() >= m_tightCuts[1]) &&
                (cluster->eratio() >= m_tightCuts[2]);
    }
  }
}

//!=====================================================================

bool ElectronMaker::compute(const xAOD::CaloCluster* cluster, std::string pidname) const
{
  bool isTight = false, isMedium = false, isLoose = false, isVeryLoose = false;
  evaluatePID(cluster, isTight, isMedium, isLoose, isVeryLoose);

  if (pidname == "tight")  return isTight;
  if (pidname == "medium") return isMedium;
  if (pidname == "loose")  return isLoose;
  if (pidname == "vloose") return isVeryLoose;

  MSG_DEBUG("Unknown working point: " << pidname << ". Rejecting by default");
  return false;
}

#include "CaloCluster/CaloCluster.h"
#include "CaloCell/CaloCellContainer.h"
#include "GaugiKernel/StringHash.h"
#include "GaugiKernel/EventContext.h"

using namespace xAOD;

CaloCluster::CaloCluster() :
  EDM(),
  m_e(0.0),
  m_et(0.0),
  m_e0(0.0),
  m_e1(0.0),
  m_e2(0.0),
  m_e3(0.0),
  m_ehad1(0.0),
  m_ehad2(0.0),
  m_ehad3(0.0),
  m_etot(0.0),
  m_e233(0.0),
  m_e237(0.0),
  m_e277(0.0),
  m_emaxs1(0.0),
  m_emaxs2(0.0),
  m_e2tsts1(0.0),
  m_reta(0.0),
  m_rphi(0.0),
  m_rhad(0.0),
  m_rhad1(0.0),
  m_eratio(0.0),
  m_f0(0.0),
  m_f1(0.0),
  m_f2(0.0),
  m_f3(0.0),
  m_weta2(0.0),
  m_eta(0.0),
  m_phi(0.0),
  m_deta(0.0),
  m_dphi(0.0),
  m_secondR(0.0),
  m_lambdaCenter(0.0),
  m_secondLambda(0.0),
  m_fracMax(0.0),
  m_lateralMom(0.0),
  m_longitudinalMom(0.0),
  m_cellsKeyHash(0),
  m_cellIndices(),
  m_container(),
  m_seedLink()
{
  m_seedLink.setOwner(this);
}

CaloCluster::CaloCluster(float emaxs2, float eta, float phi, float deta, float dphi) :
  EDM(),
  m_e(0.0),
  m_et(0.0),
  m_e0(0.0),
  m_e1(0.0),
  m_e2(0.0),
  m_e3(0.0),
  m_ehad1(0.0),
  m_ehad2(0.0),
  m_ehad3(0.0),
  m_etot(0.0),
  m_e233(0.0),
  m_e237(0.0),
  m_e277(0.0),
  m_emaxs1(0.0),
  m_emaxs2(emaxs2),
  m_e2tsts1(0.0),
  m_reta(0.0),
  m_rphi(0.0),
  m_rhad(0.0),
  m_rhad1(0.0),
  m_eratio(0.0),
  m_f0(0.0),
  m_f1(0.0),
  m_f2(0.0),
  m_f3(0.0),
  m_weta2(0.0),
  m_eta(eta),
  m_phi(phi),
  m_deta(deta),
  m_dphi(dphi),
  m_secondR(0.0),
  m_lambdaCenter(0.0),
  m_secondLambda(0.0),
  m_fracMax(0.0),
  m_lateralMom(0.0),
  m_longitudinalMom(0.0),
  m_cellsKeyHash(0),
  m_cellIndices(),
  m_container(),
  m_seedLink()
{
  m_seedLink.setOwner(this);
}

CaloCluster::~CaloCluster()
{}

void CaloCluster::clear() {
  m_container.clear();
  m_cellIndices.clear();
}

void CaloCluster::push_back(const xAOD::CaloCell *cell) {
  if (cell) {
    m_container.push_back(cell);
  }
}

void CaloCluster::push_back(uint32_t index, const xAOD::CaloCell *cell) {
  m_cellIndices.push_back(index);
  if (cell) {
    m_container.push_back(cell);
  }
}

size_t CaloCluster::size() const { 
  if (!m_container.empty()) {
    return m_container.size();
  }
  return m_cellIndices.size();
}

void CaloCluster::setCellsContainerKey(const std::string &key) {
  m_cellsKeyHash = Gaugi::stringHash(key);
}

void CaloCluster::setCellsContainerKey(uint64_t keyHash) {
  m_cellsKeyHash = keyHash;
}

const std::vector<const xAOD::CaloCell*>& CaloCluster::cells() const {
  if (m_container.empty() && !m_cellIndices.empty() && m_cellsKeyHash != 0) {
    const auto *ctx = eventContext();
    if (ctx) {
      const auto *cellContainer = ctx->get<xAOD::CaloCellContainer>(m_cellsKeyHash);
      if (cellContainer) {
        m_container.reserve(m_cellIndices.size());
        for (uint32_t idx : m_cellIndices) {
          if (idx < cellContainer->size()) {
            m_container.push_back(cellContainer->at(idx));
          }
        }
      }
    }
  }
  return m_container;
}

const xAOD::Seed* CaloCluster::seed() const {
  m_seedLink.setOwner(this);
  return m_seedLink.get();
}

void CaloCluster::setSeed(const xAOD::Seed* seed) {
  m_seedLink = SG::ElementLink<xAOD::Seed>("", 0, seed, this);
}

void CaloCluster::setSeed(const std::string& key, uint32_t index, const xAOD::Seed* seed) {
  m_seedLink = SG::ElementLink<xAOD::Seed>(key, index, seed, this);
}

void CaloCluster::setSeed(uint64_t keyHash, uint32_t index, const xAOD::Seed* seed) {
  m_seedLink = SG::ElementLink<xAOD::Seed>(keyHash, index, this);
  if (seed) {
    m_seedLink.setElement(keyHash, index, seed);
  }
}

void CaloCluster::setSeed(const SG::ElementLink<xAOD::Seed>& link) {
  m_seedLink = link;
  m_seedLink.setOwner(this);
}

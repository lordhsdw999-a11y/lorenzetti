#include "CaloRings/CaloRings.h"

using namespace xAOD;

CaloRings::CaloRings() :
  EDM(),
  m_caloCluster(),
  m_eta(0.0),
  m_phi(0.0)
{
  m_caloCluster.setOwner(this);
}

void CaloRings::setCaloCluster(const xAOD::CaloCluster *clus) {
  m_caloCluster = SG::ElementLink<xAOD::CaloCluster>("", 0, clus, this);
}

void CaloRings::setCaloCluster(const std::string& key, uint32_t index, const xAOD::CaloCluster* clus) {
  m_caloCluster = SG::ElementLink<xAOD::CaloCluster>(key, index, clus, this);
}

void CaloRings::setCaloCluster(uint64_t keyHash, uint32_t index, const xAOD::CaloCluster* clus) {
  m_caloCluster = SG::ElementLink<xAOD::CaloCluster>(keyHash, index, this);
  if (clus) {
    m_caloCluster.setElement(keyHash, index, clus);
  }
}

void CaloRings::setCaloCluster(const SG::ElementLink<xAOD::CaloCluster>& link) {
  m_caloCluster = link;
  m_caloCluster.setOwner(this);
}

const xAOD::CaloCluster* CaloRings::caloCluster() const {
  m_caloCluster.setOwner(this);
  return m_caloCluster.get();
}

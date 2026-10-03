#include "Egamma/Electron.h"

using namespace xAOD;

Electron::Electron() :
  EDM(),
  m_e(0.0),
  m_et(0.0),
  m_eta(0.0),
  m_phi(0.0),
  m_isEM(4, false),
  m_caloCluster()
{
  m_caloCluster.setOwner(this);
}

void Electron::setCaloCluster(const xAOD::CaloCluster *clus) {
  m_caloCluster = SG::ElementLink<xAOD::CaloCluster>("", 0, clus, this);
}

void Electron::setCaloCluster(const std::string& key, uint32_t index, const xAOD::CaloCluster* clus) {
  m_caloCluster = SG::ElementLink<xAOD::CaloCluster>(key, index, clus, this);
}

void Electron::setCaloCluster(uint64_t keyHash, uint32_t index, const xAOD::CaloCluster* clus) {
  m_caloCluster = SG::ElementLink<xAOD::CaloCluster>(keyHash, index, this);
  if (clus) {
    m_caloCluster.setElement(keyHash, index, clus);
  }
}

void Electron::setCaloCluster(const SG::ElementLink<xAOD::CaloCluster>& link) {
  m_caloCluster = link;
  m_caloCluster.setOwner(this);
}

const xAOD::CaloCluster* Electron::caloCluster() const {
  m_caloCluster.setOwner(this);
  return m_caloCluster.get();
}

bool Electron::isTight() const {
  return m_isEM[0];
}

bool Electron::isMedium() const {
  return m_isEM[1];
}

bool Electron::isLoose() const {
  return m_isEM[2];
}

bool Electron::isVeryLoose() const {
  return m_isEM[3];
}

void Electron::setIsTight(bool isTight) {
  m_isEM[0] = isTight;
}

void Electron::setIsMedium(bool isMedium) {
  m_isEM[1] = isMedium;
}

void Electron::setIsLoose(bool isLoose) {
  m_isEM[2] = isLoose;
}

void Electron::setIsVeryLoose(bool isVeryLoose) {
  m_isEM[3] = isVeryLoose;
}

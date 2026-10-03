#include "CaloCell/CaloCell.h"

using namespace xAOD;

CaloCell::CaloCell() :
  EDM(),
  m_eta(0.0),
  m_phi(0.0),
  m_deta(0.0),
  m_dphi(0.0),
  m_e(0.0),
  m_et(0.0),
  m_tau(0.0),
  m_descriptorLink()
{
  m_descriptorLink.setOwner(this);
}

CaloCell::CaloCell(float eta, float phi, float deta, float dphi) :
  EDM(),
  m_eta(eta),
  m_phi(phi),
  m_deta(deta),
  m_dphi(dphi),
  m_e(0.0),
  m_et(0.0),
  m_tau(0.0),
  m_descriptorLink()
{
  m_descriptorLink.setOwner(this);
}

const xAOD::CaloDetDescriptor* CaloCell::descriptor() const {
  m_descriptorLink.setOwner(this);
  return m_descriptorLink.get();
}

void CaloCell::setDescriptor(const xAOD::CaloDetDescriptor *descriptor) {
  m_descriptorLink = SG::ElementLink<xAOD::CaloDetDescriptor>("", 0, descriptor, this);
}

void CaloCell::setDescriptor(const std::string& key, uint32_t index, const xAOD::CaloDetDescriptor* descriptor) {
  m_descriptorLink = SG::ElementLink<xAOD::CaloDetDescriptor>(key, index, descriptor, this);
}

void CaloCell::setDescriptor(uint64_t keyHash, uint32_t index, const xAOD::CaloDetDescriptor* descriptor) {
  m_descriptorLink = SG::ElementLink<xAOD::CaloDetDescriptor>(keyHash, index, this);
  if (descriptor) {
    m_descriptorLink.setElement(keyHash, index, descriptor);
  }
}

void CaloCell::setDescriptor(const SG::ElementLink<xAOD::CaloDetDescriptor>& link) {
  m_descriptorLink = link;
  m_descriptorLink.setOwner(this);
}

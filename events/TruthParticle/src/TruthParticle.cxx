#include "TruthParticle/TruthParticle.h"

using namespace xAOD;

TruthParticle::TruthParticle() :
  EDM(),
  m_pdgid(0),
  m_seedid(0),
  m_e(0.0),
  m_et(0.0),
  m_eta(0.0),
  m_phi(0.0),
  m_px(0.0),
  m_py(0.0),
  m_pz(0.0),
  m_vtx_x(0.0),
  m_vtx_y(0.0),
  m_vtx_z(0.0),
  m_seedLink()
{
  m_seedLink.setOwner(this);
}

TruthParticle::TruthParticle(int pdgid, int seedid, 
                             float e, float et, float eta, float phi, 
                             float px, float py, float pz,  
                             float vx, float vy, float vz) :
  EDM(),
  m_pdgid(pdgid),
  m_seedid(seedid),
  m_e(e),
  m_et(et),
  m_eta(eta),
  m_phi(phi),
  m_px(px),
  m_py(py),
  m_pz(pz),
  m_vtx_x(vx),
  m_vtx_y(vy),
  m_vtx_z(vz),
  m_seedLink()
{
  m_seedLink.setOwner(this);
}

const xAOD::Seed* TruthParticle::seed() const {
  m_seedLink.setOwner(this);
  return m_seedLink.get();
}

void TruthParticle::setSeed(const xAOD::Seed* seed) {
  m_seedLink = SG::ElementLink<xAOD::Seed>("", 0, seed, this);
}

void TruthParticle::setSeed(const std::string& key, uint32_t index, const xAOD::Seed* seed) {
  m_seedLink = SG::ElementLink<xAOD::Seed>(key, index, seed, this);
}

void TruthParticle::setSeed(uint64_t keyHash, uint32_t index, const xAOD::Seed* seed) {
  m_seedLink = SG::ElementLink<xAOD::Seed>(keyHash, index, this);
  if (seed) {
    m_seedLink.setElement(keyHash, index, seed);
  }
}

void TruthParticle::setSeed(const SG::ElementLink<xAOD::Seed>& link) {
  m_seedLink = link;
  m_seedLink.setOwner(this);
}

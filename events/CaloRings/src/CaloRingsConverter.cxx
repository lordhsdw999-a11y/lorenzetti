#include "CaloRings/CaloRingsConverter.h"

using namespace xAOD;

bool CaloRingsConverter::convert(const CaloRings *rings, CaloRings_t &rings_t) {
  if (rings) {
    rings_t.cluster_key_hash = rings->caloClusterLink().keyHash();
    rings_t.cluster_index    = rings->caloClusterLink().index();
    rings_t.rings            = rings->rings();
    return true;
  }
  return false;
}

bool CaloRingsConverter::convert(const CaloRings_t &rings_t, CaloRings *&rings) {
  rings = new xAOD::CaloRings();
  rings->setRings(rings_t.rings);
  rings->setCaloCluster(rings_t.cluster_key_hash, rings_t.cluster_index);
  return true;
}
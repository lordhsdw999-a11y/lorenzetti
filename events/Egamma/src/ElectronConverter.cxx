#include "Egamma/ElectronConverter.h"

using namespace xAOD;

bool ElectronConverter::convert(const Electron *electron, Electron_t &electron_t) {
  if (electron) {
    electron_t.eta = electron->eta();
    electron_t.phi = electron->phi();
    electron_t.et  = electron->et();
    electron_t.e   = electron->e();
    
    electron_t.isEM.clear();
    electron_t.isEM.push_back(electron->isTight());
    electron_t.isEM.push_back(electron->isMedium());
    electron_t.isEM.push_back(electron->isLoose());
    electron_t.isEM.push_back(electron->isVeryLoose());

    electron_t.cluster_key_hash = electron->caloClusterLink().keyHash();
    electron_t.cluster_index    = electron->caloClusterLink().index();

    return true;
  }
  return false;
}

bool ElectronConverter::convert(const Electron_t &electron_t, Electron *&electron) {
  electron = new xAOD::Electron();
  electron->setEta(electron_t.eta);
  electron->setPhi(electron_t.phi);
  electron->setEt(electron_t.et);
  electron->setE(electron_t.e);

  if (electron_t.isEM.size() >= 4) {
    electron->setIsTight(electron_t.isEM[0]);
    electron->setIsMedium(electron_t.isEM[1]);  
    electron->setIsLoose(electron_t.isEM[2]);
    electron->setIsVeryLoose(electron_t.isEM[3]);
  }

  electron->setCaloCluster(electron_t.cluster_key_hash, electron_t.cluster_index);
  return true;
}
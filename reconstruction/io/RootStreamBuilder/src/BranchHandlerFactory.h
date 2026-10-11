#ifndef BranchHandlerFactory_h
#define BranchHandlerFactory_h

#include "GenericBranchHandler.h"
#include "CaloHitBranchHandler.h"

// EDM Includes
#include "EventInfo/EventInfoContainer.h"
#include "EventInfo/EventInfoConverter.h"

#include "TruthParticle/TruthParticleContainer.h"
#include "TruthParticle/TruthParticleConverter.h"

#include "EventInfo/SeedContainer.h"
#include "EventInfo/SeedConverter.h"

#include "CaloHit/CaloHitContainer.h"
#include "CaloHit/CaloHitConverter.h"

#include "CaloCell/CaloDetDescriptorContainer.h"
#include "CaloCell/CaloDetDescriptorConverter.h"

#include "CaloCell/CaloCellContainer.h"
#include "CaloCell/CaloCellConverter.h"

#include "CaloCluster/CaloClusterContainer.h"
#include "CaloCluster/CaloClusterConverter.h"

#include "CaloRings/CaloRingsContainer.h"
#include "CaloRings/CaloRingsConverter.h"

#include "Egamma/ElectronContainer.h"
#include "Egamma/ElectronConverter.h"

#include <memory>
#include <string>
#include <algorithm>

namespace Gaugi {

  /**
   * @class BranchHandlerFactory
   * @brief Factory creating typed IBranchHandler instances from type names and keys.
   */
  class BranchHandlerFactory {
  public:
    static std::unique_ptr<IBranchHandler> createHandler(
        const std::string &rawTypeName,
        const std::string &key,
        bool onlyRoI = false,
        float etaWindow = 0.4f,
        float phiWindow = 0.4f,
        const std::string &truthKey = "Particles",
        const std::vector<int> &cellHashes = {})
    {
      std::string typeName = rawTypeName;
      // Strip namespace if present
      if (typeName.find("xAOD::") == 0) {
        typeName = typeName.substr(6);
      }

      if (typeName == "CaloHitContainer" || typeName == "CaloHit") {
        return std::make_unique<CaloHitBranchHandler>(key, onlyRoI, etaWindow, phiWindow, truthKey, cellHashes);
      }
      else if (typeName == "EventInfoContainer" || typeName == "EventInfo") {
        return std::make_unique<GenericBranchHandler<xAOD::EventInfoContainer,
                                                     xAOD::EventInfo_t,
                                                     xAOD::EventInfoConverter>>("EventInfoContainer", key);
      }
      else if (typeName == "TruthParticleContainer" || typeName == "TruthParticle") {
        return std::make_unique<GenericBranchHandler<xAOD::TruthParticleContainer,
                                                     xAOD::TruthParticle_t,
                                                     xAOD::TruthParticleConverter>>("TruthParticleContainer", key);
      }
      else if (typeName == "SeedContainer" || typeName == "Seed") {
        return std::make_unique<GenericBranchHandler<xAOD::SeedContainer,
                                                     xAOD::Seed_t,
                                                     xAOD::SeedConverter>>("SeedContainer", key);
      }

      else if (typeName == "CaloDetDescriptorContainer" || typeName == "CaloDetDescriptor") {
        return std::make_unique<GenericBranchHandler<xAOD::CaloDetDescriptorContainer,
                                                     xAOD::CaloDetDescriptor_t,
                                                     xAOD::CaloDetDescriptorConverter>>("CaloDetDescriptorContainer", key);
      }
      else if (typeName == "CaloCellContainer" || typeName == "CaloCell") {
        return std::make_unique<GenericBranchHandler<xAOD::CaloCellContainer,
                                                     xAOD::CaloCell_t,
                                                     xAOD::CaloCellConverter>>("CaloCellContainer", key);
      }
      else if (typeName == "CaloClusterContainer" || typeName == "CaloCluster") {
        return std::make_unique<GenericBranchHandler<xAOD::CaloClusterContainer,
                                                     xAOD::CaloCluster_t,
                                                     xAOD::CaloClusterConverter>>("CaloClusterContainer", key);
      }
      else if (typeName == "CaloRingsContainer" || typeName == "CaloRings") {
        return std::make_unique<GenericBranchHandler<xAOD::CaloRingsContainer,
                                                     xAOD::CaloRings_t,
                                                     xAOD::CaloRingsConverter>>("CaloRingsContainer", key);
      }
      else if (typeName == "ElectronContainer" || typeName == "Electron") {
        return std::make_unique<GenericBranchHandler<xAOD::ElectronContainer,
                                                     xAOD::Electron_t,
                                                     xAOD::ElectronConverter>>("ElectronContainer", key);
      }

      return nullptr;
    }
  };

} // namespace Gaugi

#endif

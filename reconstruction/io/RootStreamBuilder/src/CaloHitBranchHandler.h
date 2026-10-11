#ifndef CaloHitBranchHandler_h
#define CaloHitBranchHandler_h

#include "GenericBranchHandler.h"
#include "CaloHit/CaloHitContainer.h"
#include "CaloHit/CaloHitConverter.h"
#include "TruthParticle/TruthParticleContainer.h"
#include "G4Kernel/CaloPhiRange.h"
#include <cmath>
#include <vector>
#include <algorithm>

namespace Gaugi {

  /**
   * @class CaloHitBranchHandler
   * @brief Specialized branch handler for CaloHitContainer with optional RoI filtering.
   */
  class CaloHitBranchHandler : public GenericBranchHandler<xAOD::CaloHitContainer,
                                                           xAOD::CaloHit_t,
                                                           xAOD::CaloHitConverter> {
  public:
    CaloHitBranchHandler(const std::string &key,
                         bool onlyRoI = false,
                         float etaWindow = 0.4f,
                         float phiWindow = 0.4f,
                         const std::string &truthKey = "Particles",
                         const std::vector<int> &cellHashes = {})
      : GenericBranchHandler("CaloHitContainer", key),
        m_onlyRoI(onlyRoI),
        m_etaWindow(etaWindow),
        m_phiWindow(phiWindow),
        m_truthKey(truthKey),
        m_cellHashes(cellHashes)
    {}

    virtual ~CaloHitBranchHandler() = default;

    virtual StatusCode writeFromContext(SG::EventContext &ctx) override {
      clear();
      SG::ReadHandle<xAOD::CaloHitContainer> handle(m_key, ctx);
      if (!handle.isValid()) {
        return StatusCode::FAILURE;
      }

      xAOD::CaloHitConverter cnv;

      if (m_onlyRoI) {
        SG::ReadHandle<xAOD::TruthParticleContainer> particles(m_truthKey, ctx);
        bool hasParticles = particles.isValid() && !particles->empty();
        bool keepCells = !m_cellHashes.empty();

        for (const auto hit : *handle) {
          if (!hit) continue;
          bool match = false;

          if (hasParticles) {
            for (const auto &par : *particles) {
              float deltaEta = std::abs(par->eta() - hit->eta());
              float deltaPhi = std::abs(CaloPhiRange::diff(par->phi(), hit->phi()));
              if (deltaEta < m_etaWindow / 2.0f && deltaPhi < m_phiWindow / 2.0f) {
                match = true;
                break;
              }
            }
          }

          if (!match && keepCells) {
            if (std::find(m_cellHashes.begin(), m_cellHashes.end(), static_cast<int>(hit->hash())) != m_cellHashes.end()) {
              match = true;
            }
          }

          if (!match && (hasParticles || keepCells)) {
            continue; // Skip hit outside RoI
          }

          xAOD::CaloHit_t item_t;
          cnv.convert(hit, item_t);
          m_data->push_back(item_t);
        }
      } else {
        for (const auto hit : *handle) {
          if (!hit) continue;
          xAOD::CaloHit_t item_t;
          cnv.convert(hit, item_t);
          m_data->push_back(item_t);
        }
      }

      return StatusCode::SUCCESS;
    }

  private:
    bool m_onlyRoI;
    float m_etaWindow;
    float m_phiWindow;
    std::string m_truthKey;
    std::vector<int> m_cellHashes;
  };

} // namespace Gaugi

#endif

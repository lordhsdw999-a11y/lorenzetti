#ifndef CaloCellBranchHandler_h
#define CaloCellBranchHandler_h

#include "GenericBranchHandler.h"
#include "CaloCell/CaloCellContainer.h"
#include "CaloCell/CaloCellConverter.h"
#include "CaloCell/CaloDetDescriptorContainer.h"
#include <string>

namespace Gaugi {

  /**
   * @class CaloCellBranchHandler
   * @brief Specialized branch handler for CaloCellContainer with optional noise sigma filtering (ATLAS Run 4).
   *
   * Evaluates cell energies against electronic noise sigma (E > N*sigma)
   * independently on-the-fly during read. Surviving cells are recorded into StoreGate.
   */
  class CaloCellBranchHandler : public GenericBranchHandler<xAOD::CaloCellContainer,
                                                            xAOD::CaloCell_t,
                                                            xAOD::CaloCellConverter> {
  public:
    CaloCellBranchHandler(const std::string &key,
                          bool filterBySigma = false,
                          float sigmaThreshold = 2.0f,
                          const std::string &descriptorsKey = "CaloDetDescriptors")
      : GenericBranchHandler("CaloCellContainer", key),
        m_filterBySigma(filterBySigma),
        m_sigmaThreshold(sigmaThreshold),
        m_descriptorsKey(descriptorsKey)
    {}

    virtual ~CaloCellBranchHandler() = default;

    virtual StatusCode readAndRecord(SG::EventContext &ctx) override {
      if (!m_data) {
        return StatusCode::FAILURE;
      }

      auto container = std::make_unique<xAOD::CaloCellContainer>();
      xAOD::CaloCellConverter cnv;

      if (m_filterBySigma) {
        SG::ReadHandle<xAOD::CaloDetDescriptorContainer> descContainer(m_descriptorsKey, ctx);
        bool hasDescriptors = descContainer.isValid();

        for (const auto &item_t : *m_data) {
          float cell_e = item_t.e;
          float sigma = 0.0f;
          if (hasDescriptors && item_t.descriptor_index < descContainer->size()) {
            const auto desc = descContainer->at(item_t.descriptor_index);
            if (desc) {
              sigma = desc->sigma();
            }
          }

          float threshold = (sigma > 0.0f) ? (m_sigmaThreshold * sigma) : 0.0f;
          if (cell_e <= threshold) {
            continue; // Filter out cell with E <= N*sigma
          }

          xAOD::CaloCell *cell = nullptr;
          cnv.convert(item_t, cell);
          if (cell) {
            container->push_back(cell);
          }
        }
      } else {
        // Standard unfiltered read
        for (const auto &item_t : *m_data) {
          xAOD::CaloCell *cell = nullptr;
          cnv.convert(item_t, cell);
          if (cell) {
            container->push_back(cell);
          }
        }
      }

      SG::WriteHandle<xAOD::CaloCellContainer> handle(m_key, ctx);
      handle.record(std::move(container));
      return StatusCode::SUCCESS;
    }

  private:
    bool m_filterBySigma;
    float m_sigmaThreshold;
    std::string m_descriptorsKey;
  };

} // namespace Gaugi

#endif

#ifndef CaloCellBranchHandler_h
#define CaloCellBranchHandler_h

#include "GenericBranchHandler.h"
#include "CaloCell/CaloCellContainer.h"
#include "CaloCell/CaloCellConverter.h"
#include "CaloCell/CaloDetDescriptorContainer.h"
#include <unordered_set>
#include <memory>
#include <string>

namespace Gaugi {

  /**
   * @class CaloCellBranchHandler
   * @brief Specialized branch handler for CaloCellContainer with optional noise sigma filtering (ATLAS Run 4).
   *
   * Evaluates reconstructed cell energies against electronic noise sigma (E > N*sigma)
   * on-the-fly during read. Surviving cells are recorded into StoreGate, and matching
   * TruthCells are automatically filtered to maintain strict 1-to-1 correspondence.
   */
  class CaloCellBranchHandler : public GenericBranchHandler<xAOD::CaloCellContainer,
                                                            xAOD::CaloCell_t,
                                                            xAOD::CaloCellConverter> {
  public:
    CaloCellBranchHandler(const std::string &key,
                          bool filterBySigma = false,
                          float sigmaThreshold = 2.0f,
                          const std::string &descriptorsKey = "CaloDetDescriptors",
                          std::shared_ptr<std::unordered_set<uint32_t>> sharedPassedIndices = nullptr)
      : GenericBranchHandler("CaloCellContainer", key),
        m_filterBySigma(filterBySigma),
        m_sigmaThreshold(sigmaThreshold),
        m_descriptorsKey(descriptorsKey),
        m_passedIndices(sharedPassedIndices ? sharedPassedIndices : std::make_shared<std::unordered_set<uint32_t>>())
    {}

    virtual ~CaloCellBranchHandler() = default;

    std::shared_ptr<std::unordered_set<uint32_t>> passedIndices() const {
      return m_passedIndices;
    }

    virtual StatusCode readAndRecord(SG::EventContext &ctx) override {
      if (!m_data) {
        return StatusCode::FAILURE;
      }

      auto container = std::make_unique<xAOD::CaloCellContainer>();
      xAOD::CaloCellConverter cnv;

      if (m_filterBySigma) {
        SG::ReadHandle<xAOD::CaloDetDescriptorContainer> descContainer(m_descriptorsKey, ctx);
        bool hasDescriptors = descContainer.isValid();

        if (m_key == "Cells") {
          m_passedIndices->clear();

          for (const auto &item_t : *m_data) {
            float reco_e = item_t.e;
            float sigma = 0.0f;
            if (hasDescriptors && item_t.descriptor_index < descContainer->size()) {
              const auto desc = descContainer->at(item_t.descriptor_index);
              if (desc) {
                sigma = desc->sigma();
              }
            }

            float threshold = (sigma > 0.0f) ? (m_sigmaThreshold * sigma) : 0.0f;
            if (reco_e <= threshold) {
              continue; // Filter out cell with E <= N*sigma
            }

            m_passedIndices->insert(item_t.descriptor_index);

            xAOD::CaloCell *cell = nullptr;
            cnv.convert(item_t, cell);
            if (cell) {
              container->push_back(cell);
            }
          }
        } else if (m_key == "TruthCells") {
          // Truth cells must strictly match the surviving real cells
          for (const auto &item_t : *m_data) {
            if (!m_passedIndices->count(item_t.descriptor_index)) {
              continue; // Filter out truth cell because corresponding real cell was filtered
            }

            xAOD::CaloCell *cell = nullptr;
            cnv.convert(item_t, cell);
            if (cell) {
              container->push_back(cell);
            }
          }
        } else {
          // General cell container
          for (const auto &item_t : *m_data) {
            float reco_e = item_t.e;
            float sigma = 0.0f;
            if (hasDescriptors && item_t.descriptor_index < descContainer->size()) {
              const auto desc = descContainer->at(item_t.descriptor_index);
              if (desc) {
                sigma = desc->sigma();
              }
            }

            float threshold = (sigma > 0.0f) ? (m_sigmaThreshold * sigma) : 0.0f;
            if (reco_e <= threshold) {
              continue;
            }

            xAOD::CaloCell *cell = nullptr;
            cnv.convert(item_t, cell);
            if (cell) {
              container->push_back(cell);
            }
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
    std::shared_ptr<std::unordered_set<uint32_t>> m_passedIndices;
  };

} // namespace Gaugi

#endif

#ifndef RootStreamReader_h
#define RootStreamReader_h

#include "GaugiKernel/Algorithm.h"
#include "GaugiKernel/StatusCode.h"
#include "GaugiKernel/EventContext.h"
#include "IBranchHandler.h"
#include "TFile.h"
#include "TTree.h"
#include <string>
#include <vector>
#include <memory>

/**
 * @class RootStreamReader
 * @brief Generic, auto-discovering ROOT stream reader for all Lorenzetti data tiers.
 * 
 * Inspects all branches in the input TTree, identifies the EDM container types and keys,
 * and dynamically records the reconstructed xAOD containers into StoreGate for each event.
 */
class RootStreamReader : public Gaugi::Algorithm {
public:
  RootStreamReader(std::string name);
  virtual ~RootStreamReader();

  virtual StatusCode initialize() override;
  virtual StatusCode bookHistograms(SG::EventContext &ctx) const override;
  virtual StatusCode pre_execute(SG::EventContext &ctx) const override;
  virtual StatusCode execute(SG::EventContext &ctx, const G4Step *step) const override;
  virtual StatusCode execute(SG::EventContext &ctx, int evt) const override;
  virtual StatusCode post_execute(SG::EventContext &ctx) const override;
  virtual StatusCode fillHistograms(SG::EventContext &ctx) const override;
  virtual StatusCode finalize() override;

  /*! Return the number of events in the TTree */
  long long entries() const;

private:
  StatusCode discoverBranches(TTree *tree);

  std::string m_inputFile;
  std::string m_ntupleName;
  int m_outputLevel;
  bool m_filterBySigma;
  float m_sigmaThreshold;
  std::string m_descriptorsKey;

  TFile *m_file;
  TTree *m_tree;
  std::vector<std::unique_ptr<Gaugi::IBranchHandler>> m_handlers;
};

#endif

#ifndef ElectronMaker_h
#define ElectronMaker_h

#include "CaloCell/enumeration.h"
#include "GaugiKernel/StatusCode.h"
#include "GaugiKernel/DataHandle.h"
#include "GaugiKernel/Algorithm.h"
#include "CaloCell/CaloCellContainer.h"
#include "CaloCluster/CaloClusterContainer.h"
#include "Egamma/Electron.h"
#include "Egamma/ElectronContainer.h"
#include <string>
#include <vector>

/**
 * @class ElectronMaker
 * @brief Algorithm to reconstruct electron candidates from calorimeter clusters.
 * 
 * Creates electron objects from CaloClusters. Evaluates PID selection criteria
 * (Very Loose, Loose, Medium, Tight) for central and forward calorimeter clusters.
 */
class ElectronMaker : public Gaugi::Algorithm {
public:
  /** Constructor **/
  ElectronMaker(std::string name);
  
  /** Destructor **/
  virtual ~ElectronMaker();
  
  virtual StatusCode initialize() override;

  /*! Book all histograms into StoreGate */
  virtual StatusCode bookHistograms(SG::EventContext &ctx) const override;
  
  virtual StatusCode pre_execute(SG::EventContext &ctx) const override;
  
  virtual StatusCode execute(SG::EventContext &ctx, const G4Step *step) const override;
  
  /*! Execute in ComponentAccumulator */
  virtual StatusCode execute(SG::EventContext &ctx, int /*evt*/) const override;
  
  virtual StatusCode post_execute(SG::EventContext &ctx) const override;
  
  virtual StatusCode fillHistograms(SG::EventContext &ctx) const override;
  
  virtual StatusCode finalize() override;

  /**
   * @brief Evaluates all PID decisions in a single pass.
   * @param cluster Candidate calorimeter cluster.
   * @param isTight Output boolean for Tight WP.
   * @param isMedium Output boolean for Medium WP.
   * @param isLoose Output boolean for Loose WP.
   * @param isVeryLoose Output boolean for Very Loose WP.
   */
  void evaluatePID(const xAOD::CaloCluster* cluster,
                   bool &isTight,
                   bool &isMedium,
                   bool &isLoose,
                   bool &isVeryLoose) const;

  /**
   * @brief Check if a cluster passes a specific electron ID cut.
   * @param cluster The candidate cluster.
   * @param workingPoint The operating point ("tight", "medium", "loose", "vloose").
   * @return true if accepted.
   */
  bool compute(const xAOD::CaloCluster* cluster, std::string workingPoint) const;

private:
  int m_outputLevel;  
  std::string m_clusterKey;
  std::string m_electronKey;
  std::string m_histPath;
  
  std::vector<float> m_tightCuts;
  std::vector<float> m_mediumCuts;
  std::vector<float> m_looseCuts;
  std::vector<float> m_vlooseCuts;
  std::vector<float> m_secondLambdaCuts;
  std::vector<float> m_lateralMomCuts;
  std::vector<float> m_longMomCuts;
  std::vector<float> m_fracMaxCuts;
  std::vector<float> m_secondRCuts;
  std::vector<float> m_lambdaCenterCuts;
};

#endif

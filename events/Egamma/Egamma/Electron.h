#ifndef Electron_h
#define Electron_h

#include "CaloCluster/CaloCluster.h"
#include "CaloCell/CaloCell.h"
#include "GaugiKernel/EDM.h"
#include "GaugiKernel/ElementLink.h"
#include "GaugiKernel/macros.h"
#include <vector>
#include <cmath>
#include <string>

namespace xAOD {
  
  class Electron : public Gaugi::EDM {  
  public:
    /*! Constructor */
    Electron();

    /*! Destructor */
    ~Electron() = default;
   
    /*! The eta center of the cluster given by the simulation (RoI) */ 
    PRIMITIVE_SETTER_AND_GETTER(float, m_eta, setEta, eta);
    /*! The phi center of the cluster given by the simulation (RoI) */ 
    PRIMITIVE_SETTER_AND_GETTER(float, m_phi, setPhi, phi);
    /*! set/get energy */
    PRIMITIVE_SETTER_AND_GETTER(float, m_e, setE, e);
    /*! set/get transverse energy */
    PRIMITIVE_SETTER_AND_GETTER(float, m_et, setEt, et);
    
    /*! Set CaloCluster direct pointer */
    void setCaloCluster(const xAOD::CaloCluster *clus);

    /*! Set CaloCluster via key string and index */
    void setCaloCluster(const std::string& key, uint32_t index, const xAOD::CaloCluster* clus = nullptr);

    /*! Set CaloCluster via 64-bit key hash and index */
    void setCaloCluster(uint64_t keyHash, uint32_t index, const xAOD::CaloCluster* clus = nullptr);

    /*! Set CaloCluster via ElementLink */
    void setCaloCluster(const SG::ElementLink<xAOD::CaloCluster>& link);

    /*! Get the associated CaloCluster */
    const xAOD::CaloCluster* caloCluster() const;

    /*! Get the ElementLink to the associated CaloCluster */
    const SG::ElementLink<xAOD::CaloCluster>& caloClusterLink() const { return m_caloCluster; }

    bool isTight() const;
    bool isMedium() const;
    bool isLoose() const;
    bool isVeryLoose() const;
    void setIsTight(bool isTight);
    void setIsMedium(bool isMedium);
    void setIsLoose(bool isLoose);
    void setIsVeryLoose(bool isVeryLoose);
    bool isForward() const { return std::abs(m_eta) > 2.5; }

  private:
    float m_e;
    float m_et;
    float m_eta;
    float m_phi;

    std::vector<bool> m_isEM;

    SG::ElementLink<xAOD::CaloCluster> m_caloCluster;
  };

} // namespace xAOD

#endif
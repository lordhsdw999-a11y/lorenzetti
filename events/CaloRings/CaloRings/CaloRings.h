#ifndef CaloRings_h
#define CaloRings_h

#include "CaloCluster/CaloCluster.h"
#include "CaloCell/CaloCell.h"
#include "GaugiKernel/EDM.h"
#include "GaugiKernel/ElementLink.h"
#include "GaugiKernel/macros.h"
#include <vector>
#include <cmath>

namespace xAOD {
  
  class CaloRings : public Gaugi::EDM {  
  public:
    /*! Constructor */
    CaloRings();

    /*! Destructor */
    ~CaloRings() = default;

    /*! The eta center of the cluster given by the simulation (RoI) */ 
    PRIMITIVE_SETTER_AND_GETTER(float, m_eta, setEta, eta);

    /*! The phi center of the cluster given by the simulation (RoI) */ 
    PRIMITIVE_SETTER_AND_GETTER(float, m_phi, setPhi, phi);

    /*! Rings energy */
    PRIMITIVE_SETTER_AND_GETTER(std::vector<float>, m_rings, setRings, rings);

    /*! Set the associated CaloCluster pointer directly */
    void setCaloCluster(const xAOD::CaloCluster *clus);

    /*! Set the associated CaloCluster via container key and element index */
    void setCaloCluster(const std::string& key, uint32_t index, const xAOD::CaloCluster* clus = nullptr);

    /*! Set the associated CaloCluster via 64-bit key hash and element index */
    void setCaloCluster(uint64_t keyHash, uint32_t index, const xAOD::CaloCluster* clus = nullptr);

    /*! Set the associated CaloCluster via ElementLink */
    void setCaloCluster(const SG::ElementLink<xAOD::CaloCluster>& link);

    /*! Get the associated cluster to this CaloRings */
    const xAOD::CaloCluster* caloCluster() const;

    /*! Get the ElementLink to the associated cluster */
    const SG::ElementLink<xAOD::CaloCluster>& caloClusterLink() const { return m_caloCluster; }

  private:
    std::vector<float> m_rings;
    SG::ElementLink<xAOD::CaloCluster> m_caloCluster;
    
    float m_eta;
    float m_phi;
  };

} // namespace xAOD

#endif

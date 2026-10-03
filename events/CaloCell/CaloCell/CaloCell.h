#ifndef CaloCell_h
#define CaloCell_h

/** simulator includes **/
#include "CaloCell/enumeration.h"
#include "CaloCell/CaloDetDescriptor.h"
#include "GaugiKernel/EDM.h"
#include "GaugiKernel/ElementLink.h"
#include "GaugiKernel/macros.h"
#include <string>
#include <cstdint>

namespace xAOD {
  
  class CaloCell : public Gaugi::EDM {  
  public:
    /** Constructor **/
    CaloCell();
    
    /** Constructor with coordinates **/
    CaloCell(float eta, float phi, float deta, float dphi);

    /** Destructor **/
    ~CaloCell() = default;

    /*! Cell eta center */
    PRIMITIVE_SETTER_AND_GETTER(float, m_eta, setEta, eta);
    /*! Cell phi center */
    PRIMITIVE_SETTER_AND_GETTER(float, m_phi, setPhi, phi);
    /*! Cell delta eta */
    PRIMITIVE_SETTER_AND_GETTER(float, m_deta, setDeltaEta, deltaEta);
    /*! Cell delta phi */
    PRIMITIVE_SETTER_AND_GETTER(float, m_dphi, setDeltaPhi, deltaPhi);
    /*! Cell energy **/
    PRIMITIVE_SETTER_AND_GETTER(float, m_e, setE, e);
    /*! Transverse energy */
    PRIMITIVE_SETTER_AND_GETTER(float, m_et, setEt, et);
    /*! Cell time delay of the pulse (Time of flight) **/
    PRIMITIVE_SETTER_AND_GETTER(float, m_tau, setTau, tau);

    /*! Get the associated CaloDetDescriptor */ 
    const xAOD::CaloDetDescriptor* descriptor() const;

    /*! Get the ElementLink to the associated CaloDetDescriptor */
    const SG::ElementLink<xAOD::CaloDetDescriptor>& descriptorLink() const { return m_descriptorLink; }

    /*! Set the associated CaloDetDescriptor direct pointer */ 
    void setDescriptor(const xAOD::CaloDetDescriptor* descriptor);

    /*! Set the associated CaloDetDescriptor via key string and index */
    void setDescriptor(const std::string& key, uint32_t index, const xAOD::CaloDetDescriptor* descriptor = nullptr);

    /*! Set the associated CaloDetDescriptor via 64-bit key hash and index */
    void setDescriptor(uint64_t keyHash, uint32_t index, const xAOD::CaloDetDescriptor* descriptor = nullptr);

    /*! Set the associated CaloDetDescriptor via ElementLink */
    void setDescriptor(const SG::ElementLink<xAOD::CaloDetDescriptor>& link);

  private:
    float m_eta;
    float m_phi;
    float m_deta;
    float m_dphi;
    float m_e;
    float m_et;
    float m_tau;

    SG::ElementLink<xAOD::CaloDetDescriptor> m_descriptorLink;
  };

} // namespace xAOD

#endif

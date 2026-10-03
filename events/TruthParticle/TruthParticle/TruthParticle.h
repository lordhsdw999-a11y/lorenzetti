#ifndef TruthParticle_h
#define TruthParticle_h

#include "EventInfo/Seed.h"
#include "GaugiKernel/EDM.h"
#include "GaugiKernel/ElementLink.h"
#include "GaugiKernel/macros.h"
#include <string>
#include <cstdint>

namespace xAOD {
  
  class TruthParticle : public Gaugi::EDM {  
  public:
    /*! Constructor */
    TruthParticle();
    /*! Constructor */
    TruthParticle(int pdgid, int seedid, 
                  float e, float et, float eta, float phi, 
                  float px, float py, float pz, 
                  float vx, float vy, float vz); // production vertex position
                    
    /*! Destructor */
    ~TruthParticle() = default;

    /*! The eta center of the cluster given by the simulation (RoI) */ 
    PRIMITIVE_SETTER_AND_GETTER(float, m_eta, setEta, eta);
    /*! The phi center of the cluster given by the simulation (RoI) */ 
    PRIMITIVE_SETTER_AND_GETTER(float, m_phi, setPhi, phi);
    /*! set/get energy */
    PRIMITIVE_SETTER_AND_GETTER(float, m_e, setE, e);
    /*! set/get transverse energy */
    PRIMITIVE_SETTER_AND_GETTER(float, m_et, setEt, et);
    /*! set/get particle identification */
    PRIMITIVE_SETTER_AND_GETTER(int, m_pdgid, setPdgid, pdgid);
    
    PRIMITIVE_SETTER_AND_GETTER(int, m_seedid, setSeedid, seedid);

    PRIMITIVE_SETTER_AND_GETTER(float, m_px, setPx, px);
    PRIMITIVE_SETTER_AND_GETTER(float, m_py, setPy, py);
    PRIMITIVE_SETTER_AND_GETTER(float, m_pz, setPz, pz);

    /*! set/get vertex position */
    PRIMITIVE_SETTER_AND_GETTER(float, m_vtx_x, setVx, vx);
    PRIMITIVE_SETTER_AND_GETTER(float, m_vtx_y, setVy, vy);
    PRIMITIVE_SETTER_AND_GETTER(float, m_vtx_z, setVz, vz);

    /*! Access Seed pointer */
    const xAOD::Seed* seed() const;

    /*! Access Seed ElementLink */
    const SG::ElementLink<xAOD::Seed>& seedLink() const { return m_seedLink; }

    /*! Set Seed direct pointer */
    void setSeed(const xAOD::Seed* seed);

    /*! Set Seed via key and index */
    void setSeed(const std::string& key, uint32_t index, const xAOD::Seed* seed = nullptr);

    /*! Set Seed via key hash and index */
    void setSeed(uint64_t keyHash, uint32_t index, const xAOD::Seed* seed = nullptr);

    /*! Set Seed via ElementLink */
    void setSeed(const SG::ElementLink<xAOD::Seed>& link);

  private:
    int m_pdgid;
    int m_seedid;
    float m_e;
    float m_et;
    float m_eta;
    float m_phi;
    float m_px;
    float m_py;
    float m_pz;
    
    // vertex position
    float m_vtx_x;      
    float m_vtx_y;
    float m_vtx_z;

    SG::ElementLink<xAOD::Seed> m_seedLink;
  };

} // namespace xAOD

#endif

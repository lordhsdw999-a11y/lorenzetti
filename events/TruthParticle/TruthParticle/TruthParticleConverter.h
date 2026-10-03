#ifndef TruthParticleConverter_h
#define TruthParticleConverter_h

#include "TruthParticle/TruthParticle.h"
#include <cstdint>

namespace xAOD {

  struct TruthParticle_t {
    int      pdgid;
    uint64_t seed_key_hash;
    uint32_t seed_index;
    int      seedid;
    float    e;
    float    et;
    float    eta;
    float    phi;
    float    px;
    float    py;
    float    pz;
    float    vx; // vertex position x (prod_vx)
    float    vy; // vertex position y
    float    vz; // vertex position z
  };

  class TruthParticleConverter {
  public:
    TruthParticleConverter() = default;
    ~TruthParticleConverter() = default;

    bool convert(const TruthParticle *truth, TruthParticle_t &truth_t) const;
    bool convert(const TruthParticle_t &truth_t, TruthParticle *&truth) const;
  };

} // namespace xAOD

#endif

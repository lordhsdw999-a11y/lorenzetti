#ifndef CaloRingsConverter_h
#define CaloRingsConverter_h

#include "CaloRings/CaloRings.h"
#include <vector>
#include <cstdint>

namespace xAOD {

  struct CaloRings_t {
    uint64_t           cluster_key_hash;
    uint32_t           cluster_index;
    std::vector<float> rings;
  };

  class CaloRingsConverter {
  public:
    CaloRingsConverter() = default;
    ~CaloRingsConverter() = default;

    // Convert an EDM class object into a persistent struct
    bool convert(const CaloRings *rings, CaloRings_t &rings_t);

    // Convert a persistent struct into an EDM class object
    bool convert(const CaloRings_t &rings_t, CaloRings *&rings);
  };

} // namespace xAOD

#endif

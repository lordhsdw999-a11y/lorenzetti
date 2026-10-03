#ifndef ElectronConverter_h
#define ElectronConverter_h

#include "Egamma/Electron.h"
#include <vector>
#include <cstdint>

namespace xAOD {

  struct Electron_t {
    uint64_t          cluster_key_hash;
    uint32_t          cluster_index;
    float             e;
    float             et;
    float             eta;
    float             phi;
    std::vector<bool> isEM;
  };

  class ElectronConverter {
  public:
    ElectronConverter() = default;
    ~ElectronConverter() = default;

    // Convert an EDM class object into a persistent struct
    bool convert(const Electron *electron, Electron_t &electron_t);

    // Convert a persistent struct into an EDM class object
    bool convert(const Electron_t &electron_t, Electron *&electron);
  };

} // namespace xAOD

#endif

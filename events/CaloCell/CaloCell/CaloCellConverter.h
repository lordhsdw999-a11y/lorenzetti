#ifndef CaloCellConverter_h
#define CaloCellConverter_h

/** simulator includes **/
#include "CaloCell/CaloCell.h"
#include <map>
#include <cstdint>

namespace xAOD {

  typedef std::map<unsigned long int, const xAOD::CaloCell*> cell_links_t;

  struct CaloCell_t {
    float e;
    float et;
    float tau; 
    float eta;
    float phi;
    float deta;
    float dphi;
    
    uint64_t descriptor_key_hash;
    uint32_t descriptor_index;
    unsigned long int descriptor_link; // Legacy / geometric hash link
  };

  class CaloCellConverter {
  public:
    CaloCellConverter() = default;
    ~CaloCellConverter() = default;

    // Convert an EDM class object into a persistent struct
    bool convert(const CaloCell *cell, CaloCell_t &cell_t);

    // Convert a persistent struct into an EDM class object
    bool convert(const CaloCell_t &cell_t, CaloCell *&cell);
  };

} // namespace xAOD

#endif

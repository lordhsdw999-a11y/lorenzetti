#ifndef IBranchHandler_h
#define IBranchHandler_h

#include "GaugiKernel/StatusCode.h"
#include "GaugiKernel/EventContext.h"
#include "TTree.h"
#include <string>
#include <memory>

namespace Gaugi {

  /**
   * @class IBranchHandler
   * @brief Polymorphic interface to serialize and deserialize branches dynamically.
   */
  class IBranchHandler {
  public:
    virtual ~IBranchHandler() = default;

    /*! Return the EDM type name (e.g., "CaloClusterContainer", "ElectronContainer") */
    virtual std::string typeName() const = 0;

    /*! Return the StoreGate container key (e.g., "CaloClusters", "Electrons") */
    virtual std::string key() const = 0;

    /*! Return the formatted branch name ("<TypeName>_<Key>") */
    virtual std::string branchName() const = 0;

    /*! Initialize branch for reading from TTree */
    virtual void initReadBranch(TTree *tree) = 0;

    /*! Initialize branch for writing to TTree */
    virtual void initWriteBranch(TTree *tree) = 0;

    /*! Read data from persistent vector, convert, and record into EventContext */
    virtual StatusCode readAndRecord(SG::EventContext &ctx) = 0;

    /*! Read container from EventContext, convert, and write into persistent vector */
    virtual StatusCode writeFromContext(SG::EventContext &ctx) = 0;

    /*! Clear internal buffer between events */
    virtual void clear() = 0;
  };

} // namespace Gaugi

#endif

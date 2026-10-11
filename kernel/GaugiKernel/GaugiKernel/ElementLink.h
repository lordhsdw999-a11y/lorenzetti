#ifndef ElementLink_h
#define ElementLink_h

#include "GaugiKernel/DataHandle.h"
#include "GaugiKernel/DataVector.h"
#include "GaugiKernel/EDM.h"
#include "GaugiKernel/StringHash.h"
#include <string>
#include <cstdint>
#include <stdexcept>
#include <iostream>

namespace SG {

  /**
   * @class ElementLink
   * @brief Persistent smart reference enabling relational navigation between EDM objects.
   *
   * Stores the target container key (or hash) and element index. Resolves the target
   * pointer on-demand (lazy evaluation) through the event's EventContext without
   * requiring manual link reconstruction loops in I/O readers.
   */
  template <typename TargetT>
  class ElementLink {
  public:
    /*! Default constructor (creates an unbound, invalid link) */
    ElementLink();

    /*! Constructor from target key string and index */
    ElementLink(const std::string& key, uint32_t index, const Gaugi::EDM* owner = nullptr);

    /*! Constructor from 64-bit target key hash and index */
    ElementLink(uint64_t keyHash, uint32_t index, const Gaugi::EDM* owner = nullptr);

    /*! Constructor with immediate target pointer */
    ElementLink(const std::string& key, uint32_t index, const TargetT* target, const Gaugi::EDM* owner = nullptr);

    /*! Copy constructor */
    ElementLink(const ElementLink& other);

    /*! Assignment operator */
    ElementLink& operator=(const ElementLink& other);

    /*! Destructor */
    ~ElementLink() = default;

    /*! Pointer dereference operator */
    const TargetT* operator->() const;

    /*! Value dereference operator */
    const TargetT& operator*() const;

    /*! Retrieve the resolved target pointer */
    const TargetT* get() const;

    /*! Check if the link points to a valid, resolvable object */
    bool isValid() const;

    /*! Check if this link is in its default, uninitialized state */
    bool isDefault() const;

    /*! Get the target container key string */
    const std::string& key() const { return m_targetKey; }

    /*! Get the 64-bit target container hash */
    uint64_t keyHash() const { return m_keyHash; }

    /*! Get the target element index */
    uint32_t index() const { return m_index; }

    /*! Set the owning EDM object */
    void setOwner(const Gaugi::EDM* owner) const { m_owner = owner; }

    /*! Set target by key string and index */
    void setElement(const std::string& key, uint32_t index, const TargetT* target = nullptr);

    /*! Set target by hash and index */
    void setElement(uint64_t keyHash, uint32_t index, const TargetT* target = nullptr);

    /*! Reset the cached pointer to force re-resolution */
    void resetCache() const;

  private:
    /*! Resolve target pointer on-demand via owner's EventContext */
    void resolve() const;

    std::string m_targetKey;             // Target collection key in EventContext
    uint64_t    m_keyHash;               // 64-bit FNV-1a hash of the target collection
    uint32_t    m_index;                 // Position index inside target DataVector

    mutable const Gaugi::EDM* m_owner;   //! Transient pointer to owner EDM element
    mutable const TargetT* m_cachedPtr;  //! Transient cached pointer to resolved target
    mutable bool m_isResolved;           //! Transient flag indicating cache validity
  };

} // namespace SG

#include "ElementLink.icc"

#endif

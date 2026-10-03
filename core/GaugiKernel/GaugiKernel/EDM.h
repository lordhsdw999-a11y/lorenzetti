#ifndef EDM_h
#define EDM_h

namespace SG {
  class DataHandle;
  class EventContext;
}

namespace Gaugi {

  /**
   * @class EDM
   * @brief Base class for all Event Data Model (EDM) elements in Lorenzetti.
   *
   * Holds a reference to the parent container to facilitate relational navigation
   * via ElementLink without hardcoding global state or manual pointer reconstruction.
   */
  class EDM {
  public:
    EDM() : m_container(nullptr) {}
    virtual ~EDM() = default;

    /**
     * @brief Set the parent container managing this object.
     */
    void setContainer(const SG::DataHandle* container) {
      m_container = container;
    }

    /**
     * @brief Get the parent container managing this object.
     */
    const SG::DataHandle* container() const {
      return m_container;
    }

  private:
    const SG::DataHandle* m_container; //! Transient pointer to parent container
  };

} // namespace Gaugi

#endif

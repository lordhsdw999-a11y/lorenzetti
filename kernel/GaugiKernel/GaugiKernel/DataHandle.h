#ifndef DataHandle_h
#define DataHandle_h

#include "GaugiKernel/StoreGate.h"
#include "GaugiKernel/MsgStream.h"
#include "GaugiKernel/StringHash.h"
#include <string>
#include <map>
#include <memory>
#include <vector>
#include <typeinfo>
#include <type_traits>
#include <utility>

namespace SG {

  class EventContext;

  /**
   * @class DataHandle
   * @brief Base class for downcasting all containers managed within EventContext.
   */
  class DataHandle {
  public:
    DataHandle() : m_ctx(nullptr) {}
    virtual ~DataHandle() {}

    /**
     * @brief Set the EventContext managing this container.
     */
    virtual void setContext(EventContext* ctx) {
      m_ctx = ctx;
    }

    /**
     * @brief Get the EventContext managing this container.
     */
    virtual EventContext* getContext() const {
      return m_ctx;
    }

  protected:
    EventContext* m_ctx; //! Transient context pointer
  };


  /**
   * @class EventContext
   * @brief Central per-event data bus storing and providing O(1) lookup by key and hash.
   */
  class EventContext : public MsgService {
  public:
    /*! Constructor */
    EventContext(std::string name);
    
    /*! Destructor */
    ~EventContext();

    /*! Record Containers of type DataVector<OBJECT> into EventContext */
    template<class T> 
    void record(std::string &sgkey, std::unique_ptr<T> &container);

    template<class T> 
    void record(const std::string &sgkey, std::unique_ptr<T> &container);

    /*! Get container pointer given a key string */
    template<class T> 
    const T* get(std::string &sgkey);

    template<class T> 
    const T* get(const std::string &sgkey);

    /*! Get container pointer given a 64-bit key hash */
    template<class T> 
    const T* get(uint64_t hash);

    /*! Clear all data handlers map and hash tables */
    void clear();
      
    /*! Set the store gate service */
    void setStoreGateSvc(StoreGate *store) { m_store = store; }

    /*! Get the store gate service */
    StoreGate* getStoreGateSvc() { return m_store; }

    void setThreadId(int id) { m_threadId = id; }
    int getThreadId() { return m_threadId; }

    void setNumberOfThreads(int numberOfThreads) { m_numberOfThreads = numberOfThreads; }
    int getNumberOfThreads() { return m_numberOfThreads; }

    /*! Get all keys in storage */
    std::vector<std::string> keys() const { 
      std::vector<std::string> keys;
      for (const auto &it : m_storable_ptr) {
        keys.push_back(it.first);
      }
      return keys;
    }

    /*! Check if key string exists */
    bool exist(std::string key) const {
      return m_storable_ptr.count(key) > 0;
    }

    /*! Check if hash exists */
    bool exist(uint64_t hash) const {
      return m_hash_to_ptr.count(hash) > 0;
    }

    /*! Get 64-bit hash associated with a key string */
    uint64_t getHash(const std::string& sgkey) const {
      auto it = m_key_to_hash.find(sgkey);
      if (it != m_key_to_hash.end()) {
        return it->second;
      }
      return Gaugi::stringHash(sgkey);
    }

    /*! Get key string associated with a 64-bit hash */
    std::string getKeyFromHash(uint64_t hash) const {
      auto it = m_hash_to_key.find(hash);
      if (it != m_hash_to_key.end()) {
        return it->second;
      }
      return "";
    }

  private:
    std::map<std::string, std::unique_ptr<const DataHandle>> m_storable_ptr;
    std::map<uint64_t, const DataHandle*> m_hash_to_ptr;
    std::map<std::string, uint64_t> m_key_to_hash;
    std::map<uint64_t, std::string> m_hash_to_key;
    
    StoreGate *m_store;
    int m_threadId;
    int m_numberOfThreads;
  };


  template<class T>
  class ReadHandle {
  public:
    ReadHandle(std::string sgkey, EventContext &ctx);
    ~ReadHandle();

    /*
     * @brief Dereference the pointer / container.
     */
    const T* operator->() const;
    const T& operator*() const;
    const T* ptr() const;
    const T* get() const;

    /*
     * @brief Forward direct iterator access for range-for loops.
     */
    auto begin() const -> decltype(std::declval<const T>().begin()) {
      return m_ptr ? m_ptr->begin() : decltype(std::declval<const T>().begin()){};
    }
    auto end() const -> decltype(std::declval<const T>().end()) {
      return m_ptr ? m_ptr->end() : decltype(std::declval<const T>().end()){};
    }

    std::string key() const;
    bool isValid() const;

  private:
    std::string m_sgkey;
    const T* m_ptr;
    bool m_isValid; 
  };


  template<class T>
  class WriteHandle {
  public:
    WriteHandle(std::string sgkey, EventContext &ctx);
    WriteHandle();
    ~WriteHandle();

    /*
     * @brief Dereference the pointer.
     */
    T* operator->();
    T& operator*();
    T* get();
    T* ptr();

    /*
     * @brief Forward direct iterator access for range-for loops.
     */
    auto begin() -> decltype(std::declval<T>().begin()) {
      return m_ptr ? m_ptr->begin() : decltype(std::declval<T>().begin()){};
    }
    auto end() -> decltype(std::declval<T>().end()) {
      return m_ptr ? m_ptr->end() : decltype(std::declval<T>().end()){};
    }

    /*
     * @brief Transfer container ownership to WriteHandle
     */ 
    void record(std::unique_ptr<T> ptr);

    /*
     * @brief Get the storable key
     */ 
    std::string key() const;

  private:
    std::string m_sgkey;
    std::unique_ptr<T> m_ptr;
    EventContext *m_ctx;
  };

} // namespace SG

#include "DataHandle.icc"

#endif

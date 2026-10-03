#ifndef GenericBranchHandler_h
#define GenericBranchHandler_h

#include "IBranchHandler.h"
#include "GaugiKernel/DataHandle.h"
#include <vector>
#include <memory>

namespace Gaugi {

  /**
   * @class GenericBranchHandler
   * @brief Type-safe template implementing IBranchHandler for EDM container types.
   */
  template <typename TContainer, typename TStruct, typename TConverter>
  class GenericBranchHandler : public IBranchHandler {
  public:
    GenericBranchHandler(const std::string &typeName, const std::string &key)
      : m_typeName(typeName),
        m_key(key),
        m_branchName(typeName + "_" + key),
        m_data(new std::vector<TStruct>()),
        m_ownsData(true)
    {}

    virtual ~GenericBranchHandler() {
      if (m_ownsData && m_data) {
        delete m_data;
        m_data = nullptr;
      }
    }

    virtual std::string typeName() const override { return m_typeName; }
    virtual std::string key() const override { return m_key; }
    virtual std::string branchName() const override { return m_branchName; }

    virtual void initReadBranch(TTree *tree) override {
      if (!tree) return;
      std::string bname = m_branchName;
      if (tree->GetAlias(bname.c_str())) {
        bname = std::string(tree->GetAlias(bname.c_str()));
      }
      if (!tree->FindBranch(bname.c_str())) {
        return;
      }
      tree->SetBranchStatus(bname.c_str(), 1);
      tree->SetBranchAddress(bname.c_str(), &m_data);
    }

    virtual void initWriteBranch(TTree *tree) override {
      if (!tree) return;
      tree->Branch(m_branchName.c_str(), &m_data);
    }

    virtual StatusCode readAndRecord(SG::EventContext &ctx) override {
      if (!m_data) {
        return StatusCode::FAILURE;
      }

      auto container = std::make_unique<TContainer>();
      TConverter cnv;

      for (const auto &item_t : *m_data) {
        typename TContainer::base_type *obj = nullptr;
        cnv.convert(item_t, obj);
        if (obj) {
          container->push_back(obj);
        }
      }

      SG::WriteHandle<TContainer> handle(m_key, ctx);
      handle.record(std::move(container));
      return StatusCode::SUCCESS;
    }

    virtual StatusCode writeFromContext(SG::EventContext &ctx) override {
      clear();
      SG::ReadHandle<TContainer> handle(m_key, ctx);
      if (!handle.isValid()) {
        return StatusCode::FAILURE;
      }

      TConverter cnv;
      for (const auto obj : *handle) {
        if (!obj) continue;
        TStruct item_t;
        cnv.convert(obj, item_t);
        m_data->push_back(item_t);
      }

      return StatusCode::SUCCESS;
    }

    virtual void clear() override {
      if (m_data) {
        m_data->clear();
      }
    }

  private:
    std::string m_typeName;
    std::string m_key;
    std::string m_branchName;
    std::vector<TStruct> *m_data;
    bool m_ownsData;
  };

} // namespace Gaugi

#endif

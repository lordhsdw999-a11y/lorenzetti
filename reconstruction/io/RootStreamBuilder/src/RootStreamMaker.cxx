#include "RootStreamMaker.h"
#include "BranchHandlerFactory.h"

using namespace Gaugi;

RootStreamMaker::RootStreamMaker(std::string name)
  : IMsgService(name),
    Algorithm(),
    m_ntupleName("CollectionTree"),
    m_outputFile(""),
    m_itemList(),
    m_outputLevel(1),
    m_onlyRoI(false),
    m_etaWindow(0.4f),
    m_phiWindow(0.4f),
    m_truthKey("Particles"),
    m_cellHashes(),
    m_file(nullptr),
    m_tree(nullptr),
    m_ownsFile(false),
    m_handlers()
{
  declareProperty("TreeName",      m_ntupleName);
  declareProperty("NtupleName",    m_ntupleName); // alias for backwards compatibility
  declareProperty("ItemList",      m_itemList);
  declareProperty("OutputFile",    m_outputFile);
  declareProperty("OutputLevel",   m_outputLevel);
  declareProperty("OnlyRoI",       m_onlyRoI);
  declareProperty("EtaWindow",     m_etaWindow);
  declareProperty("PhiWindow",     m_phiWindow);
  declareProperty("TruthKey",      m_truthKey);
  declareProperty("InputTruthKey", m_truthKey);
  declareProperty("CellHashes",    m_cellHashes);
}

RootStreamMaker::~RootStreamMaker()
{
  m_handlers.clear();
  if (m_ownsFile && m_file) {
    if (m_file->IsOpen()) {
      m_file->Write();
      m_file->Close();
    }
    delete m_file;
    m_file = nullptr;
  }
}

StatusCode RootStreamMaker::initialize()
{
  CHECK_INIT();
  setMsgLevel(m_outputLevel);

  if (!m_outputFile.empty()) {
    m_file = TFile::Open(m_outputFile.c_str(), "RECREATE");
    if (!m_file || m_file->IsZombie()) {
      MSG_FATAL("Could not open ROOT output file for writing: " << m_outputFile);
      return StatusCode::FAILURE;
    }
    m_ownsFile = true;
    m_file->cd();
    m_tree = new TTree(m_ntupleName.c_str(), m_ntupleName.c_str());
  }

  return StatusCode::SUCCESS;
}

StatusCode RootStreamMaker::setupBranches()
{
  if (!m_tree) {
    return StatusCode::FAILURE;
  }

  if (!m_handlers.empty()) {
    return StatusCode::SUCCESS; // Already configured
  }

  for (const auto &item : m_itemList) {
    if (item.empty()) continue;

    std::string typeName;
    std::string key;

    // Support Type#Key, Type/Key, or Type_Key
    size_t sepPos = item.find('#');
    if (sepPos == std::string::npos) {
      sepPos = item.find('/');
    }
    if (sepPos == std::string::npos) {
      sepPos = item.find('_');
    }

    if (sepPos == std::string::npos) {
      MSG_WARNING("Invalid item specification: '" << item << "'. Expected 'TypeName#Key'. Skipping.");
      continue;
    }

    typeName = item.substr(0, sepPos);
    key = item.substr(sepPos + 1);

    auto handler = BranchHandlerFactory::createHandler(
        typeName, key, m_onlyRoI, m_etaWindow, m_phiWindow, m_truthKey, m_cellHashes);
    if (handler) {
      handler->initWriteBranch(m_tree);
      if (m_onlyRoI && (typeName == "CaloHitContainer" || typeName == "CaloHit")) {
        MSG_INFO("Configured write branch '" << handler->branchName() << "' with RoI filtering (TruthKey: "
                 << m_truthKey << ", EtaWindow: " << m_etaWindow << ", PhiWindow: " << m_phiWindow << ")");
      } else {
        MSG_INFO("Configured write branch '" << handler->branchName() << "' for item: " << item);
      }
      m_handlers.push_back(std::move(handler));
    } else {
      MSG_ERROR("Unknown type '" << typeName << "' in item '" << item << "'. Cannot create branch handler.");
    }
  }

  MSG_INFO("RootStreamMaker setup complete with " << m_handlers.size() << " active branches.");
  return StatusCode::SUCCESS;
}

StatusCode RootStreamMaker::bookHistograms(SG::EventContext &/*ctx*/) const
{
  return StatusCode::SUCCESS;
}

StatusCode RootStreamMaker::pre_execute(SG::EventContext &/*ctx*/) const
{
  return StatusCode::SUCCESS;
}

StatusCode RootStreamMaker::execute(SG::EventContext &/*ctx*/, const G4Step * /*step*/) const
{
  return StatusCode::SUCCESS;
}

StatusCode RootStreamMaker::execute(SG::EventContext &ctx, int /*evt*/) const
{
  return post_execute(ctx);
}

StatusCode RootStreamMaker::post_execute(SG::EventContext &ctx) const
{
  // Initialize tree from EventContext decorator if not owned
  if (!m_tree) {
    auto store = ctx.getStoreGateSvc();
    if (!store) {
      MSG_FATAL("StoreGate service is null!");
      return StatusCode::FAILURE;
    }

    TFile *file = dynamic_cast<TFile*>(static_cast<TObject*>(store->decorator("events")));
    if (file) {
      file->cd();
      TTree *tree = dynamic_cast<TTree*>(file->Get(m_ntupleName.c_str()));
      if (!tree) {
        tree = new TTree(m_ntupleName.c_str(), m_ntupleName.c_str());
      }
      const_cast<RootStreamMaker*>(this)->m_tree = tree;
    } else {
      m_tree = new TTree(m_ntupleName.c_str(), m_ntupleName.c_str());
    }

    if (const_cast<RootStreamMaker*>(this)->setupBranches().isFailure()) {
      return StatusCode::FAILURE;
    }
  }

  for (const auto &handler : m_handlers) {
    if (handler->writeFromContext(ctx).isFailure()) {
      MSG_DEBUG("No container found for branch: " << handler->branchName() << " (key: " << handler->key() << ")");
    }
  }

  m_tree->Fill();
  return StatusCode::SUCCESS;
}

StatusCode RootStreamMaker::fillHistograms(SG::EventContext &/*ctx*/) const
{
  return StatusCode::SUCCESS;
}

StatusCode RootStreamMaker::finalize()
{
  if (m_ownsFile && m_file) {
    m_file->cd();
    m_file->Write();
    m_file->Close();
    delete m_file;
    m_file = nullptr;
    m_tree = nullptr;
  }
  return StatusCode::SUCCESS;
}

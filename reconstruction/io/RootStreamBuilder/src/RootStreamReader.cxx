#include "RootStreamReader.h"
#include "BranchHandlerFactory.h"
#include "TObjArray.h"
#include "TBranch.h"

using namespace Gaugi;

RootStreamReader::RootStreamReader(std::string name)
  : IMsgService(name),
    Algorithm(),
    m_inputFile(""),
    m_ntupleName("CollectionTree"),
    m_outputLevel(1),
    m_file(nullptr),
    m_tree(nullptr),
    m_handlers()
{
  declareProperty("InputFile",   m_inputFile);
  declareProperty("NtupleName",  m_ntupleName);
  declareProperty("OutputLevel", m_outputLevel);
}

RootStreamReader::~RootStreamReader()
{
  m_handlers.clear();
  if (m_file) {
    if (m_file->IsOpen()) {
      m_file->Close();
    }
    delete m_file;
    m_file = nullptr;
  }
}

StatusCode RootStreamReader::initialize()
{
  CHECK_INIT();
  setMsgLevel(m_outputLevel);

  if (m_inputFile.empty()) {
    MSG_FATAL("InputFile property is empty!");
    return StatusCode::FAILURE;
  }

  m_file = TFile::Open(m_inputFile.c_str(), "READ");
  if (!m_file || m_file->IsZombie()) {
    MSG_FATAL("Could not open ROOT input file: " << m_inputFile);
    return StatusCode::FAILURE;
  }

  m_tree = dynamic_cast<TTree*>(m_file->Get(m_ntupleName.c_str()));
  if (!m_tree) {
    MSG_FATAL("Could not find TTree with name '" << m_ntupleName << "' in file: " << m_inputFile);
    return StatusCode::FAILURE;
  }

  MSG_INFO("Opened file '" << m_inputFile << "' with " << m_tree->GetEntries() << " events.");
  return discoverBranches(m_tree);
}

StatusCode RootStreamReader::discoverBranches(TTree *tree)
{
  if (!tree) {
    return StatusCode::FAILURE;
  }

  TObjArray *branchList = tree->GetListOfBranches();
  if (!branchList) {
    MSG_WARNING("No branches found in TTree: " << m_ntupleName);
    return StatusCode::SUCCESS;
  }

  for (int i = 0; i < branchList->GetEntries(); ++i) {
    TBranch *branch = dynamic_cast<TBranch*>(branchList->At(i));
    if (!branch) continue;

    std::string bname = branch->GetName();
    size_t sepPos = bname.find('_');
    if (sepPos == std::string::npos || sepPos == 0 || sepPos == bname.size() - 1) {
      MSG_DEBUG("Skipping branch with non-standard naming: " << bname);
      continue;
    }

    std::string typeName = bname.substr(0, sepPos);
    std::string key = bname.substr(sepPos + 1);

    auto handler = BranchHandlerFactory::createHandler(typeName, key);
    if (handler) {
      handler->initReadBranch(tree);
      MSG_INFO("Auto-discovered branch '" << bname << "' -> Type: " << typeName << ", Key: " << key);
      m_handlers.push_back(std::move(handler));
    } else {
      MSG_DEBUG("No handler factory registered for type '" << typeName << "' (branch: " << bname << ")");
    }
  }

  MSG_INFO("Auto-discovery complete. Registered " << m_handlers.size() << " branch readers.");
  return StatusCode::SUCCESS;
}

StatusCode RootStreamReader::bookHistograms(SG::EventContext &/*ctx*/) const
{
  return StatusCode::SUCCESS;
}

StatusCode RootStreamReader::pre_execute(SG::EventContext &/*ctx*/) const
{
  return StatusCode::SUCCESS;
}

StatusCode RootStreamReader::execute(SG::EventContext &/*ctx*/, const G4Step * /*step*/) const
{
  return StatusCode::SUCCESS;
}

StatusCode RootStreamReader::execute(SG::EventContext &ctx, int evt) const
{
  if (!m_tree) {
    MSG_ERROR("TTree is null during execute!");
    return StatusCode::FAILURE;
  }

  m_tree->GetEntry(evt);

  for (const auto &handler : m_handlers) {
    if (handler->readAndRecord(ctx).isFailure()) {
      MSG_WARNING("Failed to read and record branch: " << handler->branchName());
    }
  }

  return StatusCode::SUCCESS;
}

StatusCode RootStreamReader::post_execute(SG::EventContext &/*ctx*/) const
{
  return StatusCode::SUCCESS;
}

StatusCode RootStreamReader::fillHistograms(SG::EventContext &/*ctx*/) const
{
  return StatusCode::SUCCESS;
}

StatusCode RootStreamReader::finalize()
{
  return StatusCode::SUCCESS;
}

long long RootStreamReader::entries() const
{
  return m_tree ? m_tree->GetEntries() : 0;
}

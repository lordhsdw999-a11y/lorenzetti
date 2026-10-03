#include "GaugiKernel/DataHandle.h"

using namespace SG;

EventContext::EventContext(std::string name) : 
  MsgService(name),
  m_store(nullptr),
  m_threadId(0),
  m_numberOfThreads(1)
{}

EventContext::~EventContext() {
  clear();
}

void EventContext::clear() {
  m_storable_ptr.clear();
  m_hash_to_ptr.clear();
  m_key_to_hash.clear();
  m_hash_to_key.clear();
}

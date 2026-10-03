#ifndef StringHash_h
#define StringHash_h

#include <cstdint>
#include <string>
#include <cstring>

namespace Gaugi {

  /**
   * @brief 64-bit FNV-1a Hash Implementation for Fast String and Key Hashing.
   */
  inline uint64_t fnv1a_64(const char* str, size_t len) {
    uint64_t hash = 14695981039346656037ULL; // FNV offset basis
    for (size_t i = 0; i < len; ++i) {
      hash ^= static_cast<uint64_t>(static_cast<unsigned char>(str[i]));
      hash *= 1099511628211ULL; // FNV prime
    }
    return hash;
  }

  /**
   * @brief Computes 64-bit hash for a given string.
   */
  inline uint64_t stringHash(const std::string& str) {
    return fnv1a_64(str.data(), str.size());
  }

  /**
   * @brief Computes a combined 64-bit hash for (TypeName + "#" + KeyName).
   */
  inline uint64_t hashKey(const std::string& typeName, const std::string& keyName) {
    std::string combined = typeName + "#" + keyName;
    return fnv1a_64(combined.data(), combined.size());
  }

} // namespace Gaugi

#endif

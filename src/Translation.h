#pragma once

#include <vector>
#include <random>

#include "Config.h"
#include "Statistics.h"

namespace Ramulator
{
  class TranslationBase
  {
    public:
      std::vector<int> free_physical_pages;
      uint64_t free_physical_pages_remaining;
      std::map<std::pair<int, uint64_t>, uint64_t> page_translation;
      bool hydra_enabled = false;
      int max_address_pages = 0;

    protected:
      ScalarStat physical_page_replacement;


    public:
      TranslationBase(const YAML::Node& config, uint64_t max_address);

    public:
      virtual uint64_t page_allocator(uint64_t addr, int coreid) = 0;
      virtual void blacklist_page(uint64_t addr) = 0;
      
  };

  class NoTranslation final : public TranslationBase
  {
    using TranslationBase::TranslationBase;
    public:
      uint64_t page_allocator(uint64_t addr, int coreid) override
      {
        return (addr % (free_physical_pages_remaining << 12ULL));
      };
      void blacklist_page(uint64_t addr) override {};
  };

  class RandomTranslation final : public TranslationBase
  {
    private:
      std::mt19937_64 allocator_rng;

    public:
      RandomTranslation(const YAML::Node& config, uint64_t max_address);
      uint64_t page_allocator(uint64_t addr, int coreid) override;
      void blacklist_page(uint64_t addr) override {};
  };

  class LessRandomTranslation final : public TranslationBase
  {
    private:
      std::mt19937_64 allocator_rng;
      int contiguous_allocation_quota;
      int current_contiguously_allocated_pages;
      uint64_t current_base;
      std::vector<uint64_t> blacklist;

    public:
      LessRandomTranslation(const YAML::Node& config, uint64_t max_address);
      uint64_t page_allocator(uint64_t addr, int coreid) override;
      void blacklist_page(uint64_t addr) override 
      {
        blacklist.push_back(addr);
      };
  };

  TranslationBase* make_translation(const YAML::Node& config, uint64_t max_address);
}
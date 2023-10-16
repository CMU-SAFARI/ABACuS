#pragma once

#include "RefreshBasedDefense.h"
#include "Config.h"
#include "Controller.h"

#include <vector>
#include <random>

namespace Ramulator
{
  template <class T>
  class ABACUS : public RefreshBasedDefense<T>
  {
  public:
    ABACUS(const YAML::Node &config, Controller<T>* ctrl);
    ~ABACUS() = default;
    void tick();
    void update(typename T::Command cmd, const std::vector<int> &addr_vec, uint64_t open_for_nclocks, int core_id);
    
    void finish() {}

    std::string to_string()
    {
      return fmt::format("Refresh-based RowHammer Defense\n"
                         "  └  "
                         "ABACUS\n"
                         "  └  "
                         "Probability threshold: {}\n", probability_threshold);
    }

  private:
    struct COUNT_ENTRY{
      int count;
      uint64_t bank_bv; // bank bit vector
    };
    // probability threshold for ABACUS
    float probability_threshold;
    float para_engage_threshold;
    // a random number generator
    std::mt19937 generator;
    // a uniform distribution between 0 and 1
    std::uniform_real_distribution<float> distribution;
    int no_table_entries;
    int activation_threshold;
    int rowhammer_threshold;
    int reset_period;
    int reset_period_clk;
    bool debug = false;
    bool debug_verbose = false;
    bool graphene_only;
    bool counter_per_core;
    bool reset_on_spillover;
    bool accessed_row_filter_enable;
    bool abacus_big;

    int num_cores;

    uint64_t clk;

    // per core/thread activation count table
    // indexed using core_id, tagged using rank,bank,row id
    std::vector<std::unordered_map<int, struct COUNT_ENTRY>> activation_count_table;
    // spillover counter per core/thread
    std::vector<int> spillover_counter;
    // per row activation count table
    std::vector<struct COUNT_ENTRY> per_row_activation_count_table;
    bool para_engaged;

    std::vector<bool> accessed_row_filter;

    VectorStat activates_received_during_graphene;
    VectorStat activates_received_during_para;
    VectorStat activates_received_during_para_but_in_table;

    void completely_refresh_dram_rank(int no_ranks);
    void refresh_only_accessed_rows(int no_ranks);

  };
};

#include "ABACUS.tpp"
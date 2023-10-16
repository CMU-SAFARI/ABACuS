#pragma once

#include "RefreshBasedDefense.h"
#include "Config.h"
#include "Controller.h"

#include <vector>
#include <random>

/**
 * Things that are hard coded:
 * 1. RCC size is 4K entries per rank
 * 2. refresh period is 64 ms
 * 3. Each row group stores 128 rows
 * 4. each row activation counter is 2 bytes
*/
namespace Ramulator
{
  template <class T>
  class Hydra : public RefreshBasedDefense<T>
  {
  public:
    Hydra(const YAML::Node &config, Controller<T>* ctrl);
    ~Hydra() = default;
    void tick();
    void update(typename T::Command cmd, const std::vector<int> &addr_vec, uint64_t open_for_nclocks, int core_id = 0);
    
    void finish() {}

    std::string to_string()
    {
      return fmt::format("Refresh-based RowHammer Defense\n"
                         "  └  "
                         "Hydra\n");
    }

  private:
    struct GCT_ENTRY{
      int count;
      bool initialized;
    };

    // RNG for evictions
    std::mt19937 generator;
    std::uniform_int_distribution<int> distribution;

    uint64_t clk;
    int no_columns_per_row;
    uint64_t reset_period_clk = 0;
    int reset_period;

    // Hydra: "We use 32K entry GCT. This means a row-group consists of 128-rows"
    std::vector<std::vector<struct GCT_ENTRY>> group_count_table;
    //std::vector<std::vector<struct RCC_ENTRY>> row_count_cache;
    // 32-way set associative
    std::vector<std::vector<std::unordered_map<int, int>>> row_count_cache;
    // the actual row count table
    std::vector<int> row_count_table;
    // the SRAM row count table for the row count table itself
    std::vector<int> row_count_table_count_table;

    int hydra_required_rows_per_bank = 0;  
    const int row_group_size = 128; // should remain constant across Hydra configurations?
    int group_threshold = 200; // T_{G} in the paper. By default it is 200.
    int tracking_threshold = 250; // T_{H} in the paper. By default it is 250.

    bool debug = false;

    ScalarStat rcc_hits;
    ScalarStat rcc_misses;
    ScalarStat rcc_evictions;

    Request generate_counter_update_request(const std::vector<int> &aggr_addr_vec);
    Request generate_counter_read_request(const std::vector<int> &aggr_addr_vec);
    std::vector<int> get_counter_table_address(const std::vector<int> &aggr_addr_vec);

    int get_tag_to_evict(int rank_id, int row_cache_index);
  };
};

#include "Hydra.tpp"
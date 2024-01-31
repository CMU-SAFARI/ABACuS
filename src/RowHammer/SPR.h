#pragma once

#include "RefreshBasedDefense.h"
#include "Config.h"
#include "Controller.h"
#include "Statistics.h"

#include <vector>
#include <unordered_map>
#include <random>
#include <fstream>

namespace Ramulator
{
  template <class T>
  /**
   * Slow Start RowHammer Defense (SPR)
  */
  class SPR : public RefreshBasedDefense<T>
  {
  public:
    SPR(const YAML::Node &config, Controller<T>* ctrl);
    ~SPR() = default;

    void tick();
    void update(typename T::Command cmd, const std::vector<int> &addr_vec, uint64_t open_for_nclocks, int core_id = 0);
    void finish();

    std::string to_string()
    {
    return fmt::format("Refresh-based RowHammer Defense\n"
                        "  └  "
                        "SPR\n");
    }

  private:
    struct RPT_ENTRY{
      float probability;
      uint64_t last_activation_timestamp;
      bool first_time;
    };

    uint64_t clk;
    std::vector<int> row_address_index_bits;
    int timeout_cycles;
    float initial_probability;
    float probability_multiplier;
    float probability_divider;
    float probability_lower_limit;
    bool debug;
    bool debug_verbose;
    bool log_activation_period;
    int nRC;
    int nREFW;
    int rowhammer_threshold;
    bool go_back_to_zero;
    bool stabilize_at_para;
    float para_threshold;
    bool go_back_to_zero_after_refresh;
    bool disable_probability_stats;
    std::string activation_period_file_name;
    std::ofstream act_dump_to_file;

    // per bank refresh probability table
    std::vector<std::vector<RPT_ENTRY>> refresh_probability_table;
    int table_size;

    // useful stats
    VectorStat avg_refresh_probability;
    VectorStat sum_refresh_probability;

    // a random number generator
    std::mt19937 generator;
    // a uniform distribution between 0 and 1
    std::uniform_real_distribution<float> distribution;
  };
}

#include "SPR.tpp"
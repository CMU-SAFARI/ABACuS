#include "Hydra.h"

namespace Ramulator
{
  
  template <class T>
  Hydra<T>::Hydra(const YAML::Node &config, Controller<T>* ctrl) : RefreshBasedDefense<T>(config, ctrl)
  {
    debug = config["debug"].as<bool>();
    group_threshold = config["group_threshold"].as<int>(200);
    tracking_threshold = config["tracking_threshold"].as<int>(250);
    reset_period = config["reset_period"].as<int>();

    // Get organization configuration
    this->no_rows_per_bank = ctrl->channel->spec->org_entry.count[int(T::Level::Row)];
    this->no_bank_groups = ctrl->channel->spec->org_entry.count[int(T::Level::BankGroup)];
    this->no_banks = ctrl->channel->spec->org_entry.count[int(T::Level::Bank)];
    this->no_ranks = ctrl->channel->spec->org_entry.count[int(T::Level::Rank)];
    no_columns_per_row = ctrl->channel->spec->org_entry.count[int(T::Level::Column)];
    // initialize group count table
    group_count_table.resize(this->no_ranks * this->no_bank_groups * this->no_banks);
    // initialize every group_count_table entry to a vector of size no_rows_per_bank/row_group_size
    for (int i = 0; i < this->no_ranks * this->no_bank_groups * this->no_banks; i++)
    {
      group_count_table[i].resize(this->no_rows_per_bank/row_group_size);
      for (int j = 0; j < this->no_rows_per_bank/row_group_size; j++)
      {
        group_count_table[i][j].count = 0;
        group_count_table[i][j].initialized = false;
      }
    }

    // Hydra: "we provision an RCC containing 8K-entries (4K-entries per rank)"
    // initialize row-count cache
    row_count_cache.resize(this->no_ranks);
      // because it is going to be 32-ways, each rank gets 256 entries
    for (int i = 0; i < this->no_ranks; i++)
      row_count_cache[i].resize(256);

    // initialize row count table, one entry per row
    row_count_table.resize(this->no_ranks * this->no_bank_groups * this->no_banks * this->no_rows_per_bank);
  
    hydra_required_rows_per_bank = (this->no_rows_per_bank * 2) / (no_columns_per_row * 8);
    row_count_table_count_table.resize(this->no_ranks * this->no_bank_groups * this->no_banks * hydra_required_rows_per_bank);

    // X miliseconds / clock period in nanoseconds
    reset_period_clk = (uint64_t) (reset_period / (((float) ctrl->channel->spec->speed_entry[int(T::TimingCons::tCK_ps)])/1000));

    rcc_hits
      .name("row_count_cache_hits_channel_" + std::to_string(ctrl->channel->id))
      .desc("The amount of times the row count cache was hit")
      .precision(0)
      ;

    rcc_misses
      .name("row_count_cache_misses_channel_" + std::to_string(ctrl->channel->id))
      .desc("The amount of times the row count cache was missed")
      .precision(0)
      ;

    rcc_evictions
      .name("row_count_cache_evictions_channel_" + std::to_string(ctrl->channel->id))
      .desc("The amount of times there was an eviction from the row count cache")
      .precision(0)
      ;

    // initialize random number generator
    generator = std::mt19937(1337);
    // initialize uniform distribution
    distribution = std::uniform_int_distribution<int>(0, 31);
  }

  template <class T>
  void Hydra<T>::tick()
  {
    clk++;
    // if 64 miliseconds have passed, reset row count cache and group count table
    if ((clk % reset_period_clk) == 0)
    {
      for (int i = 0; i < this->no_ranks; i++)
      {
        // erase all entries
        for (int j = 0; j < 256; j++)
          row_count_cache[i][j].erase(row_count_cache[i][j].begin(), row_count_cache[i][j].end());
      }
      for (int i = 0; i < this->no_ranks * this->no_bank_groups * this->no_banks; i++)
      {
        for (int j = 0; j < this->no_rows_per_bank/row_group_size; j++)
        {
          group_count_table[i][j].count = 0;
          group_count_table[i][j].initialized = false;
        }
      }
      // and reset the row_count_table_count_table
      for (int i = 0; i < this->no_ranks * this->no_bank_groups * this->no_banks * hydra_required_rows_per_bank; i++)
        row_count_table_count_table[i] = 0;
    }
    this->schedule_preventive_refreshes();
  }

  template <class T>
  void Hydra<T>::update(typename T::Command cmd, const std::vector<int> &addr_vec, uint64_t open_for_nclocks, int core_id)
  {
    if (cmd != T::Command::PRE)
      return;

    int bank_group_id = addr_vec[int(T::Level::BankGroup)];
    int bank_id = addr_vec[int(T::Level::Bank)];
    int rank_id = addr_vec[int(T::Level::Rank)];
    int row_id = addr_vec[int(T::Level::Row)];

    // primary_index points to the row groups in the bank targeted by the request
    int primary_index = rank_id * this->no_banks * this->no_bank_groups + bank_group_id * this->no_banks + bank_id;

    // if this request went to the counter table, handle it differently
    if (row_id < hydra_required_rows_per_bank)
    {
      // this->no_ranks * this->no_bank_groups * this->no_banks * hydra_required_rows_per_bank
      assert((primary_index * hydra_required_rows_per_bank + row_id) >= 0);
      assert((primary_index * hydra_required_rows_per_bank + row_id) < (this->no_ranks * this->no_bank_groups * this->no_banks * hydra_required_rows_per_bank));
      row_count_table_count_table[primary_index * hydra_required_rows_per_bank + row_id]++;
      if (debug)
        std::cout << "Hydra: row_count_table_count_table[" << primary_index * hydra_required_rows_per_bank + row_id << "] = " << row_count_table_count_table[primary_index * hydra_required_rows_per_bank + row_id] << std::endl;
      if (row_count_table_count_table[primary_index * hydra_required_rows_per_bank + row_id] >= tracking_threshold)
      {
        if (debug)
          std::cout << "Performing a preventive refresh in the row count table" << std::endl;
        // enqueue a preventive refresh to this row
        this->enqueue_preventive_refresh(addr_vec);
        row_count_table_count_table[primary_index * hydra_required_rows_per_bank + row_id] = 0;
      }
      return;
    }

    // secondary_index points to the row group entry in the bank
    int secondary_index = 0;
    // Hydra wants 128-row row groups. 
    // It uses the least significant n bits to index the row group.
    // (where n is log2(no_rows) - log2(row_group_size))
    int row_address_bits = log2(this->no_rows_per_bank);
    int row_group_bits = log2(this->row_group_size);
    secondary_index = (row_id >> row_group_bits);

    assert(primary_index < (this->no_ranks * this->no_bank_groups * this->no_banks));
    assert(secondary_index < (this->no_rows_per_bank/this->row_group_size));

    assert((primary_index * this->no_rows_per_bank + row_id) < (this->no_ranks * this->no_bank_groups * this->no_banks * this->no_rows_per_bank));

    // Step 1, check group count table
    if (group_count_table[primary_index][secondary_index].count >= group_threshold)
    {
      if (debug)
        std::cout << "Group exceeds group threshold" << " ra: " << rank_id << " bg: " << bank_group_id << " b: " << bank_id << " ro: " << row_id << std::endl;
      // Step 1.1, only once after periodic reset: initialize row counter table entries in memory
      if (group_count_table[primary_index][secondary_index].initialized == false)
      {
        if (debug)
          std::cout << "Initializing row counter table entries in the group" << " ra: " << rank_id << " bg: " << bank_group_id << " b: " << bank_id << " ro: " << row_id << std::endl;
        int row_id_begin = secondary_index << row_group_bits;
        int row_id_end = row_id_begin + this->row_group_size;

        assert(row_id_end <= this->no_rows_per_bank);

        // initialize the simulated row count table entries
        for (int i = row_id_begin; i < row_id_end; i++)
          row_count_table[primary_index * this->no_rows_per_bank + i] = group_threshold;

        std::vector<int> addr_vec_begin = addr_vec;
        addr_vec_begin[int(T::Level::Row)] = row_id_begin;
        // this points to the column that stores the activation
        // count for the first row in this group
        addr_vec_begin = get_counter_table_address(addr_vec_begin);

        std::vector<int> addr_vec_end = addr_vec;
        addr_vec_end[int(T::Level::Row)] = row_id_end;
        // this points to the last column that stores the activation
        // count for the last row in this group
        addr_vec_end = get_counter_table_address(addr_vec_end);

        // starting from the column address of addr_vec_begin,
        // until the column address of addr_vec_end, generate
        // a new write request
        for (int i = addr_vec_begin[int(T::Level::Column)]; i <= addr_vec_end[int(T::Level::Column)]; i++)
        {
          std::vector<int> addr_vec_request = addr_vec_begin;
          addr_vec_request[int(T::Level::Column)] = i;
          Request init_counter_table_req(addr_vec_request, Request::Type::WRITE, nullptr);
          this->ctrl->priority_enqueue(init_counter_table_req);
        }

        group_count_table[primary_index][secondary_index].initialized = true;
      }

      // Step 2, access row count cache to check if the row is already in the cache
      // 256 sets in the cache, we use 8 least significant bits of the row address to index the cache
      int row_cache_index = row_id & 0xFF;
      // the remaining bits in the row address along with the bank address bits are used as the tag
      int row_cache_tag = (row_id >> 8) 
                          | (bank_id << (row_address_bits - 8)) 
                          | (bank_group_id << (row_address_bits - 8 + ((int)log2(this->no_banks))));

      assert((rank_id >= 0) && (rank_id < this->no_ranks));

      // find in row_count_cache[rank_id] if row_cache_tag is present as a key
      auto entry = row_count_cache[rank_id][row_cache_index].find(row_cache_tag);
      if (entry != row_count_cache[rank_id][row_cache_index].end())
      {
        if (debug)
        {
          std::cout << "Row count cache hit" << " ra: " << rank_id << " bg: " << bank_group_id << " b: " << bank_id << " ro: " << row_id << std::endl;
          std::cout << "row_count_cache[" << rank_id << "][" << row_cache_index << "].tag = " << entry->second << std::endl;
        }
        rcc_hits++;
        // Step 3, if the row is cached, increment the row count
        entry->second++;
        // Step 4, if the row count is greater than the threshold, schedule a refresh
        if (entry->second >= tracking_threshold)
        {
          this->enqueue_preventive_refresh(addr_vec);
          entry->second = 0;
        }
      }
      else
      {
        if (debug)
          std::cout << "Row count cache miss" << " ra: " << rank_id << " bg: " << bank_group_id << " b: " << bank_id << " ro: " << row_id << std::endl;
          
        rcc_misses++;
        // Step 3, if the row is not cached, replace the cache entry with the new row
        if (row_count_cache[rank_id][row_cache_index].size() == 32)
        {
          int evict_tag = get_tag_to_evict(rank_id, row_cache_index);

          if (debug)
          {
            std::cout << "Replacing row count cache entry" << " ra: " << rank_id << " bg: " << bank_group_id << " b: " << bank_id << " ro: " << row_id << std::endl;
            std::cout << "row_count_cache[" << rank_id << "][" << row_cache_index << "].tag = " << evict_tag << std::endl;
          }
          rcc_evictions++;
          // get the address from the tag and row_cache_index
          int evict_row_id = ((evict_tag & (row_address_bits - 8)) << 8) | row_cache_index;
          int evict_bank_id = (evict_tag >> (row_address_bits - 8)) & ((1 << ((int)log2(this->no_banks))) - 1);
          int evict_bank_group_id = (evict_tag >> (row_address_bits - 8 + ((int)log2(this->no_banks)))) & ((1 << ((int)log2(this->no_bank_groups))) - 1);
          std::vector<int> evict_addr_vec = addr_vec;
          evict_addr_vec[int(T::Level::Row)] = evict_row_id;
          evict_addr_vec[int(T::Level::Bank)] = evict_bank_id;
          evict_addr_vec[int(T::Level::BankGroup)] = evict_bank_group_id;
          // Create the appropriate request to access row counter table in DRAM
          Request update_counter_req = generate_counter_update_request(evict_addr_vec);
          if (!this->ctrl->priority_enqueue(update_counter_req))
          {
            std::cerr << "Hydra: Failed to enqueue counter update request" << std::endl;
            exit(1);
          }
          int evict_primary_index = rank_id * this->no_banks * this->no_bank_groups + evict_bank_group_id * this->no_banks + evict_bank_id;
          assert((evict_primary_index * this->no_rows_per_bank + evict_row_id) < (this->no_ranks * this->no_bank_groups * this->no_banks * this->no_rows_per_bank));
          row_count_table[evict_primary_index * this->no_rows_per_bank + evict_row_id] = row_count_cache[rank_id][row_cache_index].find(evict_tag)->second;
          row_count_cache[rank_id][row_cache_index].erase(evict_tag);
        }
        // Second we retrieve the row count from DRAM
        Request read_counter_req = generate_counter_read_request(addr_vec);
        if (!this->ctrl->priority_enqueue(read_counter_req))
        {
          std::cerr << "Hydra: Failed to enqueue counter read request" << std::endl;
          exit(1);
        }

        // Third, we can evict the old row from the cache and insert the new row
        row_count_table[primary_index * this->no_rows_per_bank + row_id]++;
        row_count_cache[rank_id][row_cache_index].insert({row_cache_tag, row_count_table[primary_index * this->no_rows_per_bank + row_id]});

        // Step 4, if the row count is greater than the threshold, schedule a refresh
        if (row_count_cache[rank_id][row_cache_index].find(row_cache_tag)->second >= tracking_threshold)
        {
          this->enqueue_preventive_refresh(addr_vec);
          row_count_cache[rank_id][row_cache_index].find(row_cache_tag)->second = 0;
        }
      }
    }
    else
    {
      // increment group count table
      group_count_table[primary_index][secondary_index].count++;
      if (debug)
        std::cout << "Hydra: Group count for ra:" << rank_id << " bg: " << bank_group_id << " b: " << bank_id << " ro: " << row_id << " is " << group_count_table[primary_index][secondary_index].count << std::endl;
    }
  }

  template <class T>
  Request Hydra<T>::generate_counter_update_request(const std::vector<int> &aggr_addr_vec)
  {
    std::vector<int> row_counter_table_address = get_counter_table_address(aggr_addr_vec);
    Request req(row_counter_table_address, Request::Type::WRITE, nullptr);
    return req;
  }

  template <class T>
  Request Hydra<T>::generate_counter_read_request(const std::vector<int> &aggr_addr_vec)
  {
    std::vector<int> row_counter_table_address = get_counter_table_address(aggr_addr_vec);
    Request req(row_counter_table_address, Request::Type::READ, nullptr);
    return req;
  }


  template <class T>
  std::vector<int> Hydra<T>::get_counter_table_address(const std::vector<int> &aggr_addr_vec)
  {
    std::vector<int> new_addr_vec;
    new_addr_vec.resize(aggr_addr_vec.size());

    // copy the old address vector
    for (size_t i = 0; i < aggr_addr_vec.size(); i++)
      new_addr_vec[i] = aggr_addr_vec[i];

    new_addr_vec[int(T::Level::Row)] = (aggr_addr_vec[int(T::Level::Row)] * 2) / (no_columns_per_row * 8);
    new_addr_vec[int(T::Level::Column)] = ((aggr_addr_vec[int(T::Level::Row)] * 2) % (no_columns_per_row * 8)) >> 3;

    return new_addr_vec;
  }

  template <class T>
  int Hydra<T>::get_tag_to_evict(int rank_id, int row_cache_index)
  {
    int tag_index = distribution(generator);
    // select the tag of the tag_index'th entry in row_count_cache[rank_id][row_cache_index]
    auto it = row_count_cache[rank_id][row_cache_index].begin();
    std::advance(it, tag_index);
    return it->first;
  }

};

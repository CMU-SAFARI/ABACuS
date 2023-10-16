#include "ABACUS.h"

namespace Ramulator
{
  
  template <class T>
  ABACUS<T>::ABACUS(const YAML::Node &config, Controller<T>* ctrl) : RefreshBasedDefense<T>(config, ctrl)
  {
    probability_threshold = config["probability_threshold"].as<float>();
    no_table_entries = config["no_table_entries"].as<int>();
    activation_threshold = config["activation_threshold"].as<int>();
    para_engage_threshold = config["para_engage_threshold"].as<int>();
    rowhammer_threshold = config["rowhammer_threshold"].as<int>();
    reset_period = config["reset_period"].as<int>();
    num_cores = config["num_cores"].as<int>();
    debug = config["debug"].as<bool>();
    debug_verbose = config["debug_verbose"].as<bool>();
    graphene_only = config["graphene_only"].as<bool>();
    counter_per_core = config["counter_per_core"].as<bool>();
    reset_on_spillover = config["reset_on_spillover"].as<bool>();
    accessed_row_filter_enable = config["accessed_row_filter"].as<bool>(false);
    abacus_big = config["abacus_big"].as<bool>(false);

    reset_period_clk = (int) (reset_period / (((float) ctrl->channel->spec->speed_entry[int(T::TimingCons::tCK_ps)])/1000));

    // Get organization configuration
    this->no_rows_per_bank = ctrl->channel->spec->org_entry.count[int(T::Level::Row)];
    this->no_bank_groups = ctrl->channel->spec->org_entry.count[int(T::Level::BankGroup)];
    this->no_banks = ctrl->channel->spec->org_entry.count[int(T::Level::Bank)];
    this->no_ranks = ctrl->channel->spec->org_entry.count[int(T::Level::Rank)];

    if (!counter_per_core)
      num_cores = 1;

    // initialize activation count table
    // and spillover counter    
    for (int i = 0 ; i < num_cores ; i++)
    {
      std::unordered_map<int, struct COUNT_ENTRY> table;
      for (int j = -65536; j < -65536 + no_table_entries; j++)
      {
        struct COUNT_ENTRY entry;
        entry.count = 0;
        entry.bank_bv = 0;
        table.insert(std::make_pair(j, entry));
      }
      activation_count_table.push_back(table);
      spillover_counter.push_back(0);
    }

    // initialize accessed row filter with no_rows_per_bank entries, just use resize
    if (accessed_row_filter_enable)
    {
      accessed_row_filter.resize(this->no_rows_per_bank);
      for (int i = 0 ; i < this->no_rows_per_bank ; i++)
        accessed_row_filter[i] = false;
    }

    // initialize per row activation count table
    if (abacus_big)
    {
      for (int i = 0 ; i < this->no_rows_per_bank ; i++)
      {
        struct COUNT_ENTRY entry;
        entry.count = 0;
        entry.bank_bv = 0;
        per_row_activation_count_table.push_back(entry);
      }
    }

    // initialize random number generator
    generator = std::mt19937(1337);
    // initialize uniform distribution
    distribution = std::uniform_real_distribution<float>(0.0, 1.0);

    para_engaged = false;

    clk = 0;

    activates_received_during_graphene
      .init(num_cores)
      .name("activates_received_during_graphene_core_")
      .desc("Number of activates received during graphene")
      ;
    
    activates_received_during_para
      .init(num_cores)
      .name("activates_received_during_para_core_")
      .desc("Number of activates received during para")
      ;

    activates_received_during_para_but_in_table
      .init(num_cores)
      .name("activates_received_during_para_core_but_in_table")
      .desc("Number of activates received during para but looked up in the table and handled by graphene")
      ;
  }

  template <class T>
  void ABACUS<T>::tick()
  {
    this->schedule_preventive_refreshes();

    // reset activation count table every reset_period
    // by setting every element to 0
    // and reset spillover counter
    if (clk % reset_period_clk == 0)
    {
      for (int i = 0 ; i < num_cores ; i++)
      {
        for (auto it = activation_count_table[i].begin(); it != activation_count_table[i].end(); it++)
        {
          it->second.count = 0;
          it->second.bank_bv = 0;
        }
        spillover_counter[i] = 0;
      }
      para_engaged = false;

      // reset accessed row filter
      if (accessed_row_filter_enable)
      {
        for (int i = 0 ; i < this->no_rows_per_bank ; i++)
          accessed_row_filter[i] = false;
      }

      if (abacus_big)
      {
        for (int i = 0 ; i < this->no_rows_per_bank ; i++)
        {
          per_row_activation_count_table[i].count = 0;
          per_row_activation_count_table[i].bank_bv = 0;
        }
      }
    }

    clk++;
  }

  template <class T>
  void ABACUS<T>::update(typename T::Command cmd, const std::vector<int> &addr_vec, uint64_t open_for_nclocks, int core_id)
  {
    if (cmd != T::Command::PRE)
      return;

    if (!counter_per_core)
      core_id = 0;

    if (!para_engaged)
      activates_received_during_graphene[core_id]++;
    else
      activates_received_during_para[core_id]++;

    if (accessed_row_filter_enable)
      accessed_row_filter[addr_vec[int(T::Level::Row)]] = true;

    int tag = addr_vec[int(T::Level::Row)];

    int flat_bank_id = addr_vec[int(T::Level::Bank)] +
                       addr_vec[int(T::Level::BankGroup)] * this->no_banks +
                       addr_vec[int(T::Level::Rank)] * this->no_banks * this->no_bank_groups;

    //if (debug_verbose)
    //  std::cout << "core_id: " << core_id << " tag: " << tag << " activation count: " << activation_count_table[core_id][tag].count << " activation bv: "  << activation_count_table[core_id][tag].bank_bv << " flat_bank_id: " << flat_bank_id << std::endl;

    if (!abacus_big)
    {
      // check if the row is already in the table
      if (!para_engaged && (activation_count_table[core_id].find(tag) == activation_count_table[core_id].end()))
      {
        // if row is not in the table, find an entry 
        // with a count equal to that of the spillover counter
        bool found = false;
        int to_remove = -1;
        int spillover_value = -1;

        for (auto it = activation_count_table[core_id].begin(); it != activation_count_table[core_id].end(); it++)
        {
          if (debug_verbose)
            std::cout << "  └  " << "checking row " << it->first << " with count " << it->second.count << std::endl;

          if (it->second.count == spillover_counter[core_id])
          {
            // if we find an entry, record it
            spillover_value = it->second.count;
            to_remove = it->first;
            found = true;
            break;
          }
        }
        if (found)
        {
          // for debug
          if (debug_verbose)
          {
            // print the row that is being removed
            std::cout << "Removing row " << to_remove << " from table " << tag << std::endl;
            // print the row that is being added
            std::cout << "Adding row " << tag << " to table " << tag << std::endl;
            std::cout << "  └  " << "spillover counter: " << spillover_counter[core_id] << std::endl;
          }
          // remove to_remove from the table
          activation_count_table[core_id].erase(to_remove);
          // add tag to the table
          activation_count_table[core_id][tag].count = spillover_value + 1;
          activation_count_table[core_id][tag].bank_bv = (1 << flat_bank_id);
        }
        // if we did not find such an entry, increment spillover counter by one
        else
        {
          int increment = 1;
          spillover_counter[core_id] += increment;

          if (!graphene_only)
          {
            if (spillover_counter[core_id] == para_engage_threshold)
            {
              para_engaged = true;
              if (debug)
                std::cout << "Para engaged!" << std::endl;
            }
          }
        }
      }
      else if (!para_engaged)
      {
        // if row in table, check its bank bv
        // if the bank bv is 0, set it to 1
        bool is_set = (activation_count_table[core_id][tag].bank_bv >> flat_bank_id) & 1;

        // we need to increment the counter and reset bank_bv
        if (is_set)
        {
          activation_count_table[core_id][tag].count += 1;
          activation_count_table[core_id][tag].bank_bv = 0 | (1 << flat_bank_id);
        }
        else
        {
          activation_count_table[core_id][tag].bank_bv |= (1 << flat_bank_id);
        }
        
        if (debug_verbose)
        {
          std::cout << "Row " << tag << " in table[" << core_id << "]" << std::endl;
          std::cout << "  └  " << "threshold: " << activation_threshold << std::endl;
          std::cout << "  └  " << "count: " << activation_count_table[core_id][tag].count << std::endl;
          std::cout << "  └  " << "bank_bv: " << activation_count_table[core_id][tag].bank_bv << std::endl;
        }

        // check if the count exceeds the threshold
        if (activation_count_table[core_id][tag].count >= activation_threshold)
        {
          if (debug)
            std::cout << "Row " << tag << " in table " << core_id << " has exceeded the threshold!" << " Spillover counter value: " << spillover_counter[core_id] << std::endl;
          // if yes, schedule preventive refreshes
          for (int i = 0; i < this->no_ranks; i++)
          {
            for (int j = 0; j < this->no_bank_groups; j++)
            {
              std::vector<int> new_addr_vec = addr_vec;
              for (int k = 0; k < this->no_banks; k++)
              {
                new_addr_vec[int(T::Level::Bank)] = k;
                new_addr_vec[int(T::Level::BankGroup)] = j;
                new_addr_vec[int(T::Level::Rank)] = i;
                this->enqueue_preventive_refresh(new_addr_vec);
              }
            }
          }
          activation_count_table[core_id][tag].count = spillover_counter[core_id];
          activation_count_table[core_id][tag].bank_bv = 0;
        }
      }
      else
      {
        // even when para is engaged, we count the activation counts of rows inside the table
        // and do PARA for the rest of the rows
        if (activation_count_table[core_id].find(tag) != activation_count_table[core_id].end())
        {
          activates_received_during_para_but_in_table[core_id]++;

          // if row in table, check its bank bv
          // if the bank bv is 0, set it to 1
          bool is_set = (activation_count_table[core_id][tag].bank_bv >> flat_bank_id) & 1;

          // we need to increment the counter and reset bank_bv
          if (is_set)
          {
            activation_count_table[core_id][tag].count += 1;
            activation_count_table[core_id][tag].bank_bv = 0 | (1 << flat_bank_id);
          }
          else
          {
            activation_count_table[core_id][tag].bank_bv |= (1 << flat_bank_id);
          }
          
          if (debug_verbose)
          {
            std::cout << "Row " << tag << " in table[" << core_id << "]" << std::endl;
            std::cout << "  └  " << "threshold: " << activation_threshold << std::endl;
            std::cout << "  └  " << "count: " << activation_count_table[core_id][tag].count << std::endl;
            std::cout << "  └  " << "bank_bv: " << activation_count_table[core_id][tag].bank_bv << std::endl;
          }

          // check if the count exceeds the threshold
          if (activation_count_table[core_id][tag].count >= activation_threshold)
          {
            if (debug)
              std::cout << "Row " << tag << " in table " << core_id << " has exceeded the threshold!" << " Spillover counter value: " << spillover_counter[core_id] << std::endl;
            // if yes, schedule preventive refreshes
            for (int i = 0; i < this->no_ranks; i++)
            {
              for (int j = 0; j < this->no_bank_groups; j++)
              {
                std::vector<int> new_addr_vec = addr_vec;
                for (int k = 0; k < this->no_banks; k++)
                {
                  new_addr_vec[int(T::Level::Bank)] = k;
                  new_addr_vec[int(T::Level::BankGroup)] = j;
                  new_addr_vec[int(T::Level::Rank)] = i;
                  this->enqueue_preventive_refresh(new_addr_vec);
                }
              }
            }
            activation_count_table[core_id][tag].count = 0;
            activation_count_table[core_id][tag].bank_bv = 0;
          }
        }
        else
        {
          // if RNG produces a number less than probability_threshold
          // schedule a preventive refresh
          if (distribution(generator) < probability_threshold)
          {
            this->enqueue_preventive_refresh(addr_vec);
          }
        }
      }

      if (spillover_counter[core_id] > (activation_threshold - 10))
      {
        if (!accessed_row_filter_enable)
          completely_refresh_dram_rank(this->no_ranks);
        else
          refresh_only_accessed_rows(this->no_ranks);
        // reset activation count table by iterating over all core_id and tags
        for (int i = 0 ; i < num_cores ; i++)
        {
          for (auto it = activation_count_table[i].begin(); it != activation_count_table[i].end(); it++)
          {
            it->second.count = 0;
            it->second.bank_bv = 0;
          }
        }
        // reset spillover counter by iterating over all core_id
        for (int i = 0 ; i < num_cores ; i++)
          spillover_counter[i] = 0;

        // reset accessed row filter
        if (accessed_row_filter_enable)
        {
          for (int i = 0 ; i < this->no_rows_per_bank ; i++)
            accessed_row_filter[i] = false;
        }
      }
    }
    else // abacus_big
    {
      // if row in table, check its bank bv
      // if the bank bv is 0, set it to 1
      bool is_set = (per_row_activation_count_table[tag].bank_bv >> flat_bank_id) & 1;

      // we need to increment the counter and reset bank_bv
      if (is_set)
      {
        per_row_activation_count_table[tag].count += 1;
        per_row_activation_count_table[tag].bank_bv = 0 | (1 << flat_bank_id);
      }
      else
      {
        per_row_activation_count_table[tag].bank_bv |= (1 << flat_bank_id);
      }

      if (debug_verbose)
      {
        std::cout << "Row " << tag << " in table[" << 0 << "]" << std::endl;
        std::cout << "  └  " << "threshold: " << activation_threshold << std::endl;
        std::cout << "  └  " << "count: " << per_row_activation_count_table[tag].count << std::endl;
        std::cout << "  └  " << "bank_bv: " << per_row_activation_count_table[tag].bank_bv << std::endl;
      }
      // check the count of the row and schedule a refresh if necessary
      if (per_row_activation_count_table[tag].count >= activation_threshold)
      {
        if (debug)
          std::cout << "Row " << tag << " in table " << 0 << " has exceeded the threshold!" << std::endl;
        // if yes, schedule preventive refreshes
        for (int i = 0; i < this->no_ranks; i++)
        {
          for (int j = 0; j < this->no_bank_groups; j++)
          {
            std::vector<int> new_addr_vec = addr_vec;
            for (int k = 0; k < this->no_banks; k++)
            {
              new_addr_vec[int(T::Level::Bank)] = k;
              new_addr_vec[int(T::Level::BankGroup)] = j;
              new_addr_vec[int(T::Level::Rank)] = i;
              this->enqueue_preventive_refresh(new_addr_vec);
            }
          }
        }
        per_row_activation_count_table[tag].count = 0;
        per_row_activation_count_table[tag].bank_bv = 0;
      }
    }
  }

  template <class T>
  void ABACUS<T>::completely_refresh_dram_rank(int no_ranks)
  {
    // reset_period * 2 is the refresh period
    // divide by tREFI to get the number of refreshes needed
    int nREFI = this->ctrl->channel->spec->speed_entry[int(T::TimingCons::nREFI)];
    int number_of_refreshes = (reset_period_clk * 2) / nREFI;

    if (debug)
      std::cout << "Completely refreshing dram ranks " << no_ranks << " with number of refreshes: " << number_of_refreshes << std::endl;

    for (int i = 0 ; i < number_of_refreshes; i++)
    {
      // Refresh request to rank_id
      std::vector<int> addr_vec(int(T::Level::MAX), -1);
      addr_vec[0] = this->ctrl->channel->id;

      Request req(addr_vec, Request::Type::REFRESH, nullptr);

      for (int j = 0 ; j < no_ranks ; j++)
      {
        req.addr_vec[int(T::Level::Rank)] = j;
        bool what = this->ctrl->priority_enqueue(req);
        assert(what);
      }
    }
  }

  template <class T>
  void ABACUS<T>::refresh_only_accessed_rows(int no_ranks)
  {
    // for each row in the accessed row filter
    // activate the neighbors of the accessed row
    if (debug)
      std::cout << "Refreshing only accessed rows" << std::endl;
    
    std::vector<int> addr_vec(int(T::Level::MAX), -1);
      addr_vec[0] = this->ctrl->channel->id;

    for (int i = 0 ; i < this->no_rows_per_bank ; i++)
    {
      if (accessed_row_filter[i])
      {
        // Refresh request to rank_id
        for (int j = 0 ; j < no_ranks ; j++)
        {
          for (int bg = 0 ; bg < this->no_bank_groups ; bg++)
          {
            for (int ba = 0 ; ba < this->no_banks ; ba++)
            {
              addr_vec[int(T::Level::Rank)] = j;
              addr_vec[int(T::Level::Row)] = i;
              addr_vec[int(T::Level::BankGroup)] = bg;
              addr_vec[int(T::Level::Bank)] = ba;
              this->enqueue_preventive_refresh(addr_vec);
            }
          }
        }
      }
    }
  }
};
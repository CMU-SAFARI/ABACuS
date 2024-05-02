#include "SPR.h"

namespace Ramulator
{
  template <class T>
  SPR<T>::SPR(const YAML::Node &config, Controller<T>* ctrl) : RefreshBasedDefense<T>(config, ctrl)
  {
    row_address_index_bits = config["row_address_index_bits"].as<std::vector<int>>();
    table_size = 1 << row_address_index_bits.size();
    timeout_cycles = config["timeout_cycles"].as<int>();
    probability_multiplier = config["probability_multiplier"].as<float>();
    probability_divider = config["probability_divider"].as<float>();
    // probability_lower_limit = config["probability_lower_limit"].as<float>();
    debug = config["debug"].as<bool>();
    debug_verbose = config["debug_verbose"].as<bool>();
    log_activation_period = config["log_activation_period"].as<bool>(false);
    activation_period_file_name = config["activation_period_file_name"].as<std::string>("");
    initial_probability = config["initial_probability"].as<float>(0.99895);
    nRC = ctrl->channel->spec->speed_entry[int(T::TimingCons::nRC)];
    nREFW = ctrl->channel->spec->speed_entry[int(T::TimingCons::nREFI)] * 8205; // hardcoded
    rowhammer_threshold = config["rowhammer_threshold"].as<int>(1000);
    go_back_to_zero = config["go_back_to_zero"].as<bool>(false);
    stabilize_at_para = config["stabilize_at_para"].as<bool>(false);
    para_threshold = config["para_threshold"].as<float>(0.966);
    go_back_to_zero_after_refresh = config["go_back_to_zero_after_refresh"].as<bool>(true);
    disable_probability_stats = config["disable_probability_stats"].as<bool>(false);
    probability_lower_limit = initial_probability * pow(probability_multiplier, rowhammer_threshold);

    // Get organization configuration
    this->no_rows_per_bank = ctrl->channel->spec->org_entry.count[int(T::Level::Row)];
    this->no_bank_groups = ctrl->channel->spec->org_entry.count[int(T::Level::BankGroup)];
    this->no_banks = ctrl->channel->spec->org_entry.count[int(T::Level::Bank)];
    this->no_ranks = ctrl->channel->spec->org_entry.count[int(T::Level::Rank)];

    if (debug)
    {
      std::cout << "SPR configuration:" << std::endl;
      std::cout << "  └  " << "row_address_index_bits: ";
      for (auto bit : row_address_index_bits)
        std::cout << bit << " ";
      std::cout << std::endl;
      std::cout << "  └  " << "timeout_cycles: " << timeout_cycles << std::endl;
      std::cout << "  └  " << "probability_multiplier: " << probability_multiplier << std::endl;
      std::cout << "  └  " << "probability_divider: " << probability_divider << std::endl;
      std::cout << "  └  " << "probability_lower: " << probability_lower_limit << std::endl;
      std::cout << "  └  " << "no_rows_per_bank: " << this->no_rows_per_bank << std::endl;
      std::cout << "  └  " << "no_bank_groups: " << this->no_bank_groups << std::endl;
      std::cout << "  └  " << "no_banks: " << this->no_banks << std::endl;
      std::cout << "  └  " << "no_ranks: " << this->no_ranks << std::endl;
    }

    // assert if any of the row_address_index_bits
    // is larger than log2 of no_rows_per_bank
    for (auto bit : row_address_index_bits)
      if (bit >= (int) log2(this->no_rows_per_bank))
        throw std::runtime_error("Not enough bits in the row address!");

    // Initialize the refresh probability table
    refresh_probability_table.resize(this->no_ranks * this->no_bank_groups * this->no_banks);
    for (int i = 0; i < this->no_ranks * this->no_bank_groups * this->no_banks; i++)
    {
      refresh_probability_table[i].resize(table_size);
      for (int j = 0; j < table_size; j++)
        refresh_probability_table[i][j] = {initial_probability, 0ULL, true};
    }

    // initialize random number generator
    generator = std::mt19937(1337);
    // initialize uniform distribution
    distribution = std::uniform_real_distribution<float>(0.0, 1.0);

    if (!log_activation_period && !disable_probability_stats)
    {
      sum_refresh_probability
        .init(this->no_banks * this->no_bank_groups * this->no_ranks * table_size)
        .name("sum_refresh_probability_" + std::to_string(ctrl->channel->id) + "_table")
        .desc("Sum of refresh probability values sampled every cycle per channel per table")
        .precision(6)
        ;

      avg_refresh_probability
        .init(this->no_banks * this->no_bank_groups * this->no_ranks * table_size)
        .name("avg_refresh_probability_" + std::to_string(ctrl->channel->id) + "_table")
        .desc("Average refresh probability values per channel per table")
        .precision(6)
        ;
    }

    if (log_activation_period)
    {
      std::cout << "Going to log activation period to " << activation_period_file_name << std::endl;
      act_dump_to_file = std::ofstream(activation_period_file_name, std::ios::out);
      if (!act_dump_to_file.is_open())
        throw std::runtime_error("Could not open activation_period_file_name for writing");
    }
  }

  template <class T>
  void SPR<T>::finish()
  {
    if (!log_activation_period && !disable_probability_stats)
      for (int i = 0; i < this->no_ranks * this->no_bank_groups * this->no_banks; i++)
        for (int j = 0; j < table_size; j++)
          avg_refresh_probability[i * table_size + j] = sum_refresh_probability[i * table_size + j].value()/clk;

    if (log_activation_period)
    {
      act_dump_to_file.flush();
      act_dump_to_file.close();
    }
  }

  template <class T>
  void SPR<T>::tick()
  {
    // call parent function that will push requests off to the memory controller
    this->schedule_preventive_refreshes();

    clk++;

    if (stabilize_at_para)
    {
      if ((clk % nREFW) == 0)
      {
        // reset all probability thresholds to initial_probability
        for (int i = 0; i < this->no_ranks * this->no_bank_groups * this->no_banks; i++)
          for (int j = 0; j < table_size; j++)
            refresh_probability_table[i][j].probability = initial_probability;
      }
    }
  }

  template <class T>
  void SPR<T>::update(typename T::Command cmd, const std::vector<int> &addr_vec, uint64_t open_for_nclocks, int core_id)
  {
    if (cmd != T::Command::PRE)
      return;
    
    int channel_id = addr_vec[int(T::Level::Channel)];
    int bank_group_id = addr_vec[int(T::Level::BankGroup)];
    int bank_id = addr_vec[int(T::Level::Bank)];
    int rank_id = addr_vec[int(T::Level::Rank)];
    int row_id = addr_vec[int(T::Level::Row)];

    // which refresh probability table are we accessing
    int primary_index = rank_id * this->no_banks * this->no_bank_groups + bank_group_id * this->no_banks + bank_id;
    // which entry in the probability table are we accessing
    int secondary_index = 0;
    // extract the row address index bits from the row address
    // and concatenate them
    // TODO: this sometimes starts from the end of the list (?) inverting the row address bits.
    for (auto bit : row_address_index_bits)
      secondary_index = (secondary_index << 1) | ((row_id & (1 << bit)) >> bit);    

    if (log_activation_period && !refresh_probability_table[primary_index][secondary_index].first_time)
      act_dump_to_file << channel_id << ":" << rank_id << ":" << bank_group_id << ":" << bank_id << ":" 
        << secondary_index << ":" << (clk - refresh_probability_table[primary_index][secondary_index].last_activation_timestamp) << " ";


    // update the probability table value
    bool needs_update = (refresh_probability_table[primary_index][secondary_index].last_activation_timestamp + timeout_cycles) < clk;
    if (!go_back_to_zero && !stabilize_at_para && needs_update)
    {
      int number_of_timeout_cycles = (clk - refresh_probability_table[primary_index][secondary_index].last_activation_timestamp) / timeout_cycles;
      float new_probability = refresh_probability_table[primary_index][secondary_index].probability;
      for (int i = 0; i < number_of_timeout_cycles; i++)
        new_probability *= probability_divider;
      if (new_probability > initial_probability)
        new_probability = initial_probability;
      refresh_probability_table[primary_index][secondary_index].probability = new_probability;
    }

    if (!log_activation_period && !disable_probability_stats)
      sum_refresh_probability[primary_index * table_size + secondary_index] += (1 - refresh_probability_table[primary_index][secondary_index].probability);

    // check if a refresh needs to be scheduled
    float probability_threshold = refresh_probability_table[primary_index][secondary_index].probability;

    if (debug_verbose)
    {
      std::cout << "SPR Bank" << primary_index<< " row activation: " << row_id << std::endl;
      std::cout << "  └  " << "secondary_index (from row address): " << secondary_index << std::endl;
      std::cout << "  └  " << "probability value: " << probability_threshold << std::endl;
      std::cout << "  └  " << "last activation timestamp: " << 
        refresh_probability_table[primary_index][secondary_index].last_activation_timestamp << std::endl;
      std::cout << "  └  " << "current cycle: " << clk << std::endl;
    }

    // NOTE: When the probability threshold decreases, we increase
    // the chances that victim rows get refreshed.
    // This is in contrast to implementation of PARA.
    bool issued_refresh = false;
    if (!log_activation_period)
    {
      if (distribution(generator) > probability_threshold)
      {
        this->enqueue_preventive_refresh(addr_vec);
        issued_refresh = true;
      }
    }
    uint64_t attacker_has_a_hard_time_threshold = (nREFW/rowhammer_threshold);

    float probability_increase_exp = 1;
    if (clk - refresh_probability_table[primary_index][secondary_index].last_activation_timestamp < attacker_has_a_hard_time_threshold)
      probability_increase_exp = (clk - refresh_probability_table[primary_index][secondary_index].last_activation_timestamp) / (float) nRC;
    else
      probability_increase_exp = attacker_has_a_hard_time_threshold / (float) nRC;

    if (go_back_to_zero || stabilize_at_para || refresh_probability_table[primary_index][secondary_index].first_time)
      probability_increase_exp = 1;

    // update the refresh probability table
    float new_probability = refresh_probability_table[primary_index][secondary_index].probability * pow(probability_multiplier, probability_increase_exp);
    if (go_back_to_zero)
    {
      if (new_probability < probability_lower_limit)
        new_probability = initial_probability;
    }
    else if (stabilize_at_para)
    {
      if (new_probability < probability_lower_limit)
        new_probability = para_threshold;
    }
    else
    {
      if (new_probability < probability_lower_limit)
        new_probability = probability_lower_limit;
    }

    if (go_back_to_zero_after_refresh)
      if (issued_refresh)
        new_probability = initial_probability;

    refresh_probability_table[primary_index][secondary_index].probability = new_probability;

    // update the last activation timestamp
    refresh_probability_table[primary_index][secondary_index].last_activation_timestamp = clk;

    refresh_probability_table[primary_index][secondary_index].first_time = false;
  }

}
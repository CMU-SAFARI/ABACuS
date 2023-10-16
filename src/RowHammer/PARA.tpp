#include "PARA.h"

namespace Ramulator
{
  
  template <class T>
  PARA<T>::PARA(const YAML::Node &config, Controller<T>* ctrl) : RefreshBasedDefense<T>(config, ctrl)
  {
    probability_threshold = config["probability_threshold"].as<float>();
    // check if probability threshold is valid
    if (probability_threshold < 0 || probability_threshold > 1)
      throw std::runtime_error("Invalid probability threshold for PARA defense mechanism!");

    rowpress = config["rowpress"].as<bool>();
    rowpress_increment_nticks = config["rowpress_increment_nticks"].as<int>(0);
    nRAS = ctrl->channel->spec->speed_entry[int(T::TimingCons::nRAS)];
    // initialize random number generator
    generator = std::mt19937(1337);
    // initialize uniform distribution
    distribution = std::uniform_real_distribution<float>(0.0, 1.0);

    this->no_rows_per_bank = ctrl->channel->spec->org_entry.count[int(T::Level::Row)];

    debug = config["debug"].as<bool>();
  }

  template <class T>
  void PARA<T>::tick()
  {
    this->schedule_preventive_refreshes();
  }

  template <class T>
  void PARA<T>::update(typename T::Command cmd, const std::vector<int> &addr_vec, uint64_t open_for_nclocks, int core_id)
  {
    if (cmd != T::Command::PRE)
      return;

    // increase the probability threshold by the factor
    // of time that row remains open over row cycle time
    float _probability_threshold = rowpress ? probability_threshold * (((float) open_for_nclocks + rowpress_increment_nticks - nRAS)/rowpress_increment_nticks)
                                            : probability_threshold;

    if (debug)
    {
      if (rowpress)
      {
        std::cout << "Rowpress adjusted probability threshold from " << probability_threshold << " to " << _probability_threshold 
          << "\nbecause the row was open for " << open_for_nclocks << " cycles" << std::endl;
      }
    }

    // if RNG produces a number less than probability_threshold
    // schedule a preventive refresh
    if (distribution(generator) < _probability_threshold)
    {
      this->enqueue_preventive_refresh(addr_vec);
    }
  }
};
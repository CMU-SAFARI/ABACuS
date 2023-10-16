#pragma once

#include <iostream>
#include <fstream>
#include <string>

#include "Config.h"
#include "Request.h"

namespace Ramulator
{
  template <typename T>
  class Controller;

  template <class T>
  class ActInjector {
    private:
      Controller<T>* ctrl;

      std::ifstream trace_file;
      std::vector<std::vector<int>> addr_vecs;
      std::vector<int> delays;

      uint curr_idx;
      uint next_injection_cycle = 0;

      bool _enable = false;  // Will only enable after warmup.
      bool debug = false;

    public:
      ActInjector(const YAML::Node &config, Controller<T>* ctrl);
      ~ActInjector() = default;

      void tick();
      void enable() { _enable = true; };
      void disable() { _enable = false; };
  };
};

#include "ActInjector.tpp"
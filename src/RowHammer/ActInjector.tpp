#pragma once

#include "ActInjector.h"

namespace Ramulator
{
  template <typename T>
  ActInjector<T>::ActInjector(const YAML::Node &config, Controller<T>* ctrl):
  ctrl(ctrl) {
    std::string trace_path = config["trace"].as<std::string>();
    debug = config["debug"].as<bool>();

    trace_file.open(trace_path);
    if (!trace_file.is_open()) {
      std::cout << "Failed to open Act Injection Trace File: " << trace_path << std::endl;
      abort();
    }

    // Parse the trace file
    std::string line;
    while (std::getline(trace_file, line)) {
      std::stringstream ss(line);
      std::string token;

      uint num_tokens = 0;
      while (std::getline(ss, token, ' ')) {
        num_tokens++;

        switch (num_tokens)
        {
          case 1: {
            uint delay = std::stoul(token);
            delays.push_back(delay);
            break;
          }
          
          case 2: {
            std::stringstream addr_ss(token);
            std::string addr_token;
            std::vector<int> addr_vec;
            while (std::getline(addr_ss, addr_token, ',')) {
              int addr = std::stoi(addr_token);
              addr_vec.push_back(addr);
            }
            addr_vecs.push_back(addr_vec);
            break;
          }

          default:
            break;
        }

        if (num_tokens == 2) {
          break;
        }
      }
    }

    next_injection_cycle = delays[0];

    // We disable for now, only enable after warmup.
    this->disable();
  }

  template <typename T>
  void ActInjector<T>::tick() {
    if (!_enable) {
      return;
    }

    uint curr_clk = ctrl->clk;

    if (curr_clk >= next_injection_cycle) {
      // Inject an ACT
      Request req(addr_vecs[curr_idx], Request::Type::READ, nullptr);
      bool res = ctrl->enqueue(req);

      if (res) {
        if (debug) {
          std::cout << "Injected ACT ";
          for (const auto& i : addr_vecs[curr_idx]) {
            std::cout << i << ", ";
          }
          std::cout << " @ " << curr_clk << " cycles" << std::endl;
        }

        curr_idx = (curr_idx + 1) % addr_vecs.size();
        next_injection_cycle = curr_clk + delays[curr_idx];

      } else {
        if (debug) {
          std::cout << "ACT Injection ";
          for (const auto& i : addr_vecs[curr_idx]) {
            std::cout << i << ", ";
          }
          std::cout << " delayed @ " << curr_clk << " cycles" << std::endl;
        }
      }
    }
  }
};
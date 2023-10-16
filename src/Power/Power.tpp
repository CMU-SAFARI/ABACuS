#include "Power.h"

#include "DDR4.h"
#include "DDR5.h"

#include <spdlog/spdlog.h>

#define TS(timing)  (dram_node->spec->speed_entry[int(T::TimingCons::timing)])
#define VE(voltage) (dram_node->spec->voltage_entry[int(T::Voltage::voltage)])
#define CE(current) (dram_node->spec->current_entry[int(T::Current::current)])

namespace Ramulator
{
  class DDR4;
  class DDR5;

  template <class T>
  Power<T>::Power() {};

  template <class T>
  Power<T>::Power(const DRAM<T>* dram_node, typename T::Level level):
  dram_node(dram_node), level(level)
  {

  };

  template <class T>
  void Power<T>::handle_ACT_rank(bool is_rank_idle, int64_t clk, int act_multiplier)
  {
    counters.num_act += act_multiplier;
    if (is_rank_idle)
    {
      counters.first_act_cycle = clk;
      counters.pre_cycles += (clk - counters.last_pre_cycle);

      if (counters.latest_pre_cmd_cycle > 0)
        counters.pre_idle_cycles += std::max((clk - counters.latest_pre_cmd_cycle - TS(nRP)), (int64_t) 0);
      else
        counters.pre_idle_cycles += clk;
    }
    counters.latest_act_cmd_cycle = clk;
  };

  template <class T>
  void Power<T>::handle_ACT_bank(int64_t clk, int act_multiplier)
  {
    counters.num_act+= act_multiplier;
  };

  template <class T>
  void Power<T>::handle_PRE_rank(bool is_rank_idle, int64_t clk, int pre_multiplier)
  {
    counters.num_pre += pre_multiplier;
    if (is_rank_idle)
    {
      counters.last_pre_cycle = clk;
      counters.act_cycles += (clk - counters.first_act_cycle);
      update_act_idle_cycles(clk);
    }
    counters.latest_pre_cmd_cycle = clk;
  };

  template <class T>
  void Power<T>::handle_PRE_bank(int64_t clk, int pre_multiplier)
  {
    counters.num_pre += pre_multiplier;
    counters.act_cycles += (clk - counters.first_act_cycle);
  };

  template <class T>
  void Power<T>::handle_RD_rank(int64_t clk)
  {
    counters.num_rd++;
    update_act_idle_cycles(clk);
    counters.latest_read_cmd_cycle = clk;
  };

  template <class T>
  void Power<T>::handle_WR_rank(int64_t clk)
  {
    counters.num_wr++;
    update_act_idle_cycles(clk);
    counters.latest_write_cmd_cycle = clk;
  };

  template <class T>
  void Power<T>::handle_REF_rank(int64_t clk)
  {
    counters.num_ref++;

    counters.first_act_cycle = clk;

    counters.pre_idle_cycles += std::max((clk - counters.latest_pre_cmd_cycle - TS(nRP)), (int64_t) 0);
    counters.pre_cycles += (clk - counters.last_pre_cycle);
    counters.last_pre_cycle = clk + TS(nRFC) - TS(nRP);
    counters.latest_pre_cmd_cycle = counters.last_pre_cycle;
  };

  template <class T>
  void Power<T>::handle_REF_bank(int64_t clk)
  {
    counters.num_ref++;
    counters.first_act_cycle = clk;
    counters.act_cycles += TS(nRFC) - TS(nRP);
  };


  template <class T>
  void Power<T>::epilogue_rank(bool is_rank_idle,int64_t clk)
  {
    if (is_rank_idle)
    {
      counters.pre_cycles += (clk - counters.last_pre_cycle);
      counters.pre_idle_cycles += std::max((int64_t)0, (clk - counters.latest_pre_cmd_cycle - TS(nRP)));
    }
    else
    {
      counters.act_cycles += (clk - counters.first_act_cycle);
      update_act_idle_cycles(clk);
    }
  };

  template <class T>
  void Power<T>::epilogue_bank(int64_t clk)
  {
    if (dram_node->state == T::State::Opened)
      counters.act_cycles += clk - counters.first_act_cycle;
  };

  template <class T>
  void Power<T>::update_act_idle_cycles(int64_t clk)
  {
    int64_t end_read_op = counters.latest_read_cmd_cycle + TS(nCL) + TS(nBL) - 1;
    int64_t end_write_op = counters.latest_write_cmd_cycle + TS(nCWL) + TS(nBL) + TS(nWR) - 1;
    int64_t end_act_op = counters.latest_act_cmd_cycle + TS(nRCD) - 1;

    int64_t delta = std::max(std::max(end_read_op, end_write_op), end_act_op);

    if (clk > delta)
      counters.act_idle_cycles += (clk - delta);
  };

  template <class T>
  double Power<T>::calculate_energy()
  {
    // Ugly fix to bypass template specialization order bs
    if constexpr (std::is_same_v<T, DDR4>) {
      PowerCounters&   ctrs = counters;
      PowerComponents& c = components;

      double tCK_ns = (double) TS(tCK_ps) / 1000.0;

      c.ACT_stdby_energy = (VE(VDD) * CE(IDD3N) + VE(VPP) * CE(IPP3N)) * ctrs.act_cycles * tCK_ns / 1E3;
      c.PRE_stdby_energy = (VE(VDD) * CE(IDD2N) + VE(VPP) * CE(IPP2N)) * ctrs.pre_cycles * tCK_ns / 1E3;

      c.ACT_idle_energy = (VE(VDD) * CE(IDD3N) + VE(VPP) * CE(IPP3N)) * ctrs.act_idle_cycles * tCK_ns / 1E3;
      c.PRE_idle_energy = (VE(VDD) * CE(IDD2N) + VE(VPP) * CE(IPP2N)) * ctrs.pre_idle_cycles * tCK_ns / 1E3;

      c.total_idle_energy = c.ACT_idle_energy + c.PRE_idle_energy;

      c.ACT_cmd_energy  = (VE(VDD) * (CE(IDD0) - CE(IDD3N)) + VE(VPP) * (CE(IPP0) - CE(IPP3N))) * ctrs.num_act * TS(nRAS) * tCK_ns / 1E3;
      c.PRE_cmd_energy  = (VE(VDD) * (CE(IDD0) - CE(IDD2N)) + VE(VPP) * (CE(IPP0) - CE(IPP2N))) * ctrs.num_pre * TS(nRP)  * tCK_ns / 1E3;
      c.RD_cmd_energy   = (VE(VDD) * CE(IDD4R) + VE(VPP) * CE(IPP4R)) * ctrs.num_rd * TS(nBL) * tCK_ns / 1E3;
      c.WR_cmd_energy   = (VE(VDD) * CE(IDD4W) + VE(VPP) * CE(IPP4W)) * ctrs.num_wr * TS(nBL) * tCK_ns / 1E3;
      c.REF_cmd_energy  = (VE(VDD) * (CE(IDD5B) - CE(IDD3N)) + VE(VPP) * (CE(IPP5B) - CE(IPP3N))) * ctrs.num_ref * TS(nRFC) * tCK_ns / 1E3;

      return c.ACT_stdby_energy + c.PRE_stdby_energy + c.ACT_idle_energy + c.PRE_idle_energy + c.ACT_cmd_energy + c.PRE_cmd_energy + c.RD_cmd_energy + c.WR_cmd_energy + c.REF_cmd_energy;

    } else if constexpr (std::is_same_v<T, DDR5>) {
      PowerCounters&   ctrs = counters;
      PowerComponents& c = components;

      double tCK_ns = (double) TS(tCK_ps) / 1000.0;

      c.ACT_stdby_energy = (VE(VDD) * CE(IDD3N) + VE(VPP) * CE(IPP3N)) * ctrs.act_cycles * tCK_ns / 1E3;
      c.PRE_stdby_energy = (VE(VDD) * CE(IDD2N) + VE(VPP) * CE(IPP2N)) * ctrs.pre_cycles * tCK_ns / 1E3;

      c.ACT_idle_energy = (VE(VDD) * CE(IDD3N) + VE(VPP) * CE(IPP3N)) * ctrs.act_idle_cycles * tCK_ns / 1E3;
      c.PRE_idle_energy = (VE(VDD) * CE(IDD2N) + VE(VPP) * CE(IPP2N)) * ctrs.pre_idle_cycles * tCK_ns / 1E3;

      c.total_idle_energy = c.ACT_idle_energy + c.PRE_idle_energy;

      c.ACT_cmd_energy  = (VE(VDD) * (CE(IDD0) - CE(IDD3N)) + VE(VPP) * (CE(IPP0) - CE(IPP3N))) * ctrs.num_act * TS(nRAS) * tCK_ns / 1E3;
      c.PRE_cmd_energy  = (VE(VDD) * (CE(IDD0) - CE(IDD2N)) + VE(VPP) * (CE(IPP0) - CE(IPP2N))) * ctrs.num_pre * TS(nRP)  * tCK_ns / 1E3;
      c.RD_cmd_energy   = (VE(VDD) * CE(IDD4R) + VE(VPP) * CE(IPP4R)) * ctrs.num_rd * TS(nBL) * tCK_ns / 1E3;
      c.WR_cmd_energy   = (VE(VDD) * CE(IDD4W) + VE(VPP) * CE(IPP4W)) * ctrs.num_wr * TS(nBL) * tCK_ns / 1E3;
      c.REF_cmd_energy  = (VE(VDD) * (CE(IDD5B) - CE(IDD3N)) + VE(VPP) * (CE(IPP5B) - CE(IPP3N))) * ctrs.num_ref * TS(nRFC) * tCK_ns / 1E3;

      return c.ACT_stdby_energy + c.PRE_stdby_energy + c.ACT_idle_energy + c.PRE_idle_energy + c.ACT_cmd_energy + c.PRE_cmd_energy + c.RD_cmd_energy + c.WR_cmd_energy + c.REF_cmd_energy;

    }
    else {
      throw std::logic_error("Power model not implemented!");
    }
  };

  template <class T>
  void Power<T>::print_energy()
  {
    PowerCounters& ctrs = counters;

    std::cout << fmt::format("ACT:") << std::endl;
    std::cout << fmt::format("  Cycles:        {}", ctrs.act_cycles)  << std::endl;
    std::cout << fmt::format("  Idle Cycles:   {}", ctrs.act_idle_cycles)   << std::endl;
    std::cout << fmt::format("  # of ACTs:     {}", ctrs.num_act)    << std::endl;

    std::cout << fmt::format("PRE:") << std::endl;
    std::cout << fmt::format("  Cycles:        {}", ctrs.pre_cycles)  << std::endl;
    std::cout << fmt::format("  Idle Cycles:   {}", ctrs.pre_idle_cycles)   << std::endl;
    std::cout << fmt::format("  # of PREs:     {}", ctrs.num_pre)    << std::endl;

    std::cout << fmt::format("# of RDs:   {}", ctrs.num_rd)  << std::endl;
    std::cout << fmt::format("# of WRs:   {}", ctrs.num_wr)  << std::endl;
    std::cout << fmt::format("# of REFs:  {}", ctrs.num_ref) << std::endl;


    PowerComponents& c = components;

    std::cout << fmt::format("ACT energy:") << std::endl;
    std::cout << fmt::format("  Standy energy: {} nJ", c.ACT_stdby_energy)  << std::endl;
    std::cout << fmt::format("  Idle energy:   {} nJ", c.ACT_idle_energy)   << std::endl;
    std::cout << fmt::format("  CMD energy:    {} nJ", c.ACT_cmd_energy)    << std::endl;

    std::cout << fmt::format("PRE energy:") << std::endl;
    std::cout << fmt::format("  Standy energy: {} nJ", c.PRE_stdby_energy)  << std::endl;
    std::cout << fmt::format("  Idle energy:   {} nJ", c.PRE_idle_energy)   << std::endl;
    std::cout << fmt::format("  CMD energy:    {} nJ", c.PRE_cmd_energy)    << std::endl;

    std::cout << fmt::format("Total Idle energy: {} nJ", c.total_idle_energy) << std::endl;

    std::cout << fmt::format("RD CMD energy:  {} nJ", c.RD_cmd_energy)  << std::endl;
    std::cout << fmt::format("WR CMD energy:  {} nJ", c.WR_cmd_energy)  << std::endl;
    std::cout << fmt::format("REF CMD energy: {} nJ", c.REF_cmd_energy) << std::endl;
  };

  #undef TS
  #undef VE
  #undef CE
};
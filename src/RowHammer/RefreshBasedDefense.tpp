#include "RefreshBasedDefense.h"
#include "PARA.h"
#include "Graphene.h"
#include "SPR.h"
#include "Hydra.h"
#include "ABACUS.h"

namespace Ramulator{  
  template <class T>
  RefreshBasedDefense<T>* make_refresh_based_defense(YAML::Node config, Controller<T>* ctrl)
  {
    if (!config["refresh_based_defense"])
        return nullptr;

    YAML::Node rbd_config = config["refresh_based_defense"];
    rbd_config["num_cores"] = config["num_cores"].as<int>();
    std::string rbd_type = rbd_config["type"].as<std::string>("PARA");

    RefreshBasedDefense<T>* rbd = nullptr;

    if (rbd_type == "PARA")
      rbd = new PARA<T>(rbd_config, ctrl);
    else if (rbd_type == "Graphene")
      rbd = new Graphene<T>(rbd_config, ctrl);
    else if (rbd_type == "SPR")
      rbd = new SPR<T>(rbd_config, ctrl);
    else if (rbd_type == "Hydra")
      rbd = new Hydra<T>(rbd_config, ctrl);
    else if (rbd_type == "ABACUS")
      rbd = new ABACUS<T>(rbd_config, ctrl);
    else
      throw std::runtime_error(fmt::format("Unrecognized refresh based defense type: {}", rbd_type));

    std::cout << fmt::format("Refresh based defense: {}", rbd->to_string()) << std::endl;
    return rbd;
  }

  template <class T>
  void RefreshBasedDefense<T>::enqueue_preventive_refresh(const std::vector<int>& addr_vec)
  {
    // create two new preventive refreshes targeting addr_vec
    std::vector<int> m1_addr_vec = addr_vec;
    std::vector<int> m2_addr_vec = addr_vec;
    m1_addr_vec[int(T::Level::Row)] = (m1_addr_vec[int(T::Level::Row)] + 1) % no_rows_per_bank;
    m2_addr_vec[int(T::Level::Row)] = (m2_addr_vec[int(T::Level::Row)] - 1) % no_rows_per_bank;

    if (debug_base)
    {
      std::cout << "Scheduling preventive refreshes for row " << addr_vec[int(T::Level::Row)] << std::endl;
      std::cout << "  └  " << "m1: " << m1_addr_vec[int(T::Level::Row)] << std::endl;
      std::cout << "  └  " << "m2: " << m2_addr_vec[int(T::Level::Row)] << std::endl;
    }

    Request m1(m1_addr_vec, Request::Type::PREVENTIVE_REFRESH, nullptr);
    Request m2(m2_addr_vec, Request::Type::PREVENTIVE_REFRESH, nullptr);
    
    // push to queue
    if (addr_vec[int(T::Level::Row)] != (no_rows_per_bank - 1))
      pending_refresh_queue.push(m1);
    if (addr_vec[int(T::Level::Row)] != 0)
      pending_refresh_queue.push(m2);

    // TODO: Very hacky, I am writing this at 03:49 am
    // if blast radius is two
    if (blast_radius == 2) {
      // create two new preventive refreshes targeting addr_vec
      std::vector<int> m3_addr_vec = addr_vec;
      std::vector<int> m4_addr_vec = addr_vec;
      m3_addr_vec[int(T::Level::Row)] = (m3_addr_vec[int(T::Level::Row)] + 2) % no_rows_per_bank;
      m4_addr_vec[int(T::Level::Row)] = (m4_addr_vec[int(T::Level::Row)] - 2) % no_rows_per_bank;
  
      Request m3(m3_addr_vec, Request::Type::PREVENTIVE_REFRESH, nullptr);
      Request m4(m4_addr_vec, Request::Type::PREVENTIVE_REFRESH, nullptr);

      // push to queue
      if (!(addr_vec[int(T::Level::Row)] >= (no_rows_per_bank - 2)))
        pending_refresh_queue.push(m3);
      if (!(addr_vec[int(T::Level::Row)] <= 1))
        pending_refresh_queue.push(m4);
    }
  }

  template <class T>
  void RefreshBasedDefense<T>::schedule_preventive_refreshes()
  {
    if (pending_refresh_queue.empty())
      return;

    // traverse queue entries
    while (!pending_refresh_queue.empty())
    {
      Request req = pending_refresh_queue.front();
      // check if the request is still valid
      if (ctrl->enqueue(req))
        // if scheduled, remove it
        pending_refresh_queue.pop();
      else
        break;
    }
  }
};
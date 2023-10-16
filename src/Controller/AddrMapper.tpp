#pragma once

#include "AddrMapper.h"

namespace Ramulator
{
  template <typename T>
  AddrMapperBase<T>* make_addr_mapper(const YAML::Node& config, Controller<T>* ctrl)
  {
    if (! config["addr_mapper"])
      throw std::runtime_error("Address Mapper configuration (addr_mapper:) not found!");

    const YAML::Node& addr_mapper_config = config["addr_mapper"];
    std::string addr_mapper_type = addr_mapper_config["type"].as<std::string>("");

    AddrMapperBase<T>* addr_mapper = nullptr;

    if      (addr_mapper_type == "Linear")
      addr_mapper = new LinearMapper<T>(addr_mapper_config, ctrl);
    else
      throw std::runtime_error(fmt::format("Unrecognized Address Mapper type: {}", addr_mapper_type));

    std::cout << fmt::format("Address Mapper: {}", addr_mapper->to_string()) << std::endl;
    return addr_mapper;
  }

  template <typename T>
  AddrMapperBase<T>::AddrMapperBase(const YAML::Node& config, Controller<T>* ctrl):
  ctrl(ctrl)
  {
    int *sz = ctrl->channel->spec->org_entry.count;
    this->addr_bits.resize(int(T::Level::MAX));
    for (unsigned int lev = 0; lev < this->addr_bits.size(); lev++)
      this->addr_bits[lev] = calc_log2(sz[lev]);

    // This is very wrong? TODO: it might have broken other mappings
    //this->addr_bits[int(T::Level::MAX) - 1] -= calc_log2(ctrl->channel->spec->prefetch_size);
  };

  template <typename T>
  void LinearMapper<T>::apply(uint64_t addr, Request& req)
  {
    req.addr_vec.resize(this->addr_bits.size());

    switch (type)
    {
      case Type::ChRaBaRoCo:
        for (int i = this->addr_bits.size() - 1; i >= 0; i--)
          req.addr_vec[i] = slice_lower_bits(addr, this->addr_bits[i]);
        break;
      case Type::RoBaRaCoCh:
        req.addr_vec[0] = slice_lower_bits(addr, this->addr_bits[0]);
        req.addr_vec[this->addr_bits.size() - 1] = slice_lower_bits(addr, this->addr_bits[this->addr_bits.size() - 1]);
        for (int i = 1; i <= int(T::Level::Row); i++)
          req.addr_vec[i] = slice_lower_bits(addr, this->addr_bits[i]);
        break;
      case Type::MOP4CLXOR:
      {
        // std::cout << "whole address: " << std::hex << addr << std::dec << std::endl;

        //splitting bits into addresses of individual levels 
        slice_lower_bits(addr, 3); // just slice them, these are retrieved in a single burst
        req.addr_vec[int(T::Level::Column)] = slice_lower_bits(addr, 3); // MOP4CL
        for (int lvl = 0 ; lvl < int(T::Level::Row) ; lvl++)
            req.addr_vec[lvl] = slice_lower_bits(addr, this->addr_bits[lvl]);
        req.addr_vec[int(T::Level::Column)] += slice_lower_bits(addr, this->addr_bits[int(T::Level::Column)]-3) << 3;
        req.addr_vec[int(T::Level::Row)] = (int) addr;

        // print row address
        // std::cout << "row address: " << req.addr_vec[int(T::Level::Row)] << std::endl;

        int row_xor_index = 0; 
        for (int lvl = 0 ; lvl < int(T::Level::Row) ; lvl++){
          if (this->addr_bits[lvl] > 0){
            int mask = (req.addr_vec[int(T::Level::Row)] >> row_xor_index) & ((1<<this->addr_bits[lvl])-1);
            req.addr_vec[lvl] = req.addr_vec[lvl] xor mask;
            row_xor_index += this->addr_bits[lvl];
          }
        }
        // std::cout << "row address: " << req.addr_vec[int(T::Level::Row)] << std::endl;

        break;
      }
      default:
        assert(false && "Unknown address mapping!");
    };
  }

  template <typename T>
  void LinearMapper<T>::apply(uint64_t addr, std::vector<int> &addr_vec)
  {
    addr_vec.resize(this->addr_bits.size());

    switch (type)
    {
      case Type::ChRaBaRoCo:
        for (int i = this->addr_bits.size() - 1; i >= 0; i--)
          addr_vec[i] = slice_lower_bits(addr, this->addr_bits[i]);
        break;
      case Type::RoBaRaCoCh:
        addr_vec[0] = slice_lower_bits(addr, this->addr_bits[0]);
        addr_vec[this->addr_bits.size() - 1] = slice_lower_bits(addr, this->addr_bits[this->addr_bits.size() - 1]);
        for (int i = 1; i <= int(T::Level::Row); i++)
          addr_vec[i] = slice_lower_bits(addr, this->addr_bits[i]);
        break;
      case Type::MOP4CLXOR:
      {
        //splitting bits into addresses of individual levels 
        slice_lower_bits(addr, 3); // just slice them, these are retrieved in a single burst
        addr_vec[int(T::Level::Column)] = slice_lower_bits(addr, 3); // MOP4CL
        for (int lvl = 0 ; lvl < int(T::Level::Row) ; lvl++)
            addr_vec[lvl] = slice_lower_bits(addr, this->addr_bits[lvl]);
        addr_vec[int(T::Level::Column)] += slice_lower_bits(addr, this->addr_bits[int(T::Level::Column)]-3) << 3;
        addr_vec[int(T::Level::Row)] = (int) addr;

        int row_xor_index = 0; 
        for (int lvl = 0 ; lvl < int(T::Level::Row) ; lvl++){
          if (this->addr_bits[lvl] > 0){
            int mask = (addr_vec[int(T::Level::Row)] >> row_xor_index) & ((1<<this->addr_bits[lvl])-1);
            addr_vec[lvl] = addr_vec[lvl] xor mask;
            row_xor_index += this->addr_bits[lvl];
          }
        }
        break;
      }
      default:
        assert(false && "Unknown address mapping!");
    };
  }
}
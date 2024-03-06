# ABACuS: **A**ll-**B**ank **A**ctivation **C**o**u**nters for **S**calable and Low Overhead RowHammer Mitigation

ABACuS is a new RowHammer mitigation mechanism that prevents RowHammer bitflips at low area, performance, and energy overheads for modern and future DRAM chips that are very vulnerable to RowHammer (e.g., with hammer counts as low as 125 inducing bitflips).

<p align="center">
      <img src="abacus.jpg" style="width:500px;height:500px;"><br>
      <em>DALL-E's picture of ABACuS</em>
</p>

## Cite ABACuS

Please cite the following paper if you find ABACuS useful:

A. Olgun, Y. C. Tugrul, N. Bostanci, I. E. Yuksel, H. Luo, S. Rhyner, A. G. Yaglikci, G. F. Oliveira, O. Mutlu, "ABACuS: All-Bank Activation Counters for Scalable and Low Overhead RowHammer Mitigation", To appear in USENIX Security 2024, August 2024.

Link to the PDF: [https://arxiv.org/pdf/2310.09977.pdf](https://arxiv.org/pdf/2310.09977.pdf)

BibTeX format for your convenience:
```
@inproceedings{olgun2024abacus,
      title={{ABACuS: All-Bank Activation Counters for Scalable and Low Overhead RowHammer Mitigation}}, 
      author={Olgun, Ataberk and Tugrul, Yahya Can and Bostanci, Nisa and Yuksel, Ismail Emir and Luo, Haocong and Rhyner, Steve and Yaglikci, A. Giray and Oliveira, Geraldo F. and Mutlu, Onur},
      year={2024},
      booktitle={USENIX Security}
}
```

## Repository File Structure 

```
.
+-- abacus_cacti/                   # Area, power, and energy analyses sources
+-- abacus_verilog/                 # Verilog HDL sources for ABACuS hardware design
+-- configs/ABACuS/                 # Ramulator configurations for ABACuS and other state-of-the-art mechanisms
|   +-- AttackPresent/              # Configurations used in simulating adversarial workloads
|   +-- Others/                     # Configurations for four state-of-the-art mechanisms
|   +-- ABACUS/                     # Configurations for ABACuS
|   +-- Revision/                   # Configurations for ABACuS-Big (see Section 9.4 in our paper)           
+-- cputraces/                      # CPU traces for 62 single-core workloads
+-- ext/                            # External dependencies
+-- scripts/                        # Scripts to post process raw data and create the plots in our paper
+-- src/                            # Ramulator source code
|   +-- RowHammer/                  # Source code of ABACUS and four other state-of-the-art mitigation mechanisms
|   ...
...
+-- README.md                       # This file
```
## Installation Guide:

### Prerequisites:
- Podman
  - We have tested Podman 3.4.4 on Ubuntu 22.04.1
- Git 

### Installation steps:

1. Clone the repository `git clone -b usenix24-ae git@github.com:CMU-SAFARI/ABACuS.git` 

## Example Use

### If you do not have slurm

1. Run ramulator simulations `./run_artifact_with_podman.sh --personalcomputer`
2. Run the figure creator script `./create_figures_with_podman.sh` 

### If you already have slurm

1. Run ramulator simulations `./run_artifact_with_podman.sh --slurm`
2. Navigate to `scripts/` and run the figure creator script `python3 create_figures.py` 

## Reproducing area, power, and energy results

We model ABACuS, Graphene, and Hydra's area, power, and energy cost using CACTI. These results are reproduced by running `./area_results_with_podman.sh`.

## Verilog HDL Implementation

We implement ABACuS's hardware design in Verilog to faithfully measure its circuit latency. The Verilog implementation is under `abacus_verilog/`. You may use the `abacus_verilog/dc.tcl` script to launch Synopsys (synthesis) analysis runs.

## Contacts:
Ataberk Olgun (ataberk.olgun [at] safari [dot] ethz [dot] ch)  
Nisa Bostanci (nisa.bostanci [at] safari [dot] ethz [dot] ch)  

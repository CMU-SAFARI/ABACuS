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
+-- act_injection_traces/           # Traces for the adversarial workloads (see Section 9.3 in our paper)
+-- configs/ABACuS/                 # Ramulator configurations for ABACuS and other state-of-the-art mechanisms
|   +-- AttackPresent/              # Configurations used in simulating adversarial workloads
|   +-- Others/                     # Configurations for four state-of-the-art mechanisms
|   +-- ABACUS/                     # Configurations for ABACuS
|   +-- Revision/                   # Configurations for ABACuS-Big (see Section 9.4 in our paper)           
+-- cputraces/                      # CPU traces for 62 single-core workloads
+-- ext/                            # External dependencies
+-- results/                        # All raw data for the results shown in our paper
+-- scripts/                        # Scripts to post process raw data and create the plots in our paper
+-- src/                            # Ramulator source code
|   +-- RowHammer/                  # Source code of ABACUS and four other state-of-the-art mitigation mechanisms
|   ...
...
+-- README.md                       # This file
```
## Installation Guide:

### Prerequisites:
- G++ version above 8.4
- Python with pandas, seaborn, and ipython
- \[Optional\] Slurm 

### Installation steps:
- Simply run `./build.sh` to compile Ramulator
- Download the traces `abacus_cputraces.tar.bz2` (3.36 GiB) from this [Google Drive link](https://drive.google.com/file/d/1TY5oULe9tBKbcpqmjzTdyWM75NrY-0fP/view?usp=sharing)
- Extract the traces so that they reside under `cputraces/`
- \[Optional\] Download the results `abacus_results.tar.bz2` (496 MiB) from this [Google Drive link](https://drive.google.com/file/d/16fzK-1Z8gabdCZ1oibe8Q8effy8wZsoP/view?usp=sharing) and extract it to `results/`
- \[Optional\] Extract the zipped file `act_injection_traces.tar.bz2`

## Example Use

Skip to section "Reproducing Plots" in the README if you want to produce the plots in the paper from the data we provide. 

### If you do not have slurm

We provide all configurations we use in the paper under `configs/ABACUS`. Simply instruct Ramulator to use one of the configuration files. See `configs/ABACUS/ABACUS1000.yaml` for annotated key configuration parameters. To instruct Ramulator to use this config file, run the following:

`./ramulator -c configs/ABACUS/ABACUS1000.yaml`

The simulation is configured to execute a single-core system running the 429.mcf CPU trace with ABACuS tuned to mitigate RowHammer bitflips at a RowHammer threshold of 1000.

### If you already have slurm

Adapt `slurm.py` (and `slurm_adversarial.py`) to your working environment. We are working on providing a methodical approach to recreating all Slurm batch scripts, and `slurm.py` must be manually modified for now. To do so, modify the absolute paths in the script (e.g., lines 26, 31-66, 212-214) to reflect valid directory paths in your system.

Executing (modified) `slurm.py` and `slurmn_adversarial.py` will generate a `run.sh` file that you can use to schedule all slurm jobs (i.e., Ramulator simulations) required to produce all data that can be used in the next step to generate all plots in the paper.

## Reproducing plots

Use the `scripts/all_results.ipynb` file to reproduce the figures that show all our results in the paper (Figures 2, 3, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, and 18).

## Reproducing area, power, and energy results

We model ABACuS, Graphene, and Hydra's area, power, and energy cost using CACTI. Follow the three steps to reproduce our results (i.e., generate the values displayed in Table 1 in our paper).

1. Navigate to `abacus_cacti/`
2. Run `make opt` to compile CACTI (check `abacus_cacti/README` for detailed instructions on installing CACTI)
3. Run the Python code blocks in `abacus_cacti/results.ipynb` to get area, power, and energy numbers for ABACuS, Graphene, and Hydra

## Verilog HDL Implementation

We implement ABACuS's hardware design in Verilog to faithfully measure its circuit latency. The Verilog implementation is under `abacus_verilog/`. You may use the `abacus_verilog/dc.tcl` script to launch Synopsys (synthesis) analysis runs.

## Coming soon to our repository

* ABACuS hardware design (Verilog description)
* Methodical approach to launching Slurm runs
* Push-button script to replicate all results in the paper

## Contacts:
Ataberk Olgun (ataberk.olgun [at] safari [dot] ethz [dot] ch)  
Nisa Bostanci (nisa.bostanci [at] safari [dot] ethz [dot] ch)  

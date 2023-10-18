 ------------------------------------------------------------------------------
# <<Add description>>
# ------------------------------------------------------------------------------
remove_design -design
sh rm -rf WORK/*
set target_library [list /usr/pack/umc-65-kgf/umc/ll/uk65lscllmvbbl/a02/synopsys/uk65lscllmvbbl_120c25_tc.db]
set link_library [list /usr/pack/umc-65-kgf/umc/ll/uk65lscllmvbbl/a02/synopsys/uk65lscllmvbbl_120c25_tc.db]
set search_path [list /home/kanellok/sac_rowhammer/]
set_host_options -max_cores 16
# ------------------------------------------------------------------------------
# Analyze Design
# ------------------------------------------------------------------------------
# <<Insert analyze command here>>
analyze -format verilog -library WORK {parameters.vh \
    sac_top.v \
    address_cam.v \
    count_cam.v \
    control_logic.v \
}
# ------------------------------------------------------------------------------
# Elaborate Design
# ------------------------------------------------------------------------------
# <<Insert elaborate command here>>
elaborate sac_top -architecture verilog -library WORK -update
# ------------------------------------------------------------------------------
# Define Constraints
# ------------------------------------------------------------------------------
# <<Insert definition of constraints here>>

create_clock clk_i -period 2.0
# Compile Design
# ------------------------------------------------------------------------------
# <<Insert compile command here>>
compile_ultra
# ------------------------------------------------------------------------------
# Generate Reports
# ------------------------------------------------------------------------------
report_timing > reports/sac_rowhammer_reports/sac_rowhammer_timing.rpt
report_timing -path full -delay max -max_paths 5 -nworst 2 > reports/sac_rowhammer_reports/report.full_paths
report_area -hierarchy > reports/sac_rowhammer_reports/sac_rowhammer_area.rpt
report_area > reports/sac_rowhammer_reports/report.area
report_register -nosplit > reports/sac_rowhammer_reports/sac_rowhammer_registers.rpt
report_power -hierarchy > reports/sac_rowhammer_reports/sac_rowhammer_power.rpt
# ------------------------------------------------------------------------------
# Write Out Data
# ------------------------------------------------------------------------------
# Change names for Verilog.
change_names -rule verilog -hierarchy

# Write Verilog netlist.
write -hierarchy -format verilog -output netlists/sac.v
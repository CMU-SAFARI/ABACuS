
`include "parameters.vh"

module abacus
(
    input                                   clk_i,
    input                                   rst_i,
    input                                   is_ACT_i,
    input [`ROW_ADDR_BIT - 1 : 0]           row_addr_i,
    input [$clog2(`BANK_BITS) - 1 : 0]      bank_id_i,
    output                                  issue_preventive_refresh_o,
    output [`ROW_ADDR_BIT - 1 : 0]          victim_row_addr_low_o,
    output [`ROW_ADDR_BIT - 1 : 0]          victim_row_addr_high_o
);

wire [$clog2(`N_ENTRY) - 1 : 0]  cl_ac_write_addr_idx_w;
wire [`ROW_ADDR_BIT - 1 : 0]  cl_ac_search_addr_idx_w;
wire cl_ac_search_w;
wire cl_ac_write_w;
wire [$clog2(`N_ENTRY)-1:0]      ac_cl_count_idx_w;
wire ac_cl_is_hit_w;
wire ac_cl_valid_w;


address_cam ac
(
    .clk_i(clk_i),
    .rst_i(rst_i),
    .row_addr_i(cl_ac_search_addr_idx_w),
    .write_idx_i(cl_ac_write_addr_idx_w),
    .search_i(cl_ac_search_w),
    .write_i(cl_ac_write_w),
    .count_idx_o(ac_cl_count_idx_w),
    .is_hit_o(ac_cl_is_hit_w),
    .valid_o(ac_cl_valid_w)
);
wire [`SP_CNT_BIT - 1 : 0] cl_cc_sp_cnt_w;
wire [$clog2(`N_ENTRY) - 1 : 0]  cl_cc_inc_idx_w;
wire cl_cc_search_w;
wire cl_cc_write_w;
wire [$clog2(`N_ENTRY) - 1 : 0]  cc_cl_adress_idx_w;
wire cc_cl_is_hit_w;
wire cc_cl_valid_w;
wire [$clog2(`BANK_BITS) - 1 : 0] cl_cc_bank_id_w;
count_cam cc
(
    .clk_i(clk_i),
    .rst_i(rst_i),
    .sp_cnt_i(cl_cc_sp_cnt_w),
    .inc_idx_i(cl_cc_inc_idx_w),
    .bank_id_i(cl_cc_bank_id_w),
    .search_i(cl_cc_search_w),
    .write_i(cl_cc_write_w),
    .address_idx_o(cc_cl_adress_idx_w),
    .is_hit_o(cc_cl_is_hit_w),
    .valid_o(cc_cl_valid_w) 
);
control_logic cl
(
    .clk_i(clk_i),
    .rst_i(rst_i),
    .is_ACT_i(is_ACT_i),
    .row_addr_i(row_addr_i),
    .bank_id_i(bank_id_i),
    .is_hit_addr_cam_i(ac_cl_is_hit_w),
    .addr_cam_out_valid_i(ac_cl_valid_w),
    .is_hit_count_cam_i(cc_cl_is_hit_w),
    .count_cam_out_valid_i(cc_cl_valid_w),
    .write_addr_cam_idx_i(cc_cl_adress_idx_w),
    .write_count_cam_idx_i(ac_cl_count_idx_w),
    .search_addr_cam_idx_o(cl_ac_search_addr_idx_w),
    .write_addr_cam_idx_o(cl_ac_write_addr_idx_w),
    .search_count_cam_idx_o(cl_cc_sp_cnt_w),
    .write_count_cam_idx_o(cl_cc_inc_idx_w),
    .search_addr_cam_o(cl_ac_search_w),
    .search_count_cam_o(cl_cc_search_w),
    .write_count_cam_o(cl_cc_write_w),
    .bank_id_o(cl_cc_bank_id_w)
);


endmodule
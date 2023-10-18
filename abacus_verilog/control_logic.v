`include "parameters.vh"
module control_logic
(
    input                                           clk_i,
    input                                           rst_i,
    input                                           is_ACT_i,
    input       [`ROW_ADDR_BIT - 1 : 0]             row_addr_i,
    input       [$clog2(`BANK_BITS) - 1 : 0]        bank_id_i,
    input                                           is_hit_addr_cam_i,
    input                                           addr_cam_out_valid_i,
    input                                           is_hit_count_cam_i,
    input                                           count_cam_out_valid_i,
    input       [$clog2(`N_ENTRY) - 1 : 0]          write_addr_cam_idx_i,
    input       [$clog2(`N_ENTRY) - 1 : 0]          write_count_cam_idx_i,
    output      [`ROW_ADDR_BIT - 1 : 0]             search_addr_cam_idx_o,
    output      [$clog2(`N_ENTRY) - 1 : 0]          write_addr_cam_idx_o,
    output      [`SP_CNT_BIT - 1 : 0]               search_count_cam_idx_o,
    output      [$clog2(`N_ENTRY) - 1 : 0]          write_count_cam_idx_o,
    output                                          search_addr_cam_o, 
    output                                          search_count_cam_o, 
    output                                          write_count_cam_o,
    output       [$clog2(`BANK_BITS) - 1 : 0]       bank_id_o

);
assign bank_id_o = bank_id_i;

localparam  IDLE = 0,
            SEARCH_ADDR_CAM = 1,
            WRITE_ADDR_CAM = 2,
            SEARCH_COUNT_CAM = 3,
            WRITE_COUNT_CAM = 4,
            INC_SP_CNT = 5;

reg [2:0]state_r, state_ns_r;

reg search_addr_cam_o_r, search_addr_cam_o_ns_r;
reg search_count_cam_o_r, search_count_cam_o_ns_r;
reg write_addr_cam_o_r, write_addr_cam_o_ns_r;
reg write_count_cam_o_r, write_count_cam_o_ns_r;

reg [`SP_CNT_BIT - 1 : 0] sp_cnt_r, sp_cnt_ns_r;

always@*begin
    sp_cnt_ns_r = sp_cnt_r;
    search_addr_cam_o_ns_r = 0;
    search_count_cam_o_ns_r = 0;
    write_addr_cam_o_ns_r = 0;
    write_count_cam_o_ns_r = 0;
    state_ns_r = state_r;
    case(state_r)
        IDLE: begin
            if(is_ACT_i) begin
                state_ns_r = SEARCH_ADDR_CAM;
                search_addr_cam_o_ns_r = 1;
            end
            else begin
                state_ns_r = IDLE;
            end
        end
        SEARCH_ADDR_CAM: begin
            search_addr_cam_o_ns_r = 0;
            if(addr_cam_out_valid_i) begin
                if(is_hit_addr_cam_i) begin
                    state_ns_r = WRITE_COUNT_CAM;
                    write_count_cam_o_ns_r = 1;        
                end
                else begin
                    state_ns_r = SEARCH_COUNT_CAM;
                    search_count_cam_o_ns_r = 1;
                end
            end
            else begin
                state_ns_r = SEARCH_ADDR_CAM;
            end
        end
        WRITE_COUNT_CAM: begin
            state_ns_r = IDLE;
        end
        WRITE_ADDR_CAM: begin
            state_ns_r = IDLE;
        end
        SEARCH_COUNT_CAM: begin
            if(count_cam_out_valid_i) begin
                if(is_hit_count_cam_i) begin
                    state_ns_r = WRITE_ADDR_CAM;
                    write_addr_cam_o_ns_r = 1;
                end
                else begin
                    state_ns_r = INC_SP_CNT;
                    write_count_cam_o_ns_r = 1;
                end
            end
            else begin
                state_ns_r = SEARCH_COUNT_CAM;
            end
        end
        INC_SP_CNT: begin
            sp_cnt_ns_r = sp_cnt_r + 1;
            state_ns_r = IDLE;
        end

    endcase
end
always@(posedge clk_i)begin
    if(rst_i)begin
        state_r <= IDLE;
        sp_cnt_r <= 0;
        search_addr_cam_o_r <= 0;
        search_count_cam_o_r <= 0;
        write_addr_cam_o_r <= 0;
        write_count_cam_o_r <= 0;
    end
    else begin
        state_r <= state_ns_r;
        sp_cnt_r <= sp_cnt_ns_r;
        search_addr_cam_o_r <= search_addr_cam_o_ns_r;
        search_count_cam_o_r <= search_count_cam_o_ns_r;
        write_addr_cam_o_r <= write_addr_cam_o_ns_r;
        write_count_cam_o_r <= write_count_cam_o_ns_r;
    end
end
assign search_addr_cam_idx_o = row_addr_i;
assign write_addr_cam_idx_o = write_addr_cam_idx_i;
assign write_count_cam_idx_o = write_count_cam_idx_i;
assign search_count_cam_idx_o = sp_cnt_r;
assign search_addr_cam_o = search_addr_cam_o_r;


endmodule
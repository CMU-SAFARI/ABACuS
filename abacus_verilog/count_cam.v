`include "parameters.vh"
module count_cam

(
    input                                       clk_i,
    input                                       rst_i,
    input [`SP_CNT_BIT - 1 : 0]                 sp_cnt_i,
    input [$clog2(`N_ENTRY) - 1 : 0]            inc_idx_i,
    input [$clog2(`BANK_BITS) - 1 : 0]          bank_id_i,
    input                                       search_i,
    input                                       write_i,
    output [$clog2(`N_ENTRY) - 1 : 0]           address_idx_o,
    output                                      is_hit_o,
    output                                      valid_o

);

reg [`COUNT_CAM_DATA_WIDTH  - 1 : 0] cam_r [`N_ENTRY-1:0];
reg [`COUNT_CAM_DATA_WIDTH - 1 : 0] cam_ns_r [`N_ENTRY-1:0];
reg [`BANK_BITS - 1 : 0] bank_vector_r [`N_ENTRY-1:0];
reg [`BANK_BITS - 1 : 0] bank_vector_ns_r [`N_ENTRY-1:0];

integer i = 0;
localparam  IDLE     = 0,
            WRITE    = 1,
            SEARCH  = 2;
reg [2:0] state_r, state_ns_r;

reg [$clog2(`N_ENTRY)-1:0] current_search_addr_r, current_search_addr_ns_r;
reg is_hit_o_r, is_hit_o_ns_r;
reg valid_o_r, valid_o_ns_r;
reg [$clog2(`N_ENTRY)-1:0] write_addr_r, write_addr_ns_r;
//write an update logic for cam_r
//write an update logic for cam_ns_r
always@(*) begin
    valid_o_ns_r = valid_o_r;
    is_hit_o_ns_r = is_hit_o_r;
    current_search_addr_ns_r = current_search_addr_r;
    state_ns_r = state_r;
    for(i = 0; i < `N_ENTRY; i = i + 1) begin
        cam_ns_r[i] = cam_r[i];
        bank_vector_ns_r[i] = bank_vector_r[i];
    end
    case(state_r)
        IDLE: begin
            is_hit_o_ns_r = 0;
            valid_o_ns_r = 0;
            current_search_addr_ns_r = 0;
            if(search_i) begin
                state_ns_r = SEARCH;
            end
            else if(write_i) begin
                state_ns_r = WRITE;
            end
            else begin
                state_ns_r = IDLE;
            end
        end
        WRITE: begin
            if(bank_vector_r[inc_idx_i][bank_id_i] == 1'b1) begin
                bank_vector_ns_r[inc_idx_i] = 0;
                cam_ns_r[inc_idx_i] = cam_r[inc_idx_i] + 1;
            end
            bank_vector_ns_r[inc_idx_i][bank_id_i] = 1'b1;
            state_ns_r = IDLE;
        end
        SEARCH: begin
            if(current_search_addr_r == `N_ENTRY) begin
                current_search_addr_ns_r = 0;
                valid_o_ns_r = 1;
                state_ns_r = WRITE;
            end
            else begin
                current_search_addr_ns_r = current_search_addr_r + 1;
                if(cam_r[current_search_addr_r] == sp_cnt_i) begin
                    bank_vector_ns_r[current_search_addr_r][bank_id_i] = 1'b1;
                    is_hit_o_ns_r = 1;
                    valid_o_ns_r = 1;
                    state_ns_r = IDLE;
                    cam_ns_r[current_search_addr_r] = sp_cnt_i + 1; 
                    current_search_addr_ns_r = current_search_addr_r;
                end
                else begin
                    state_ns_r = SEARCH;
                    is_hit_o_ns_r = 0;
                    valid_o_ns_r = 0;
                end
            end
        end
        default: begin
            state_ns_r = IDLE;
        end
    endcase
end

always@(posedge clk_i) begin
    if(rst_i) begin
        for(i = 0; i < `N_ENTRY; i = i + 1) begin
            cam_r[i] <= 0;
            bank_vector_r[i] <= 0;
        end
        state_r <= IDLE;
        current_search_addr_r <= 0;
        is_hit_o_r <= 0;
        valid_o_r <= 0;
        write_addr_r <= 0;
    end
    else begin
        for(i = 0; i < `N_ENTRY; i = i + 1) begin
            cam_r[i] <= cam_ns_r[i];
            bank_vector_r[i] <= bank_vector_ns_r[i];
        end
        state_r <= state_ns_r;
        current_search_addr_r <= current_search_addr_ns_r;
        is_hit_o_r <= is_hit_o_ns_r;
        valid_o_r <= valid_o_ns_r;
        write_addr_r <= write_addr_ns_r;
    end
    end

assign is_hit_o = is_hit_o_r;
assign valid_o = valid_o_r;
assign address_idx_o = current_search_addr_r;

endmodule

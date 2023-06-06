module soc_top (
    input clk,
    input rst,

    output                          debug_we,
    output  [ADDR_WID-1:0]          debug_addr,
    output  [DATA_WID-1:0]          debug_data
);
    
    localparam CORE_CNT = 256;
    localparam ADDR_WID = 32;
    localparam DATA_WID = 32;

    wire    [CORE_CNT-1:0]  clk_en;
    wire    [CORE_CNT-1:0]  cpu_en;
    wire                    mem_we;
    wire    [ADDR_WID-1:0]  mem_addr;
    wire    [DATA_WID-1:0]  mem_data;

    genvar i;
    generate
        for (i = 0; i < CORE_CNT; i = i + 1) begin
            core u_core (
                .clk(clk_en[i]),
                .rst(rst),
                .cpu_en(cpu_en[i]),
                .mem_we(mem_we),
                .mem_addr(mem_addr),
                .mem_data(mem_data)
            );
        end
    endgenerate

    mem_ctrl #(
        .ADDR_WID(ADDR_WID),
        .DATA_WID(DATA_WID),
        .CORE_CNT(CORE_CNT)
    ) u_mem_ctrl (
        .clk(clk),
        .rst(rst),
        .clk_en(clk_en),
        .cpu_en(cpu_en),
        .mem_we(mem_we),
        .mem_addr(mem_addr),
        .mem_data(mem_data)
    );

    assign debug_we = mem_we;
    assign debug_addr = mem_addr;
    assign debug_data = mem_data;

endmodule
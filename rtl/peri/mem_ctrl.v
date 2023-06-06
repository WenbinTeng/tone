module mem_ctrl #(
    parameter ADDR_WID = 32,
    parameter DATA_WID = 32,
    parameter CORE_CNT = 16
) (
    input clk,
    input rst,

    output  [CORE_CNT-1:0]  clk_en,
    output  [CORE_CNT-1:0]  cpu_en,
    input                   mem_we,
    input   [ADDR_WID-1:0]  mem_addr,
    inout   [DATA_WID-1:0]  mem_data
);

    reg [31:0] token;

    always @(posedge clk or negedge rst) begin
        if      (~rst)  token = 'b0;
        else            token = token == CORE_CNT - 1 ? 'b0 : token + 'b1;
    end

    wire [3:0] wea = {4{mem_we}};
    wire [ADDR_WID-1:0] addra = mem_addr;
    wire [DATA_WID-1:0] dina = mem_data;
    wire [DATA_WID-1:0] douta;
    
    genvar i;
    generate
        for (i = 0; i < CORE_CNT; i = i + 1) begin
            assign clk_en[i] = clk & (token == i);
            assign cpu_en[i] = token == i;
            assign mem_data = mem_we && (token == i) ? douta : 'bz;
        end
    endgenerate

    blk_mem_gen_0 u_blk_mem_gen_0 (
        .clka(clk),     // input wire clka
        .rsta(rst),    // input wire rsta
        .ena(1),        // input wire ena
        .wea(wea),      // input wire [3 : 0] wea
        .addra(addra),  // input wire [31 : 0] addra
        .dina(dina),    // input wire [31 : 0] dina
        .douta(douta)   // output wire [31 : 0] douta
    );
    
endmodule
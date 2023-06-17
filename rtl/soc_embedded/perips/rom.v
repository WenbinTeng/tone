module rom (
    input           clk,
    input           rst,

    input           mem_we,
    input   [31:0]  mem_addr,
    inout   [31:0]  mem_data
);
    
    localparam CSR_START = 32'hffff8000;
    localparam CSR_END   = 32'hffffbffc;
    localparam GPR_START = 32'hffffc000;
    localparam GPR_END   = 32'hffffc07c;
    localparam TMP_START = 32'hffffc080;
    localparam TMP_END   = 32'hffffc0fc;
    localparam CON_START = 32'hffffc100;
    localparam CON_END   = 32'hffffc1fc;
    localparam PRC_START = 32'hffffe000;
    localparam PRC_END   = 32'hffffffff;

    reg [31:0] csr_array [8191:0];

    always @(posedge clk) begin
        if (mem_we && (mem_addr >= CSR_START) && (mem_addr <= CSR_END)) begin
            csr_array[mem_addr[13:2]] <= mem_data;
        end
    end

    reg [31:0] gpr_array [31:0];

    always @(posedge clk) begin
        if (mem_we && (mem_addr >= GPR_START) && (mem_addr <= GPR_END) && (mem_addr[6:2] != 'b0)) begin
            gpr_array[mem_addr[6:2]] <= mem_data;
        end
    end

    reg [31:0] temp_variable [31:0];

    always @(posedge clk) begin
        if (mem_we && (mem_addr >= TMP_START) && (mem_addr <= TMP_END)) begin
            temp_variable[mem_addr[6:2]-'b10000] <= mem_data;
        end
    end

    wire [31:0] const_value [63:0];

    genvar i;
    generate
        for (i = 0; i < 32; i = i + 1) begin
            assign const_value[i] = 32'h1 << i;
            assign const_value[32+i] = (32'h1 << i) - 1;
        end
    endgenerate

    reg [31:0] procedures [8191:0];

    always @(posedge clk) begin
        if (mem_we && (mem_addr >= PRC_START) && (mem_addr <= PRC_END)) begin
            procedures[mem_addr[12:2]] <= mem_data;
        end
    end

    initial begin
        // $readmemh("init.txt", procedures);
    end

    assign mem_data = rst && !mem_we ?
                      (mem_addr >= CSR_START) && (mem_addr <= CSR_END) ? csr_array[mem_addr[13:2]] :
                      (mem_addr >= GPR_START) && (mem_addr <= GPR_END) ? gpr_array[mem_addr[6:2]] :
                      (mem_addr >= TMP_START) && (mem_addr <= TMP_END) ? temp_variable[mem_addr[6:2]-'b10000] :
                      (mem_addr >= CON_START) && (mem_addr <= CON_END) ? const_value[mem_addr[7:2]] :
                      (mem_addr >= PRC_START) && (mem_addr <= PRC_END) ? procedures[mem_addr[12:2]] :
                      'b0 : 'bz;

endmodule
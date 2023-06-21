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

    integer i;

    // (* ram_style="distributed" *) reg [31:0] csr_array [4095:0];

    // always @(posedge clk) begin
    //     if (mem_we && (mem_addr >= CSR_START) && (mem_addr <= CSR_END)) begin
    //         csr_array[mem_addr[13:2]] <= mem_data;
    //     end
    // end

    (* ram_style="distributed" *) reg [31:0] gpr_array [31:0];

    initial begin
        for (i = 0; i < 32; i = i + 1) begin
            gpr_array[i] <= 'b0;
        end
    end

    always @(posedge clk) begin
        if (mem_we && (mem_addr >= GPR_START) && (mem_addr <= GPR_END) && (mem_addr[6:2] != 'b0)) begin
            gpr_array[mem_addr[6:2]] <= mem_data;
        end
    end

    (* ram_style="distributed" *) reg [31:0] temp_variable [31:0];

    initial begin
        for (i = 0; i < 32; i = i + 1) begin
            temp_variable[i] <= 'b0;
        end
    end

    always @(posedge clk) begin
        if (mem_we && (mem_addr >= TMP_START) && (mem_addr <= TMP_END)) begin
            temp_variable[mem_addr[6:2]-'b10000] <= mem_data;
        end
    end

    wire [31:0] const_value [63:0];

    genvar k;
    generate
        for (k = 0; k < 32; k = k + 1) begin
            assign const_value[k] = 32'h1 << k;
            assign const_value[32+k] = (32'h1 << k) - 1;
        end
    endgenerate

    reg [31:0] rz;

    initial begin
        rz = 'b0;
    end

    always @(posedge clk) begin
        if (mem_we && (mem_addr == 32'hffffc200)) begin
            rz <= mem_data;
        end
    end

    (* ram_style="distributed" *) reg [31:0] procedures [1023:0];

    always @(posedge clk) begin
        if (mem_we && (mem_addr >= PRC_START) && (mem_addr <= PRC_END)) begin
            procedures[mem_addr[11:2]] <= mem_data;
        end
    end

    initial begin
        // $readmemh("init.txt", procedures);
    end

    assign mem_data = rst && !mem_we ?
                    //  (mem_addr >= CSR_START) && (mem_addr <= CSR_END) ? csr_array[mem_addr[13:2]] :
                      (mem_addr >= GPR_START) && (mem_addr <= GPR_END) ? gpr_array[mem_addr[6:2]] :
                      (mem_addr >= TMP_START) && (mem_addr <= TMP_END) ? temp_variable[mem_addr[6:2]-'b10000] :
                      (mem_addr >= CON_START) && (mem_addr <= CON_END) ? const_value[mem_addr[7:2]] :
                      (mem_addr >= PRC_START) && (mem_addr <= PRC_END) ? procedures[mem_addr[11:2]] :
                      mem_addr == 32'hffffc200 ? rz :
                      'bz : 'bz;

endmodule
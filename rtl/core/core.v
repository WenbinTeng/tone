module core (
    input           clk,
    input           rst,
    input           cpu_en,
    output          mem_we,
    output  [31:0]  mem_addr,
    inout   [31:0]  mem_data
);
    
    reg  [ 6:0] state;
    reg  [31:0] pc;
    reg  [31:0] a;
    reg  [31:0] b;
    reg  [31:0] c;
    reg  [31:0] dst;
    wire [31:0] r = a - b;

    always @(posedge clk) begin
        if      (~rst)      state <= 'b1000000;
        else if (state[6])  state <= 'b0000001;
        else                state <= {state[4:0], state[5]};
    end

    always @(posedge clk) begin
        if      (~rst)      a <= 'b0;
        else if (state[0])  a <= trans_endian(mem_data);
        else if (state[3])  a <= trans_endian(mem_data);
    end

    always @(posedge clk) begin
        if      (~rst)      b <= 'b0;
        else if (state[1])  b <= trans_endian(mem_data);
        else if (state[4])  b <= trans_endian(mem_data);
    end

    always @(posedge clk) begin
        if      (~rst)      c <= 'b0;
        else if (state[2])  c <= trans_endian(mem_data);
    end

    always @(posedge clk) begin
        if      (~rst)      pc <= 'b0;
        else if (state[5])  pc <= ($signed(r) <= 0) ? c : pc + 'd12;
    end

    always @(posedge clk) begin
        if      (~rst)      dst <= 'b0;
        else if (state[0])  dst <= trans_endian(mem_data);
    end

    assign mem_we   = rst && cpu_en ? state[5] : 'bz;
    assign mem_data = rst && cpu_en && mem_we ? trans_endian(r) : 'bz;
    assign mem_addr = rst && cpu_en ?
                      state[0] ? pc :
                      state[1] ? pc + 'd4 :
                      state[2] ? pc + 'd8 :
                      state[3] ? a :
                      state[4] ? b :
                      state[5] ? dst :
                      'b0 : 'bz;

    function [31:0] trans_endian(input [31:0] d);
        trans_endian = {d[7:0], d[15:8], d[23:16], d[31:24]};
    endfunction

endmodule
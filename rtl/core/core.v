module core (
    input           clk,
    input           rst,
    output          mem_rd_en,
    input   [31:0]  mem_rd_data,
    output  [31:0]  mem_rd_addr,
    output          mem_wr_en,
    output  [31:0]  mem_wr_addr,
    output  [31:0]  mem_wr_data,
);
    
    reg  [ 5:0] state;
    reg  [31:0] pc;
    reg  [31:0] a;
    reg  [31:0] b;
    reg  [31:0] c;
    wire [31:0] r = a - b;

    always @(posedge clk or posedge rst) begin
        if      (rst)       state <= 'b1;
        else                state <= {state[4:0], state[5]};
    end

    always @(posedge clk or posedge rst) begin
        if      (rst)       a <= 'b0;
        else if (state[0])  a <= mem_rd_data;
        else if (state[3])  a <= mem_rd_data;
    end

    always @(posedge clk or posedge rst) begin
        if      (rst)       b <= 'b0;
        else if (state[1])  b <= mem_rd_data;
        else if (state[4])  b <= mem_rd_data;
    end

    always @(posedge clk or posedge rst) begin
        if      (rst)       c <= 'b0;
        else if (state[2])  c <= mem_rd_data;
    end

    always @(posedge clk or posedge rst) begin
        if      (rst)       pc <= 'b0;
        else if (state[5])  pc <= r <= 0 ? c : pc + 'd12;
    end

    assign mem_rd_en   = ~state[5];
    assign mem_rd_addr = state[0] ? pc :
                         state[1] ? pc + 'd4 :
                         state[2] ? pc + 'd8 :
                         state[3] ? a :
                         state[4] ? b :
                         'b0;
    assign mem_wr_en   = state[5];
    assign mem_wr_addr = pc;
    assign mem_wr_data = r;

endmodule
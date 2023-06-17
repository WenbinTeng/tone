module timer (
    input           clk,
    input           rst,

    input           mem_we,
    input   [31:0]  mem_addr,
    inout   [31:0]  mem_data,

    output          timer_int
);
    
    localparam TIMER_MASK = 32'hffff0030;
    localparam TIMER_DATA = 32'h0;
    localparam TIMER_TINT = 32'h4;
    localparam TIMER_CTRL = 32'h8;

    // timer counter data
    reg [31:0] timer_data;
    // timer expired value to raise interupt
    reg [31:0] timer_tint;
    // timer control register
    // [0]: timer enable
    // [1]: timer interupt enable
    // [2]: timer interupt pending
    reg [31:0] timer_ctrl;

    always @(posedge clk) begin
        if (~rst) begin
            timer_data <= 'b0;
        end
        else begin
            timer_data <= timer_ctrl[0] && (timer_data >= timer_tint) ? 'b0 : timer_data + 'b1;
        end
    end

    always @(posedge clk) begin
        if (~rst) begin
            timer_tint <= 'b0;
            timer_ctrl <= 'b0;
        end
        else if (mem_we) begin
            case (mem_addr)
                TIMER_TINT|TIMER_MASK: timer_tint <= mem_data;
                TIMER_CTRL|TIMER_MASK: timer_ctrl <= mem_data;
            endcase
        end
        else if (timer_ctrl[0] && (timer_data >= timer_tint)) begin
            timer_ctrl[0] = 0;
            timer_ctrl[2] = 1;
        end
    end

    assign mem_data = !mem_we ?
                      mem_addr == (TIMER_DATA|TIMER_MASK) ? timer_data :
                      mem_addr == (TIMER_TINT|TIMER_MASK) ? timer_tint :
                      mem_addr == (TIMER_CTRL|TIMER_MASK) ? timer_ctrl :
                      'b0 : 'bz;

endmodule
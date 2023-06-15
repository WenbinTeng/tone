module led (
    input           clk,
    input           rst,

    input           mem_we,
    input   [31:0]  mem_addr,
    inout   [31:0]  mem_data,

    output          led_r,
    output          led_g,
    output          led_b
);

    localparam LED_MASK = 32'hffff0040;
    localparam LED_DATA = 32'h0;

    reg [31:0] led_data;

    always @(posedge clk or negedge rst) begin
        if (~rst) begin
            led_data <= 0;
        end
        else if (mem_we && (mem_addr == (LED_DATA|LED_MASK))) begin
            led_data <= mem_data;
        end
    end
    
    assign mem_data = !mem_we && (mem_addr == (LED_DATA|LED_MASK)) ? led_data : 'bz;

endmodule
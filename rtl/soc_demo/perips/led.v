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

    localparam LED_MASK = 32'hffff0000;
    localparam LED_DATA = 32'h0;

    reg [31:0] led_data;

    always @(posedge clk) begin
        if (~rst) begin
            led_data <= 0;
        end
        else if (mem_we && (mem_addr == (LED_DATA|LED_MASK))) begin
            led_data <= mem_data;
        end
    end
    
    assign mem_data = rst && !mem_we && (mem_addr == (LED_DATA|LED_MASK)) ? led_data : 'bz;
    assign led_r = led_data[2];
    assign led_g = led_data[1];
    assign led_b = led_data[0];

endmodule
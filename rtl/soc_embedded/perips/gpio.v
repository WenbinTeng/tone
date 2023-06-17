module gpio (
    input           clk,
    input           rst,

    input           mem_we,
    input   [31:0]  mem_addr,
    inout   [31:0]  mem_data,

    inout   [ 7:0]  gpio_pins
);

    localparam GPIO_MASK = 32'hffff0000;
    localparam GPIO_DATA = 32'h0;
    localparam GPIO_CTRL = 32'h4;

    reg [31:0] gpio_data;
    reg [31:0] gpio_ctrl;

    integer i;
    always @(posedge clk) begin
        if (~rst) begin
            gpio_data <= 'h0;
            gpio_ctrl <= 'h0;
        end
        else begin
            if (mem_we) begin
                case (mem_addr)
                    GPIO_DATA|GPIO_MASK: gpio_data <= mem_data;
                    GPIO_CTRL|GPIO_MASK: gpio_ctrl <= mem_data;
                endcase
            end
            else begin
                for (i = 0; i < 8; i = i + 1)
                    if (gpio_ctrl[i])
                        gpio_data[i] <= gpio_pins[i];
            end
        end
    end

    genvar k;
    generate
        for (k = 0; k < 8; k = k + 1) begin
            assign gpio_pins[k] = gpio_ctrl[k] ? 1'bz : gpio_data[k];
        end
    endgenerate

    assign mem_data = !mem_we ?
                      mem_addr == (GPIO_DATA|GPIO_MASK) ? gpio_data :
                      mem_addr == (GPIO_CTRL|GPIO_CTRL) ? gpio_ctrl :
                      'b0 : 'bz;

endmodule
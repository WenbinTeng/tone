module soc_top (
    input           clk,
    input           rst,

    inout   [ 7:0]  gpio_pins,

    input           spi_miso,
    output          spi_mosi,
    output          spi_ss,
    output          spi_sclk,

    input           uart_rx,
    output          uart_tx,

    output          timer_int
);

    wire            mem_we;
    wire    [31:0]  mem_addr;
    wire    [31:0]  mem_data;

    core u_core (
        .clk        (clk),
        .rst        (rst),
        .cpu_en     (1),
        .mem_we     (mem_we),
        .mem_addr   (mem_addr),
        .mem_data   (mem_data)
    );

    gpio u_gpio (
        .clk        (clk),
        .rst        (rst),
        .mem_we     (mem_we),
        .mem_addr   (mem_addr),
        .mem_data   (mem_data),
        .gpio_pins  (gpio_pins)
    );

    spi u_spi (
        .clk        (clk),
        .rst        (rst),
        .mem_we     (mem_we),
        .mem_addr   (mem_addr),
        .mem_data   (mem_data),
        .spi_miso   (spi_miso),
        .spi_mosi   (spi_mosi),
        .spi_ss     (spi_ss),
        .spi_sclk   (spi_sclk)
    );

    uart u_uart (
        .clk        (clk),
        .rst        (rst),
        .mem_we     (mem_we),
        .mem_addr   (mem_addr),
        .mem_data   (mem_data),
        .uart_rx    (uart_rx),
        .uart_tx    (uart_tx)
    );

    timer u_timer (
        .clk        (clk),
        .rst        (rst),
        .mem_we     (mem_we),
        .mem_addr   (mem_addr),
        .mem_data   (mem_data),
        .timer_int  (timer_int)
    );

    ram u_ram (
        .clk        (clk),
        .rst        (rst),
        .mem_we     (mem_we),
        .mem_addr   (mem_addr),
        .mem_data   (mem_data)
    );

    rom u_rom (
        .clk        (clk),
        .rst        (rst),
        .mem_we     (mem_we),
        .mem_addr   (mem_addr),
        .mem_data   (mem_data)
    );
    
endmodule
module soc_top (
    input           clk,
    input           rst,

    output          led_r,
    output          led_g,
    output          led_b
);

    wire            mem_we;
    wire    [31:0]  mem_addr;
    wire    [31:0]  mem_data;

    core u_core (
        .clk        (clk),
        .rst        (rst),
        .cpu_en     (1'b1),
        .mem_we     (mem_we),
        .mem_addr   (mem_addr),
        .mem_data   (mem_data)
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

    led u_led (
        .clk        (clk),
        .rst        (rst),
        .mem_we     (mem_we),
        .mem_addr   (mem_addr),
        .mem_data   (mem_data),
        .led_r      (led_r),
        .led_g      (led_g),
        .led_b      (led_b)
    );

endmodule
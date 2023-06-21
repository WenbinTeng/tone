module ram (
    input           clk,
    input           rst,

    input           mem_we,
    input   [31:0]  mem_addr,
    inout   [31:0]  mem_data
);

    (* ram_style="distributed" *) reg [31:0] ram_array [1023:0];

    always @(posedge clk) begin
        if (mem_we && (mem_addr[31:2] >= 'd0) && (mem_addr[31:2] <= 'd1023)) begin
            ram_array[mem_addr[11:2]] <= mem_data;
        end
    end

    assign mem_data = rst && !mem_we && (mem_addr[31:2] >= 'd0) && (mem_addr[31:2] <= 'd1023) ? ram_array[mem_addr[11:2]] : 'bz;
    
endmodule
module ram (
    input           clk,
    input           rst,

    input           mem_we,
    input   [31:0]  mem_addr,
    inout   [31:0]  mem_data
);

    reg [31:0] ram_array [1023:0];

    always @(posedge clk or negedge rst) begin
        if (~rst) begin

        end
        else if (mem_we && (mem_addr >= 'd0) && (mem_addr <= 'd1023)) begin
            ram_array[mem_addr[11:2]] <= mem_data;
        end
    end

    assign mem_data = !mem_we && (mem_addr >= 'd0) && (mem_addr <= 'd1023) ? ram_array[mem_addr[11:2]] : 'bz;
    
endmodule
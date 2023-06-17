module spi (
    input           clk,
    input           rst,

    input           mem_we,
    input   [31:0]  mem_addr,
    inout   [31:0]  mem_data,

    input           spi_miso,
    output          spi_mosi,
    output          spi_ss,
    output          spi_sclk
);
    
    localparam SPI_MASK = 32'hffff0010;
    localparam SPI_DATA = 32'h0;
    localparam SPI_CTRL = 32'h4;
    localparam SPI_STAT = 32'h8;

    // spi data register
    // [7:0]: cmd or input or output.
    reg [31:0]  spi_data;
    // spi control register
    // [0]: 1-enable, 0-disable.
    // [1]: CPOL, clock polarity.
    // [2]: CPHA, clock phase.
    // [3]: select slave
    reg [31:0]  spi_ctrl;
    // spi status register
    // [0]: 1-busy, 0-idle.
    reg [31:0]  spi_stat;

    reg         _spi_en;
    reg         _spi_done;
    reg [ 7:0]  _spi_rx;
    reg [31:0]  _spi_clk_cnt;
    reg         _spi_clk_edg;
    reg [31:0]  _ext_clk_cnt;
    wire[31:0]  _ext_clk_div;

    always @(posedge clk) begin
        if (~rst) begin
            spi_data <= 'b0;
            spi_ctrl <= 'b0;
            spi_stat <= 'b0;
        end
        else if (mem_we) begin
            spi_stat[0] <= _spi_en;
            case (mem_addr)
                SPI_DATA|SPI_MASK: spi_data <= mem_data;
                SPI_CTRL|SPI_MASK: spi_ctrl <= mem_data;
            endcase
        end
        else begin
            spi_ctrl[0] <= 1'b0;
            spi_stat[0] <= _spi_en;
            if (_spi_done) spi_data <= {24'b0, _spi_rx};
        end
    end

    always @(posedge clk) begin
        if      (~rst)                              _spi_en <= 0;
        else if ( spi_ctrl[0] == 1'b1)              _spi_en <= 1;
        else if (_spi_done    == 1'b1)              _spi_en <= 0;
    end

    always @(posedge clk) begin
        if      (~rst)                              _spi_done <= 0;
        else if (_spi_en && _spi_clk_cnt == 'd17)   _spi_done <= 1;
        else                                        _spi_done <= 0;
    end

    always @(posedge clk) begin
        if      (~rst)                              _ext_clk_cnt <= 'b0;
        else if (_spi_en)                           _ext_clk_cnt <= (_ext_clk_cnt == _ext_clk_div) ? 'b0 : _ext_clk_cnt + 'b1;
        else                                        _ext_clk_cnt <= 'b0;
    end

    always @(posedge clk) begin
        if (~rst) begin
            _spi_clk_cnt <= 'b0;
            _spi_clk_edg <= 'b0;
        end
        else if (_spi_en) begin
            if (_ext_clk_cnt == _ext_clk_div) begin
                if (_spi_clk_cnt == 'd17) begin
                    _spi_clk_cnt <= 'b0;
                    _spi_clk_edg <= 0;
                end
                else begin
                    _spi_clk_cnt <= _spi_clk_cnt + 'b1;
                    _spi_clk_edg <= 1;
                end
            end
            else begin
                _spi_clk_cnt <= _spi_clk_cnt;
                _spi_clk_edg <= 0;
            end
        end
        else begin
            _spi_clk_cnt <= 'b0;
            _spi_clk_edg <= 0;
        end
    end

    reg         mosi_reg;
    reg         sclk_reg;
    reg [3:0]   bits_ptr;

    always @(posedge clk) begin
        if (~rst) begin
            mosi_reg <= 0;
            sclk_reg <= 0;
        end
        else if (_spi_en) begin
            case (_spi_clk_cnt[0])
                1,3,5,7,9,11,13,15: begin
                    sclk_reg <= ~sclk_reg;
                    if (spi_ctrl[2]) begin
                        mosi_reg <= spi_data[bits_ptr];
                        bits_ptr <= bits_ptr - 'b1;
                    end
                    else begin
                        _spi_rx <= {_spi_rx[6:0], spi_miso};
                    end
                end
                2,4,6,8,10,12,14,16: begin
                    sclk_reg <= ~sclk_reg;
                    if (spi_ctrl[2]) begin
                        _spi_rx <= {_spi_rx[6:0], spi_miso};
                    end
                    else begin
                        mosi_reg <= spi_data[bits_ptr];
                        bits_ptr <= bits_ptr - 'b1;
                    end
                end
                17: begin
                    sclk_reg <= spi_ctrl[1];
                end
            endcase
        end
        else begin
            sclk_reg <= spi_ctrl[1];
            mosi_reg <= spi_ctrl[2] == 0 ? spi_data[7] : 'b0;
            bits_ptr <= spi_ctrl[2] == 0 ? 'd6 : 'd7;
        end
    end

    assign spi_mosi = mosi_reg;
    assign spi_sclk = sclk_reg;
    assign spi_ss   = spi_ctrl[0];
    assign mem_data = rst && !mem_we?
                      mem_addr == (SPI_DATA|SPI_MASK) ? spi_data :
                      mem_addr == (SPI_CTRL|SPI_MASK) ? spi_ctrl :
                      mem_addr == (SPI_STAT|SPI_MASK) ? spi_stat :
                      'b0 : 'bz;

endmodule
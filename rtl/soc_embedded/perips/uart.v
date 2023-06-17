module uart(
    input           clk,
    input           rst,

    input           mem_we,
    input   [31:0]  mem_addr,
    inout   [31:0]  mem_data,

    input           uart_rx,
    output          uart_tx
);

    localparam UART_MASK = 32'hffff0020;
    localparam UART_RXDT = 32'h0;
    localparam UART_TXDT = 32'h4;
    localparam UART_CTRL = 32'h8;
    localparam UART_STAT = 32'hc;
    localparam UART_BAUD = 32'hd0;

    // uart receive data
    // [7:0]: data received
    reg [31:0] uart_rx_data;
    // uart transmit data
    // [7:0]: data to transmit
    reg [31:0] uart_tx_data;
    // uart control register
    // [0]: 1-enable-rx, 0-disable-rx
    // [1]: 1-enable-tx, 0-disable-tx
    reg [31:0] uart_ctrl;
    // uart status register
    // [0]: 1-rx-over, 0-rx-receiving
    // [1]: 1-tx-transmitting, 0-tx-idle
    reg [31:0] uart_stat;

    reg         _rx_q0;
    reg         _rx_q1;
    wire        _rx_negedge = _rx_q1 & ~_rx_q0;
    reg         _rx_start;
    reg         _rx_end;
    reg [31:0]  _rx_ext_cnt;
    wire[31:0]  _rx_ext_div = (_rx_ext_cnt == 'b0) ? {1'b0, UART_BAUD[31:1]} : UART_BAUD;
    reg [31:0]  _rx_clk_cnt;
    reg         _rx_clk_edg;

    reg         _tx_start;
    reg         _tx_end;
    reg [31:0]  _tx_ext_cnt;
    wire[31:0]  _tx_ext_div = UART_BAUD;
    reg [31:0]  _tx_bit_cnt;

    always @(posedge clk) begin
        if (~rst) begin
            uart_tx_data <= 'b0;
            uart_ctrl    <= 'b0;
            uart_stat    <= 'b0;
        end
        else if (mem_we) begin
            case (mem_addr)
                UART_CTRL|UART_MASK: uart_ctrl <= mem_data;
                UART_STAT|UART_MASK: uart_stat <= mem_data;
                UART_TXDT|UART_MASK: begin
                    if (uart_ctrl[1]&&~uart_stat[1]) begin
                        uart_tx_data <= {24'b0, mem_data[7:0]};
                        uart_stat[1] <= 1;
                    end
                end
            endcase
        end
        else begin
            if (_tx_end) uart_stat[1] <= 0;
            if (_rx_end && uart_ctrl[0]) uart_stat[0] <= 1;
        end
    end

    always @(posedge clk) begin
        if (~rst) begin
            _rx_q0 <= 0;
            _rx_q1 <= 0;
        end
        else begin
            _rx_q0 <= uart_rx;
            _rx_q1 <= _rx_q0;
        end
    end

    always @(posedge clk) begin
        if (~rst) begin
            _rx_start <= 0;
        end
        else if (uart_ctrl[0]) begin
            if (_rx_negedge) begin
                _rx_start <= 1;
            end
            else if (_rx_ext_cnt == 'd9) begin
                _rx_start <= 0;
            end
        end
        else begin
            _rx_start <= 1;
        end
    end

    always @(posedge clk) begin
        if (~rst) begin
            _rx_end <= 0;
        end
        else if (_rx_start) begin
            if (_rx_clk_edg && _rx_clk_cnt == 'd9) begin
                _rx_end <= 1;
            end
        end
        else begin
            _rx_end <= 0;
        end
    end

    always @(posedge clk) begin
        if (~rst) begin
            _rx_ext_cnt <= 'b0;
        end
        else if (_rx_start) begin
            _rx_ext_cnt <= (_rx_ext_cnt == _rx_ext_div) ? 'b0 : _rx_ext_cnt + 'b1;
        end
        else begin
            _rx_ext_cnt <= 'b0;
        end
    end

    always @(posedge clk) begin
        if (~rst) begin
            _rx_clk_cnt <= 'b0;
            _rx_clk_edg <= 'b0;
        end
        else if (_rx_start) begin
            if (_rx_ext_cnt == _rx_ext_div) begin
                if (_rx_clk_cnt == 'd9) begin
                    _rx_clk_cnt <= 'b0;
                    _rx_clk_edg <= 0;
                end
                else begin
                    _rx_clk_cnt <= _rx_clk_cnt + 'b1;
                    _rx_clk_edg <= 1;
                end
            end
            else begin
                _rx_clk_cnt <= _rx_clk_cnt;
                _rx_clk_edg <= 0;
            end
        end
        else begin
            _rx_clk_cnt <= 'b0;
            _rx_clk_edg <= 0;
        end
    end

    always @(posedge clk) begin
        if (~rst) begin
            uart_rx_data <= 'b0;
        end
        else if (_rx_start && _rx_clk_edg) begin
            case (_rx_clk_cnt)
                1: begin

                end
                2,3,4,5,6,7,8,9: begin
                    uart_rx_data <= uart_rx_data | ({31'b0, uart_rx} << (_rx_clk_cnt - 'd2));
                end
            endcase
        end
    end

    always @(posedge clk) begin
        if (~rst) begin
            _tx_start <= 0;
        end
        else if (mem_we && (mem_addr == UART_TXDT|UART_MASK)) begin
            _tx_start <= 1;
        end
        else begin
            _tx_start <= 0;
        end
    end

    always @(posedge clk) begin
        if (~rst) begin
            _tx_end <= 0;
        end
        else if (_tx_start && (_tx_bit_cnt == 'd9)) begin
            _tx_end <= 1;
        end
        else begin
            _tx_end <= 0;
        end
    end

    always @(posedge clk) begin
        if (~rst) begin
            _tx_ext_cnt <= 'b0;
        end
        else if (_tx_start) begin
            _tx_ext_cnt <= (_tx_ext_cnt == _tx_ext_div) ? 'b0 : _tx_ext_cnt + 'b1;
        end
        else begin
            _tx_ext_cnt <= 'b0;
        end
    end

    always @(posedge clk) begin
        if (~rst) begin
            _tx_bit_cnt <= 'b0;
        end
        else if (_tx_start && (_tx_ext_cnt == _tx_ext_div)) begin
            _tx_bit_cnt <= _tx_bit_cnt + 'b1;
        end
        else begin
            _tx_bit_cnt <= 'b0;
        end
    end

    reg tx_reg;

    always @(posedge clk) begin
        if (~rst) begin
            tx_reg <= 1;
        end
        else if (_tx_start) begin
            case (_tx_bit_cnt)
                1: begin
                    tx_reg <= 0;
                end
                2,3,4,5,6,7,8,9: begin
                    tx_reg <= uart_tx_data[_tx_bit_cnt - 'd2];
                end
                default: begin
                    tx_reg <= 1;
                end
            endcase
        end
        else begin
            tx_reg <= 1;
        end
    end

    assign uart_tx  = tx_reg;
    assign mem_data = !mem_we ?
                      mem_addr == (UART_RXDT|UART_MASK) ? uart_rx_data :
                      mem_addr == (UART_CTRL|UART_MASK) ? uart_ctrl :
                      mem_addr == (UART_STAT|UART_MASK) ? uart_stat :
                      'b0 : 'bz;

endmodule
`default_nettype none

module tt_um_systolic_matmul (
    input  wire [7:0] ui_in,
    output reg  [7:0] uo_out,
    input  wire [7:0] uio_in,
    output reg  [7:0] uio_out,
    output reg  [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    reg [3:0] state;
    reg [3:0] A [1:0][1:0];
    reg [3:0] B [1:0][1:0];
    reg [7:0] C [1:0][1:0];
    reg [2:0] delay_counter;
    reg [1:0] compute_counter;
    reg matrix_a_valid;
    reg matrix_b_valid;

    reg [7:0] temp_ui;
    reg [7:0] temp_uio;

    reg [3:0] pe_a [1:0][1:0];
    reg [3:0] pe_b [1:0][1:0];
    reg [7:0] pe_c [1:0][1:0];

    parameter IDLE        = 4'b0000,
              LOAD_A      = 4'b0001,
              STORE_A     = 4'b0010,
              CHECK_A     = 4'b0011,
              LOAD_B      = 4'b0100,
              STORE_B     = 4'b0101,
              CHECK_B     = 4'b0110,
              COMPUTE     = 4'b0111,
              OUTPUT_1    = 4'b1000,
              OUTPUT_2    = 4'b1001;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            delay_counter <= 0;
            compute_counter <= 0;
            matrix_a_valid <= 0;
            matrix_b_valid <= 0;
            uio_oe <= 8'b00000000;
            uo_out <= 8'h00;
            uio_out <= 8'h00;
            temp_ui <= 8'h00;
            temp_uio <= 8'h00;
            
            integer i, j;
            for (i = 0; i < 2; i = i + 1) begin
                for (j = 0; j < 2; j = j + 1) begin
                    A[i][j] <= 4'h0;
                    B[i][j] <= 4'h0;
                    C[i][j] <= 8'h00;
                    pe_a[i][j] <= 4'h0;
                    pe_b[i][j] <= 4'h0;
                    pe_c[i][j] <= 8'h00;
                end
            end
        end else begin
            case (state)
                IDLE: begin
                    uio_oe <= 8'b00000000;
                    matrix_a_valid <= 0;
                    matrix_b_valid <= 0;
                    state <= LOAD_A;
                end
                LOAD_A: begin
                    temp_ui <= ui_in;
                    temp_uio <= uio_in;
                    state <= STORE_A;
                end
                STORE_A: begin
                    A[0][0] <= temp_ui[7:4];
                    A[0][1] <= temp_ui[3:0];
                    A[1][0] <= temp_uio[7:4];
                    A[1][1] <= temp_uio[3:0];
                    state <= CHECK_A;
                end
                CHECK_A: begin
                    if ((A[0][0] != 0 || A[0][1] != 0) && 
                        (A[1][0] != 0 || A[1][1] != 0)) begin
                        matrix_a_valid <= 1;
                        state <= LOAD_B;
                    end else begin
                        state <= LOAD_A;
                    end
                end
                LOAD_B: begin
                    temp_ui <= ui_in;
                    temp_uio <= uio_in;
                    state <= STORE_B;
                end
                STORE_B: begin
                    B[0][0] <= temp_ui[7:4];
                    B[0][1] <= temp_ui[3:0];
                    B[1][0] <= temp_uio[7:4];
                    B[1][1] <= temp_uio[3:0];
                    state <= CHECK_B;
                end
                CHECK_B: begin
                    if ((B[0][0] != 0 || B[0][1] != 0) && 
                        (B[1][0] != 0 || B[1][1] != 0)) begin
                        matrix_b_valid <= 1;
                        if (matrix_a_valid) begin
                            state <= COMPUTE;
                            compute_counter <= 0;
                        end else begin
                            state <= LOAD_A;
                        end
                    end else begin
                        state <= LOAD_B;
                    end
                end
                COMPUTE: begin
                    if (matrix_a_valid && matrix_b_valid) begin
                        case (compute_counter)
                            2'b00: begin
                                pe_c[0][0] <= A[0][0] * B[0][0];
                                compute_counter <= compute_counter + 1;
                            end
                            2'b01: begin
                                pe_c[0][0] <= pe_c[0][0] + (A[0][1] * B[1][0]);
                                pe_c[0][1] <= A[0][0] * B[0][1];
                                pe_c[1][0] <= A[1][0] * B[0][0];
                                compute_counter <= compute_counter + 1;
                            end
                            2'b10: begin
                                C[0][0] <= pe_c[0][0];
                                C[0][1] <= pe_c[0][1] + (A[0][1] * B[1][1]);
                                C[1][0] <= pe_c[1][0] + (A[1][1] * B[1][0]);
                                C[1][1] <= A[1][0] * B[0][1] + (A[1][1] * B[1][1]);
                                state <= OUTPUT_1;
                            end
                        endcase
                    end else begin
                        state <= IDLE;
                    end
                end
                OUTPUT_1: begin
                    uio_oe <= 8'b11111111;
                    uo_out <= {C[0][0][3:0], C[0][1][3:0]};
                    uio_out <= {C[0][0][7:4], C[0][1][7:4]};
                    state <= OUTPUT_2;
                end
                OUTPUT_2: begin
                    uo_out <= {C[1][0][3:0], C[1][1][3:0]};
                    uio_out <= {C[1][0][7:4], C[1][1][7:4]};
                    state <= IDLE;
                end
                default: begin
                    state <= IDLE;
                end
            endcase
        end
    end
    wire _unused = &{ena, 1'b0};
endmodule

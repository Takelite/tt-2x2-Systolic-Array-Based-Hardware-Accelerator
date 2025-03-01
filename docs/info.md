<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

### Systolic Array Matrix Multiplier

This project implements a 2x2 systolic array matrix multiplier that can multiply two 2x2 matrices where each element is a 4-bit number. The design uses a state machine approach with the following key features:

Matrix Input:

Uses 8 input pins to load two 4-bit numbers at a time
Matrix A and Matrix B are loaded sequentially
Uses bidirectional pins for additional input/output capability
State Machine:

IDLE: Initial state
LOAD_A/STORE_A: Load first matrix
CHECK_A: Validate Matrix A
LOAD_B/STORE_B: Load second matrix
CHECK_B: Validate Matrix B
COMPUTE: Perform systolic computation
OUTPUT_1/OUTPUT_2: Output results
Computation:

Uses systolic array architecture for matrix multiplication
Implements pipelined multiplication and accumulation
Handles 4-bit numbers with 8-bit result precision
Output:

Outputs the result matrix row by row
Uses both dedicated and bidirectional pins for output

## How to test

Input Format:

ui_in[7:4], ui_in[3:0]: First row elements
uio_in[7:4], uio_in[3:0]: Second row elements
Test Sequence:
a. Reset the system (rst_n = 0)
b. Load Matrix A:

First row: ui_in = {a11, a12}
Second row: uio_in = {a21, a22}
c. Load Matrix B:
First row: ui_in = {b11, b12}
Second row: uio_in = {b21, b22}
d. Wait for computation
e. Read results from uo_out and uio_out
Example Test Case:
Matrix A = [1 2] Matrix B = [5 6]
[3 4] [7 8]

Expected Result = [19 22]
[43 50]

Pin Usage:

ui_in[7:0]: Input pins for matrix elements
uio_in[7:0]: Bidirectional pins for input/output
uo_out[7:0]: Output pins for results
uio_oe[7:0]: Bidirectional pin direction control
clk: System clock (100MHz)
rst_n: Active low reset
ena: Enable signal (always 1)

## External hardware

This design implements a systolic hardware accelerator specifically designed to offload matrix multiplication tasks from FPGAs. The accelerator can be integrated with various FPGA platforms (e.g., ICE40, Xilinx, Intel) to enhance matrix multiplication performance:

Integration Example:

Main FPGA runs the primary computation tasks
TinyTapeout systolic accelerator functions as a dedicated matrix multiplication co-processor
Simple interface through standard input/output pins allows easy integration with any FPGA
Bidirectional pins provide flexible data transfer options
System Benefits:

Offloads computationally intensive matrix operations from the main FPGA
Dedicated systolic architecture provides optimized matrix multiplication
Reduces FPGA resource utilization by outsourcing matrix computations
Can be used with any FPGA platform that needs matrix multiplication acceleration
Interface Requirements:

Direct connection to FPGA I/O pins
Basic handshaking protocol for data synchronization
Supports standard digital logic levels
Flexible timing requirements to accommodate different FPGA clock domains

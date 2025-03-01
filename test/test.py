# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

@cocotb.test()
async def test_matrix_multiplication(dut):
    """Test the systolic array matrix multiplication"""

    dut._log.info("Starting Matrix Multiplication Test")

    # Start clock (25MHz = 40ns period)
    clock = Clock(dut.clk, 40, units="ns")
    cocotb.start_soon(clock.start())

    # Initialize signals
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 1

    # Reset sequence
    await RisingEdge(dut.clk)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Ensure stability after reset

    dut._log.info("=== Matrix Multiplication Test ===")
    dut._log.info("Input Matrices:")
    dut._log.info("Matrix A = [1 2; 3 4]")
    dut._log.info("Matrix B = [5 6; 7 8]")
    dut._log.info("Expected Result = [19 22; 43 50]")

    # Step 1: Load Matrix A in a single cycle (packed into ui_in)
    dut.ui_in.value = (1 << 12) | (2 << 8) | (3 << 4) | 4  # Packing: 1 2 3 4
    await ClockCycles(dut.clk, 1)

    # Step 2: Load Matrix B in next cycle (using ui_in and uio_in)
    dut.ui_in.value = (5 << 8) | 6  # Packing: 5 6
    dut.uio_in.value = (7 << 8) | 8  # Packing: 7 8
    await ClockCycles(dut.clk, 1)

    # Step 3: Wait for computation to finish
    await ClockCycles(dut.clk, 3)  # Adjust cycles if needed

    # Step 4: Read output
    result = dut.uo_out.value.integer
    result2 = dut.uio_out.value.integer

    # Extract matrix elements
    result_00 = (result >> 8) & 0xFF
    result_01 = result & 0xFF
    result_10 = (result2 >> 8) & 0xFF
    result_11 = result2 & 0xFF

    # Display and verify results
    dut._log.info(f"Computed Result Matrix:")
    dut._log.info(f"[{result_00} {result_01}]")
    dut._log.info(f"[{result_10} {result_11}]")

    assert result_00 == 19 and result_01 == 22, "First row mismatch"
    assert result_10 == 43 and result_11 == 50, "Second row mismatch"

    dut._log.info("Matrix Multiplication Test: PASSED")

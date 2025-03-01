# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

async def wait_for_output_ready(dut):
    """Wait until output is ready (uio_oe becomes FF) with timeout"""
    for _ in range(1000):  # Prevent infinite loop
        await RisingEdge(dut.clk)
        if dut.uio_oe.value == 0xFF:
            return
    dut._log.error("Timeout waiting for output ready")

@cocotb.test()
async def test_matrix_multiplication(dut):
    """Test the matrix multiplication functionality"""

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
    dut._log.info("Input matrices:")
    dut._log.info("Matrix A = [1 2; 3 4]")
    dut._log.info("Matrix B = [5 6; 7 8]")
    dut._log.info("Expected Result = [19 22; 43 50]")

    # Load Matrix A
    dut.ui_in.value = 0x12   # [1,2]
    dut.uio_in.value = 0x34  # [3,4]
    await ClockCycles(dut.clk, 4)

    # Load Matrix B
    dut.ui_in.value = 0x56   # [5,6]
    dut.uio_in.value = 0x78  # [7,8]
    await ClockCycles(dut.clk, 4)

    # Clear inputs
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # Wait for computation and output ready
    await wait_for_output_ready(dut)
    dut._log.info("Reading outputs")

    # Read results
    await RisingEdge(dut.clk)
    output_val = dut.uo_out.value.integer
    output_val2 = dut.uio_out.value.integer

    # Extract matrix elements
    result_00 = (output_val >> 8) & 0xFF
    result_01 = output_val & 0xFF
    result_10 = (output_val2 >> 8) & 0xFF
    result_11 = output_val2 & 0xFF

    # Display and verify results
    dut._log.info(f"Result matrix:")
    dut._log.info(f"[{result_00} {result_01}]")
    dut._log.info(f"[{result_10} {result_11}]")

    assert result_00 == 19 and result_01 == 22, "First row mismatch"
    assert result_10 == 43 and result_11 == 50, "Second row mismatch"

    dut._log.info("Matrix Multiplication Test: PASSED")
    await ClockCycles(dut.clk, 2)
    dut._log.info("Test completed")

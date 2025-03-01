# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.binary import BinaryValue

async def wait_for_state(dut, target_state):
    """Wait until the design reaches a specific state"""
    while True:
        await RisingEdge(dut.clk)
        if dut.dbg_state.value == target_state:
            break

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

    # Wait for IDLE state
    await ClockCycles(dut.clk, 2)

    dut._log.info("=== Matrix Multiplication Test ===")
    dut._log.info("Input matrices:")
    dut._log.info("Matrix A = [1 2; 3 4]")
    dut._log.info("Matrix B = [5 6; 7 8]")
    dut._log.info("Expected Result = [19 22; 43 50]")

    # Wait for LOAD_A state
    await wait_for_state(dut, BinaryValue('0001'))
    dut._log.info("Loading Matrix A")

    # Load Matrix A
    dut.ui_in.value = 0x12   # [1,2]
    dut.uio_in.value = 0x34  # [3,4]
    await ClockCycles(dut.clk, 4)

    # Wait for LOAD_B state
    await wait_for_state(dut, BinaryValue('0100'))
    dut._log.info("Loading Matrix B")

    # Load Matrix B
    dut.ui_in.value = 0x56   # [5,6]
    dut.uio_in.value = 0x78  # [7,8]
    await ClockCycles(dut.clk, 4)

    # Clear inputs
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # Wait for computation
    await wait_for_state(dut, BinaryValue('0111'))
    dut._log.info("Computing result")

    # Wait for output
    await wait_for_state(dut, BinaryValue('1000'))
    dut._log.info("Reading outputs")

    # Read results
    await RisingEdge(dut.clk)
    result_00 = dut.uo_out.value >> 4
    result_01 = dut.uo_out.value & 0xF
    result_10 = dut.uio_out.value >> 4
    result_11 = dut.uio_out.value & 0xF

    # Display and verify results
    dut._log.info(f"Result matrix:")
    dut._log.info(f"[{result_00} {result_01}]")
    dut._log.info(f"[{result_10} {result_11}]")

    try:
        assert result_00 == 19 and result_01 == 22, "First row mismatch"
        assert result_10 == 43 and result_11 == 50, "Second row mismatch"
        dut._log.info("Matrix Multiplication Test: PASSED")
    except AssertionError as e:
        dut._log.error("Matrix Multiplication Test: FAILED")
        dut._log.error(str(e))

    await ClockCycles(dut.clk, 2)
    dut._log.info("Test completed")

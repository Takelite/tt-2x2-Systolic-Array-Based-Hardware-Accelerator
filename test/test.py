# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge
from cocotb.binary import BinaryValue

async def wait_for_state(dut, target_state):
    while True:
        await RisingEdge(dut.clk)
        if dut.state.value == target_state:
            break

@cocotb.test()
async def test_matrix_multiplication(dut):
    dut._log.info("Starting Matrix Multiplication Test")

    # Start the clock
    clock = Clock(dut.clk, 10, units="ns")  # 100MHz clock
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
    dut._log.info("Matrix A = [1 2; 3 4]")
    dut._log.info("Matrix B = [5 6; 7 8]")
    dut._log.info("Expected Result = [19 22; 43 50]")

    # Wait for LOAD_A state
    await wait_for_state(dut, BinaryValue('0001'))

    # Load Matrix A
    dut.ui_in.value = 0x12   # [1,2]
    dut.uio_in.value = 0x34  # [3,4]

    # Wait for Matrix A validation
    while True:
        await RisingEdge(dut.clk)
        if dut.matrix_a_valid.value == 1:
            break

    # Clear inputs
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # Wait for LOAD_B state
    await wait_for_state(dut, BinaryValue('0100'))

    # Load Matrix B
    dut.ui_in.value = 0x56   # [5,6]
    dut.uio_in.value = 0x78  # [7,8]

    # Wait for Matrix B to be stored
    await wait_for_state(dut, BinaryValue('0101'))
    await ClockCycles(dut.clk, 2)

    # Clear inputs
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # Wait for computation and output
    await wait_for_state(dut, BinaryValue('1000'))

    # Verify results
    await RisingEdge(dut.clk)
    
    # Get results from C matrix
    c00 = dut.C[0][0].value
    c01 = dut.C[0][1].value
    c10 = dut.C[1][0].value
    c11 = dut.C[1][1].value

    # Display results
    dut._log.info(f"Got result: [{c00} {c01}; {c10} {c11}]")

    # Assert expected results
    assert c00 == 19, f"C[0][0] = {c00}, expected 19"
    assert c01 == 22, f"C[0][1] = {c01}, expected 22"
    assert c10 == 43, f"C[1][0] = {c10}, expected 43"
    assert c11 == 50, f"C[1][1] = {c11}, expected 50"

    dut._log.info("Matrix Multiplication Test: PASSED")

    # Wait for completion
    await wait_for_state(dut, BinaryValue('0000'))
    await ClockCycles(dut.clk, 2)

@cocotb.test()
async def test_reset_behavior(dut):
    """Test reset behavior"""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Initialize
    dut.ena.value = 1
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # Assert reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)

    # Check reset values
    assert dut.state.value == 0, "State not reset to IDLE"
    assert dut.matrix_a_valid.value == 0, "matrix_a_valid not reset"
    assert dut.matrix_b_valid.value == 0, "matrix_b_valid not reset"

    dut._log.info("Reset Test: PASSED")

@cocotb.test()
async def test_invalid_input(dut):
    """Test behavior with invalid inputs"""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Initialize
    dut.ena.value = 1
    dut.rst_n.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1

    # Try loading zero matrix
    await wait_for_state(dut, BinaryValue('0001'))
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # Should not validate
    await ClockCycles(dut.clk, 5)
    assert dut.matrix_a_valid.value == 0, "Zero matrix should not validate"

    dut._log.info("Invalid Input Test: PASSED")

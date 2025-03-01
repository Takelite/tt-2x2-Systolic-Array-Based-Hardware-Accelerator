# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_systolic_matmul(dut):
    dut._log.info("Start test")

    # Set up the clock (10 us period, 100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset the DUT
    dut._log.info("Applying reset")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 5)

    # Provide Matrix A (Example: [[2, 1], [3, 4]])
    dut.ui_in.value = 0b00100001  # A[0][0] = 2, A[0][1] = 1
    dut.uio_in.value = 0b00110100  # A[1][0] = 3, A[1][1] = 4
    await ClockCycles(dut.clk, 5)

    # Provide Matrix B (Example: [[1, 2], [3, 4]])
    dut.ui_in.value = 0b00010010  # B[0][0] = 1, B[0][1] = 2
    dut.uio_in.value = 0b00110100  # B[1][0] = 3, B[1][1] = 4
    await ClockCycles(dut.clk, 5)

    # Wait for computation to complete
    await ClockCycles(dut.clk, 10)

    # Check outputs for expected results: [[5, 8], [15, 22]]
    expected_results = [
        (0b00000101, 0b00001000),  # Row 1: C[0][0] = 5, C[0][1] = 8
        (0b00001111, 0b00010110)  # Row 2: C[1][0] = 15, C[1][1] = 22
    ]

    for i, (expected_uo, expected_uio) in enumerate(expected_results):
        await ClockCycles(dut.clk, 1)
        assert dut.uo_out.value == expected_uo, f"Mismatch in row {i+1}: uo_out = {dut.uo_out.value}"
        assert dut.uio_out.value == expected_uio, f"Mismatch in row {i+1}: uio_out = {dut.uio_out.value}"
        dut._log.info(f"Row {i+1} correct: uo_out = {dut.uo_out.value}, uio_out = {dut.uio_out.value}")

    dut._log.info("Test completed successfully!")


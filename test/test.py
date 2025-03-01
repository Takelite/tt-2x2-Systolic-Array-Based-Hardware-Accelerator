import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

@cocotb.test()
async def test_systolic_matmul(dut):
    dut._log.info("Starting Systolic Matrix Multiplier Test")

    # Clock setup
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset sequence
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    dut._log.info("Applying test vectors")

    # Load Matrix A
    await RisingEdge(dut.clk)
    dut.ui_in.value = 0x12  # Matrix A: [1,2]
    dut.uio_in.value = 0x34  # Matrix A: [3,4]
    await ClockCycles(dut.clk, 2)

    # Load Matrix B
    await RisingEdge(dut.clk)
    dut.ui_in.value = 0x56  # Matrix B: [5,6]
    dut.uio_in.value = 0x78  # Matrix B: [7,8]
    await ClockCycles(dut.clk, 2)

    # Wait for computation
    await ClockCycles(dut.clk, 10)

    # Check output values
    expected_C = [[19, 22], [43, 50]]
    result_C = [
        [int(dut.uo_out.value[7:4]), int(dut.uo_out.value[3:0])],
        [int(dut.uio_out.value[7:4]), int(dut.uio_out.value[3:0])]
    ]

    assert result_C == expected_C, f"Test failed: Expected {expected_C}, Got {result_C}"
    dut._log.info("Matrix Multiplication Test PASSED")

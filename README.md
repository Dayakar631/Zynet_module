# Zynet_module
Deploying Your ZyNet Accelerator on PYNQ
The process involves loading your custom-built hardware (the ZyNet module) onto the FPGA and then using the PYNQ framework to control it with Python. This combines high-performance hardware acceleration with high-level software simplicity.

The Core Components
ZyNet Module: This is your custom-built neural network accelerator, designed in hardware and implemented on the FPGA's Programmable Logic (PL). It contains all the necessary components like neuron arrays, internal weight/bias memories, and activation function logic to perform fast AI inference. * PYNQ Framework: An open-source framework from Xilinx that runs on the Zynq's ARM processor. It allows you to program and control the FPGA fabric using simple Python commands, abstracting away the low-level hardware complexity.

The Overlay: This is the package that contains your hardware design. It consists of:

A .bit file (Bitstream): The raw binary data that physically configures the FPGA's logic gates to become your ZyNet accelerator.

A .hwh file (Hardware Handoff): A metadata file that acts as a "map" for PYNQ, describing the components in your design, their addresses, and how to communicate with them.

System Architecture: How It All Connects
The PYNQ-Z2 board uses the Zynq SoC, which integrates a processor and an FPGA. Your design leverages both parts to work as a cohesive system.

Zynq Processing System (PS): The "manager" of the operation. It runs Linux and the PYNQ framework, executing your Python scripts.

Programmable Logic (PL): The "custom factory floor" where the hardware acceleration happens. It contains your ZyNet module and an AXI DMA controller.

Communication Busses:

AXI4-Lite: A lightweight interface used by the PS to send control commands and read results from the ZyNet module's registers.

AXI4 Stream: A high-speed interface used by the AXI DMA to stream the input image data directly to the ZyNet module, bypassing the processor for maximum efficiency.

The Step-by-Step Python Workflow
Here is the exact process to load and run your ZyNet accelerator from a Jupyter Notebook on the PYNQ-Z2.

1. Place Your Overlay Files
First, you must copy your overlay files (your_design.bit and your_design.hwh) onto the PYNQ-Z2 board. Typically, you'll place them in a dedicated directory within the /home/xilinx/pynq/overlays/ folder. This allows the PYNQ framework to discover your design.

2. Load the Bitstream onto the FPGA
In a Jupyter Notebook, the first step is to load your hardware design. This one line of Python code programs the entire FPGA.

Python

from pynq import Overlay

# Load the bitstream onto the FPGA's Programmable Logic
overlay = Overlay('/home/xilinx/pynq/overlays/your_design/your_design.bit')
After this command executes, the FPGA is no longer a blank slate; it has been physically configured to be your ZyNet CNN accelerator.

3. Prepare and Send the Input Image
Next, you'll prepare your input image (e.g., a 28x28 digit) and send it to the hardware using the DMA.

Python

from pynq import allocate
import numpy as np

# 1. Prepare input data (e.g., a flattened 28x28 image)
#    This should be a NumPy array.
input_image = np.array([...], dtype=np.uint8) 

# 2. Allocate a physically contiguous memory buffer for DMA
input_buffer = allocate(shape=input_image.shape, dtype=np.uint8)
input_buffer[:] = input_image

# 3. Access the DMA controller from the overlay
dma = overlay.axi_dma_0

# 4. Send the data from the buffer to the ZyNet module
dma.sendchannel.transfer(input_buffer)
dma.sendchannel.wait() # Wait for the transfer to complete
4. Retrieve the Final Result
Once the DMA transfer is done, the ZyNet module processes the image. After a brief moment, you can read the final recognized digit directly from the accelerator's output register.

Python

# The output register's address offset, defined in your hardware design
OUTPUT_REGISTER_OFFSET = 0x08 

# Access the ZyNet module's control registers via the AXI Lite interface
zynet_registers = overlay.zynet_0.mmio

# Read the 32-bit value from the output register
recognized_digit = zynet_registers.read(OUTPUT_REGISTER_OFFSET)

print(f"The hardware recognized the digit: {recognized_digit}")

# Don't forget to free the buffer when you're done
input_buffer.freebuffer()

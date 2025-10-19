# End-to-End Design of a Hardware-Accelerated CNN on a Zynq SoC

This repository documents the complete design, training, verification, and deployment of a custom Convolutional Neural Network (CNN) hardware accelerator on a Xilinx Zynq-7000 SoC. The system is architected for high-performance, low-latency handwritten digit recognition and is controlled by the user-friendly PYNQ (Python Productivity for Zynq) framework, enabling seamless software-hardware interaction.

---

## 🚀 The Core Idea: Hybrid Computing with Zynq

Modern AI applications, especially at the edge, demand high performance and low power consumption—a challenge for traditional CPUs. This project leverages the hybrid nature of the **Zynq SoC**, which combines two powerful components on a single chip:

* **Processing System (PS):** A dual-core ARM Cortex-A9 processor that acts as the "manager." It runs a full Linux operating system and handles high-level tasks, control flow, and user interaction.
* **Programmable Logic (PL):** An FPGA fabric that acts as a "custom factory floor." We can design and implement a highly specialized, parallel hardware circuit—our **ZyNet CNN accelerator**—directly on the PL.

This architecture allows us to offload the computationally-intensive task of AI inference to the custom hardware, freeing up the processor and achieving a massive performance boost.

---

## 🏛️ System Architecture: A Detailed Look

The entire system is designed for efficient communication and data flow between the PS and PL, using the industry-standard AXI protocol suite.



* **The ZyNet CNN Accelerator:** This is our custom IP block implemented in the PL. It receives image data and performs the classification.
* **AXI DMA Controller:** This is the "automated forklift" of our system. It is responsible for moving large blocks of data (the input image) from the main system memory (DDR) directly to the ZyNet accelerator without involving the processor. This is crucial for high-throughput performance.
* **AXI4-Stream Interface:** This interface acts as a "high-speed conveyor belt," used by the DMA to stream the pixel data continuously and efficiently to the ZyNet module.
* **AXI4-Lite Interface:** This interface is the "manager's control panel." It's a lightweight bus used by the PS to configure the ZyNet module, issue commands (like reset), and read the final status and result from its registers.

---

## 🧠 Hardware Deep Dive: Inside the ZyNet Accelerator

The ZyNet accelerator is a multi-layer neural network designed specifically for efficient hardware implementation.

### The Neuron: The Fundamental Building Block

The network is built from a single, modular neuron design. Each neuron is a self-contained unit with:
* **Internal Weight & Bias Memory:** Stores the unique parameters learned during training.
* **Multiplier-Accumulator (MAC) Unit:** Performs the core mathematical operations.
* **Configurable Activation Function:** Can be instantiated as either ReLU or a Look-Up-Table-based Sigmoid function for efficiency.



### Pipelined Architecture

The full network consists of three layers (30, 20, and 10 neurons, respectively) arranged in a **pipelined** structure. This works like a factory assembly line: registers are placed between each layer to hold intermediate results. This allows Layer 1, Layer 2, and Layer 3 to all be processing different data simultaneously, maximizing throughput. A final **Max Finder** unit identifies which of the 10 output neurons has the highest activation to determine the final digit.

### The Core Design Principle: Sequential Setup vs. Parallel Execution

A critical concept in this architecture is the separation of configuration and execution:

1.  **Sequential Configuration:** Before any computation, the ARM processor must load the weights and biases into all 60 neurons. This is a **sequential** process. It uses the **AXI-Lite interface** to access a set of control registers (`layerReg`, `neuronReg`, `weightReg`) and configure each neuron one by one. The registers act as a temporary "mailbox" for loading parameters into each neuron's dedicated internal memory.

2.  **Parallel Execution:** This is where the acceleration happens. When an image is sent for classification, the input data is broadcast to all 30 neurons in the first layer **simultaneously**. Each neuron performs its calculations at the exact same time. This massive parallelism is what makes the hardware accelerator significantly faster than a purely software-based solution.

---

## 🐍 Software Control with PYNQ

The PYNQ framework makes this powerful hardware accessible from easy-to-use Python code running in a Jupyter Notebook.

### The Overlay: Your Hardware as a Python Object

The entire hardware design is packaged as an **overlay**. This consists of:
* A **`.bit` file:** The bitstream that physically programs the FPGA logic with your ZyNet design.
* A **`.hwh` file:** A hardware handoff file that acts as a "map" or "user manual". PYNQ parses this file to automatically understand your design's components (like the DMA and ZyNet IP), their memory addresses, and their functions, creating easy-to-use Python objects for them.

### Step-by-Step Deployment on the PYNQ-Z2 Board

The following code demonstrates the end-to-end workflow in a Jupyter Notebook.

#### 1. Load the Hardware Overlay

This command dynamically programs the FPGA with your CNN accelerator. The PYNQ framework streams the `.bit` file to the FPGA's configuration memory.
# Prepare a flattened 28x28 image as a NumPy array
input_image = np.array([...], dtype=np.uint8) 

# Allocate a contiguous memory buffer for DMA
input_buffer = allocate(shape=input_image.shape, dtype=np.uint8)
input_buffer[:] = input_image

# Access the DMA controller object, which PYNQ created from the HWH file
dma = overlay.axi_dma_0

# Start the DMA transfer from the buffer to the accelerator's stream interface
dma.sendchannel.transfer(input_buffer)
dma.sendchannel.wait() # Pause execution until the transfer is complete
# Define the output register's address offset from the hardware design
OUTPUT_REGISTER_OFFSET = 0x08 

# Access the accelerator's control registers via the MMIO object
zynet_ip = overlay.zynet_0
recognized_digit = zynet_ip.mmio.read(OUTPUT_REGISTER_OFFSET)

print(f"Recognized Digit: {recognized_digit}")

# Free the memory buffer to prevent memory leaks
input_buffer.freebuffer()
```python
# Prepare a flattened 28x28 image as a NumPy array
input_image = np.array([...], dtype=np.uint8) 

# Allocate a contiguous memory buffer for DMA
input_buffer = allocate(shape=input_image.shape, dtype=np.uint8)
input_buffer[:] = input_image

# Access the DMA controller object, which PYNQ created from the HWH file
dma = overlay.axi_dma_0

# Start the DMA transfer from the buffer to the accelerator's stream interface
dma.sendchannel.transfer(input_buffer)
dma.sendchannel.wait() # Pause execution until the transfer is complete
from pynq import Overlay, allocate
import numpy as np

# Load the bitstream onto the FPGA. PYNQ parses the HWH file automatically.
overlay = Overlay('path/to/your_design/zynet.bit')

# Stage 1: Builder (Full DeepStream SDK + Build Tools)
FROM nvcr.io/nvidia/deepstream:8.0-triton-devel AS builder

WORKDIR /opt/nvidia/deepstream/deepstream

# Install build tools
RUN apt-get update && apt-get install -y \
    git \
    make \
    g++ \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy and build our custom C++ parser from the monorepo
COPY ./services/processor/src /opt/nvidia/deepstream/deepstream/custom_parser
COPY ./services/processor/CMakeLists.txt /opt/nvidia/deepstream/deepstream/custom_parser/

# Build the custom YOLO parser
RUN cd /opt/nvidia/deepstream/deepstream/custom_parser && \
    mkdir -p build && cd build && \
    cmake .. && make -j$(nproc) && \
    ls -la *.so

# Stage 2: Runtime (Minimal Base Image + Python)
FROM nvcr.io/nvidia/deepstream:8.0-base

WORKDIR /app

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt && \
    # DS 8.0 Python bindings require numpy < 2.0
    pip3 install --force-reinstall numpy==1.26.0

# Copy ONLY the compiled artifact from the 'builder' stage
COPY --from=builder /opt/nvidia/deepstream/deepstream/custom_parser/build/*.so /opt/nvidia/deepstream/deepstream/lib/

# Copy our application code
COPY ./services/processor .

# Create output directory for HLS streams
RUN mkdir -p /opt/aries/streams

# Set environment variables
ENV PYTHONPATH=/opt/nvidia/deepstream/deepstream/lib:${PYTHONPATH}
ENV GST_PLUGIN_PATH=/opt/nvidia/deepstream/deepstream/lib/gst-plugins:${GST_PLUGIN_PATH}

# Run the application
CMD ["python3", "main_processor.py"]
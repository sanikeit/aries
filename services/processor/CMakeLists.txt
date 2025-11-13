cmake_minimum_required(VERSION 3.16)
project(yolo_parser)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find CUDA
find_package(CUDA REQUIRED)

# Find DeepStream
set(DEEPSTREAM_PATH /opt/nvidia/deepstream/deepstream-6.4)
set(DEEPSTREAM_INCLUDE_DIR ${DEEPSTREAM_PATH}/sources/includes)

# Include directories
include_directories(
    ${CUDA_INCLUDE_DIRS}
    ${DEEPSTREAM_INCLUDE_DIR}
    /usr/local/cuda/include
)

# Source files
set(SOURCES
    src/nvdsinfer_customparser_yolo.cpp
)

# Create shared library
add_library(nvdsinfer_custom_impl_yolo SHARED ${SOURCES})

# Link libraries
target_link_libraries(nvdsinfer_custom_impl_yolo
    ${CUDA_LIBRARIES}
    cudart
)

# Set properties
set_target_properties(nvdsinfer_custom_impl_yolo PROPERTIES
    PREFIX ""
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/lib
)

# Install target
install(TARGETS nvdsinfer_custom_impl_yolo
    LIBRARY DESTINATION lib
)
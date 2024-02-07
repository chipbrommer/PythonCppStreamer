# CMakeList.txt : CMake project for MiniStrike_ImageTracking, include source and define
# project specific logic here.
#
cmake_minimum_required (VERSION 3.8)

# Define an option for the "colibri" flag
option(COLIBRI "Enable compilation for Colibri platform" OFF)

# Check if COLIBRI option is enabled
if(COLIBRI)
    # Specify the cross-compiler for aarch64-linux-gnu-g++
    set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)
    # Print a message to the console
    message(STATUS "NOTICE: Compilation for Colibri platform enabled. Using aarch64-linux-gnu-g++ as the C++ compiler.")
endif()

# Enable Hot Reload for MSVC compilers if supported.
if (POLICY CMP0141)
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()

project ("ImageTracking")

# Add source to this project's executable.
add_executable (ImageTracking "main.cpp"  
    "eo_interface.cpp" 
    "eo_interface.h"
)

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET ImageTracking PROPERTY CXX_STANDARD 20)
endif()

# Include nlohmanns json
target_include_directories(ImageTracking PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/nlohmann)

# Include Python scripts folder
target_include_directories(ImageTracking PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/scripts)

# Creaing a useable definition in the c++ main for the scripts folder 
get_filename_component(PROJECT_ROOT ${CMAKE_SOURCE_DIR} ABSOLUTE)
set(SCRIPTS_FOLDER "scripts")
set(SCRIPTS_PATH "${PROJECT_ROOT}/${SCRIPTS_FOLDER}")
add_definitions(-DSCRIPTS_PATH="${SCRIPTS_PATH}")

# Set the desired name for the executable with an extension
set_target_properties(ImageTracking PROPERTIES OUTPUT_NAME "ImageTracking.out")
# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.10

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/build

# Include any dependencies generated for this target.
include CMakeFiles/ImageTracking.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/ImageTracking.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/ImageTracking.dir/flags.make

CMakeFiles/ImageTracking.dir/main.cpp.o: CMakeFiles/ImageTracking.dir/flags.make
CMakeFiles/ImageTracking.dir/main.cpp.o: ../main.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/ImageTracking.dir/main.cpp.o"
	/usr/bin/aarch64-linux-gnu-g++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/ImageTracking.dir/main.cpp.o -c /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/main.cpp

CMakeFiles/ImageTracking.dir/main.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/ImageTracking.dir/main.cpp.i"
	/usr/bin/aarch64-linux-gnu-g++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/main.cpp > CMakeFiles/ImageTracking.dir/main.cpp.i

CMakeFiles/ImageTracking.dir/main.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/ImageTracking.dir/main.cpp.s"
	/usr/bin/aarch64-linux-gnu-g++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/main.cpp -o CMakeFiles/ImageTracking.dir/main.cpp.s

CMakeFiles/ImageTracking.dir/main.cpp.o.requires:

.PHONY : CMakeFiles/ImageTracking.dir/main.cpp.o.requires

CMakeFiles/ImageTracking.dir/main.cpp.o.provides: CMakeFiles/ImageTracking.dir/main.cpp.o.requires
	$(MAKE) -f CMakeFiles/ImageTracking.dir/build.make CMakeFiles/ImageTracking.dir/main.cpp.o.provides.build
.PHONY : CMakeFiles/ImageTracking.dir/main.cpp.o.provides

CMakeFiles/ImageTracking.dir/main.cpp.o.provides.build: CMakeFiles/ImageTracking.dir/main.cpp.o


CMakeFiles/ImageTracking.dir/eo_interface.cpp.o: CMakeFiles/ImageTracking.dir/flags.make
CMakeFiles/ImageTracking.dir/eo_interface.cpp.o: ../eo_interface.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object CMakeFiles/ImageTracking.dir/eo_interface.cpp.o"
	/usr/bin/aarch64-linux-gnu-g++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/ImageTracking.dir/eo_interface.cpp.o -c /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/eo_interface.cpp

CMakeFiles/ImageTracking.dir/eo_interface.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/ImageTracking.dir/eo_interface.cpp.i"
	/usr/bin/aarch64-linux-gnu-g++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/eo_interface.cpp > CMakeFiles/ImageTracking.dir/eo_interface.cpp.i

CMakeFiles/ImageTracking.dir/eo_interface.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/ImageTracking.dir/eo_interface.cpp.s"
	/usr/bin/aarch64-linux-gnu-g++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/eo_interface.cpp -o CMakeFiles/ImageTracking.dir/eo_interface.cpp.s

CMakeFiles/ImageTracking.dir/eo_interface.cpp.o.requires:

.PHONY : CMakeFiles/ImageTracking.dir/eo_interface.cpp.o.requires

CMakeFiles/ImageTracking.dir/eo_interface.cpp.o.provides: CMakeFiles/ImageTracking.dir/eo_interface.cpp.o.requires
	$(MAKE) -f CMakeFiles/ImageTracking.dir/build.make CMakeFiles/ImageTracking.dir/eo_interface.cpp.o.provides.build
.PHONY : CMakeFiles/ImageTracking.dir/eo_interface.cpp.o.provides

CMakeFiles/ImageTracking.dir/eo_interface.cpp.o.provides.build: CMakeFiles/ImageTracking.dir/eo_interface.cpp.o


# Object files for target ImageTracking
ImageTracking_OBJECTS = \
"CMakeFiles/ImageTracking.dir/main.cpp.o" \
"CMakeFiles/ImageTracking.dir/eo_interface.cpp.o"

# External object files for target ImageTracking
ImageTracking_EXTERNAL_OBJECTS =

ImageTracking.out: CMakeFiles/ImageTracking.dir/main.cpp.o
ImageTracking.out: CMakeFiles/ImageTracking.dir/eo_interface.cpp.o
ImageTracking.out: CMakeFiles/ImageTracking.dir/build.make
ImageTracking.out: CMakeFiles/ImageTracking.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Linking CXX executable ImageTracking.out"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/ImageTracking.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/ImageTracking.dir/build: ImageTracking.out

.PHONY : CMakeFiles/ImageTracking.dir/build

CMakeFiles/ImageTracking.dir/requires: CMakeFiles/ImageTracking.dir/main.cpp.o.requires
CMakeFiles/ImageTracking.dir/requires: CMakeFiles/ImageTracking.dir/eo_interface.cpp.o.requires

.PHONY : CMakeFiles/ImageTracking.dir/requires

CMakeFiles/ImageTracking.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/ImageTracking.dir/cmake_clean.cmake
.PHONY : CMakeFiles/ImageTracking.dir/clean

CMakeFiles/ImageTracking.dir/depend:
	cd /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/build /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/build /mnt/c/Users/cbrommer/source/repos/MiniStrike_ImageTracking/build/CMakeFiles/ImageTracking.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/ImageTracking.dir/depend


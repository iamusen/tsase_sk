cmake_minimum_required(VERSION 3.15)
project(tsase LANGUAGES Fortran)

if(NOT CMAKE_Fortran_COMPILER)
    message(FATAL_ERROR "No Fortran compiler found. Please install a Fortran compiler (e.g., gfortran).")
endif()

add_library(al_ SHARED
    tsase/calculators/al/code/sumembforce.f
    tsase/calculators/al/code/potinit.f
    tsase/calculators/al/code/gagafeDblexp.f
    tsase/calculators/al/code/forces.f
    tsase/calculators/al/code/fofrhoDblexp.f
    tsase/calculators/al/code/embedenergy.f
    tsase/calculators/al/code/dfrhoDblexp.f
)
target_include_directories(al_ PUBLIC tsase/calculators/al/code/commonblks)

add_library(lepspho_ SHARED
    tsase/calculators/lepspho/code/lepspho.f
)

add_library(lj_ SHARED
    tsase/calculators/lj/code/lj.f
)

add_library(morse_ SHARED
    tsase/calculators/morse/code/morse.f
)

install(TARGETS al_ lepspho_ lj_ morse_
    LIBRARY DESTINATION lib
)

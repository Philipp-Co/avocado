cmake_minimum_required(VERSION 3.15)

project(avocado
    VERSION 0.0.0
    DESCRIPTION "Native compression core for the avocado package"
    LANGUAGES C)

# --- Standard & globale Einstellungen ------------------------------------
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# compile_commands.json fuer clangd / VIM-LSP erzeugen (im Build-Ordner).
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Position Independent Code ist fuer Shared Libraries Pflicht.
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# --- Build-Typ --------------------------------------------------------------
# Ohne explizite Angabe (-DCMAKE_BUILD_TYPE=...) auf Release bauen.
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# GNU/Clang setzen fuer Release standardmaessig "-O3 -DNDEBUG"; hier auf
# -O2 ueberschreiben.
set(CMAKE_C_FLAGS_RELEASE "-O2 -DNDEBUG")

# --- Link-Time-Optimization ---------------------------------------------
include(CheckIPOSupported)
check_ipo_supported(RESULT AVOCADO_IPO_SUPPORTED OUTPUT AVOCADO_IPO_ERROR)

# --- Wohin wird gebaut ----------------------------------------------------
# Default: direkt in das Python-Package, damit ctypes die Lib per
# relativem Pfad findet. Ueberschreibbar per -DAVOCADO_LIB_OUTPUT_DIR=...
set(AVOCADO_LIB_OUTPUT_DIR
    "${CMAKE_CURRENT_SOURCE_DIR}/../src/avocado/_native/lib"
    CACHE PATH "Zielverzeichnis fuer die gebaute Shared Library")

# --- Quellen --------------------------------------------------------------
# GLOB mit CONFIGURE_DEPENDS: neue .c-Dateien werden beim naechsten Build
# automatisch erkannt. Fuer maximale Reproduzierbarkeit stattdessen die
# Dateien explizit auflisten.
file(GLOB AVOCADO_SOURCES CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/src/*.c")

# --- Target ---------------------------------------------------------------
add_library(avocado SHARED ${AVOCADO_SOURCES})

# libavocado.dylib (macOS) / libavocado.so (Linux) / avocado.dll (Windows)
set_target_properties(avocado PROPERTIES
    OUTPUT_NAME "avocado"
    LIBRARY_OUTPUT_DIRECTORY "${AVOCADO_LIB_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY "${AVOCADO_LIB_OUTPUT_DIR}")  # Windows-DLL

# Header: <avocado/...> aufloesbar; PUBLIC, damit auch Consumer sie sehen.
target_include_directories(avocado PUBLIC
    "${CMAKE_CURRENT_SOURCE_DIR}/include")

if(AVOCADO_IPO_SUPPORTED)
    set_target_properties(avocado PROPERTIES INTERPROCEDURAL_OPTIMIZATION TRUE)
else()
    message(WARNING "LTO nicht unterstuetzt: ${AVOCADO_IPO_ERROR}")
endif()

# --- Debug-Symbole ----------------------------------------------------------
# Im Release-Build Debug-Symbole aus der Lib entfernen. "-S" (GNU ld & Apple
# ld64) strippt nur Debug-Infos und laesst die Export-Symboltabelle intakt,
# die ctypes zum Aufloesen der Funktionen braucht.
if(NOT MSVC)
    target_link_options(avocado PRIVATE
        $<$<CONFIG:Release>:-Wl,-S>)
endif()

# --- Dead-Code Stripping -----------------------------------------------
# Jede Funktion/jedes Datum in eigener Section, damit der Linker
# ungenutzten Code beim Linken vollstaendig entfernen kann.
if(NOT MSVC)
    target_compile_options(avocado PRIVATE -ffunction-sections -fdata-sections)

    if(APPLE)
        target_link_options(avocado PRIVATE -Wl,-dead_strip)
    else()
        target_link_options(avocado PRIVATE -Wl,--gc-sections)
    endif()
endif()

# --- Sichtbarkeit --------------------------------------------------------
# Standardmaessig alle Symbole verstecken; nur die API in compress.h wird
# ueber das AVOCADO_API-Makro explizit exportiert.
if(NOT MSVC)
    target_compile_options(avocado PRIVATE -fvisibility=hidden)
endif()

target_compile_definitions(avocado PRIVATE AVOCADO_BUILD_DLL)

# --- Warnungen ------------------------------------------------------------
if(MSVC)
    target_compile_options(avocado PRIVATE /W4)
else()
    target_compile_options(avocado PRIVATE
        -Wall -Wextra -Wpedantic -Wconversion)
endif()

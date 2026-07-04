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

# --- Warnungen ------------------------------------------------------------
if(MSVC)
    target_compile_options(avocado PRIVATE /W4)
else()
    target_compile_options(avocado PRIVATE
        -Wall -Wextra -Wpedantic -Wconversion)
endif()

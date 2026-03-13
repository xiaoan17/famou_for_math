#!/bin/bash
# compile.sh - Compile the neutron diffusion paper
# Usage: cd paper/ && bash compile.sh

set -e

# Find a LaTeX engine
if command -v pdflatex &>/dev/null; then
    ENGINE="pdflatex"
elif command -v tectonic &>/dev/null; then
    ENGINE="tectonic"
elif [ -x /tmp/tectonic ]; then
    ENGINE="/tmp/tectonic"
else
    echo "ERROR: No LaTeX engine found. Install one of:"
    echo "  brew install --cask basictex   (then restart terminal)"
    echo "  brew install tectonic"
    exit 1
fi

echo "Using LaTeX engine: $ENGINE"

if [ "$ENGINE" = "tectonic" ] || [ "$ENGINE" = "/tmp/tectonic" ]; then
    $ENGINE main.tex
else
    $ENGINE -interaction=nonstopmode main.tex
    bibtex main
    $ENGINE -interaction=nonstopmode main.tex
    $ENGINE -interaction=nonstopmode main.tex
fi

if [ -f main.pdf ]; then
    echo "SUCCESS: main.pdf generated ($(du -h main.pdf | cut -f1))"
else
    echo "FAILED: main.pdf not generated"
    exit 1
fi

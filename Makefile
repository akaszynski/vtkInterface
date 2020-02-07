# Simple makefile to simplify repetitive build env management tasks under posix

CODESPELL_DIRS ?= pyvista/ examples/ tests/
CODESPELL_SKIP ?= "*.pyc,*.txt,*.gif,*.png,*.jpg,*.ply,*.vtk,*.vti,*.js,*.html,*.doctree,*.ttf,*.woff,*.woff2,*.eot,*.mp4,*.inv,*.pickle,*.ipynb"
CODESPELL_IGNORE ?= "ignore_words.txt"

all: doctest

doctest: codespell pydocstyle

codespell:
	@echo "Running codespell"
	@codespell $(CODESPELL_DIRS) -S $(CODESPELL_SKIP) -I $(CODESPELL_IGNORE)

pydocstyle:
	@echo "Running pydocstyle"
	@pydocstyle pyvista

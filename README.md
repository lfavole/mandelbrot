# Mandelbrot set

Paint the Mandelbrot set or a fractal, with the color theme that you want.

## Building

	python -m install -e .
	python -m build
	twine check dist/*
	twine upload dist/*

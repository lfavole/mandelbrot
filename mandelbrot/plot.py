"""
Display the Mandelbrot set as a scatter plot with Matplotlib.
"""
import argparse
import os
from typing import Literal
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.markers import MarkerStyle
from PIL import Image

warnings.filterwarnings("ignore")

def complex_matrix(xmin, xmax, ymin, ymax, pixel_density):
    """
    Return the complex matrix that will be painted.
    """
    real = np.linspace(xmin, xmax, int((xmax - xmin) * pixel_density))
    imag = np.linspace(ymin, ymax, int((ymax - ymin) * pixel_density))
    return real[np.newaxis, :] + imag[:, np.newaxis] * 1j


def is_stable(comp, num_iterations):
    """
    Is a pixel stable ?
    """
    z_val = 0
    for _ in range(num_iterations):
        z_val = z_val ** 2 + comp
    return abs(z_val) <= 2


def get_members(comp, num_iterations):
    """
    Return the list of points that belong to the Mandelbrot set.
    """
    mask = is_stable(comp, num_iterations)
    return comp[mask]

def plot(
    paint_type: Literal["dots", "normal"] = "dots",
    pixel_density: int = 21,
    path: Path | str | None = None,
    show_image = False,
):
    matrix = complex_matrix(-2, 0.5, -1.5, 1.5, pixel_density = pixel_density)

    if paint_type == "dots":
        members = get_members(matrix, num_iterations = 20)
        plt.scatter(members.real, members.imag, color = "black", marker = MarkerStyle(","), s = 1)
    else:
        plt.imshow(is_stable(matrix, num_iterations = 20), cmap = "binary")

    plt.gca().set_aspect("equal")
    plt.axis("off")
    plt.tight_layout()

    if path is not None:
        plt.savefig(path, dpi = 300, backend = "agg")

    if show_image:
        if not path:
            plt.show()
        else:
            os.startfile(path)

    if path is None:
        path = "plot_tmp.jpg"
        plt.savefig(path, dpi = 300, backend = "agg")
        ret = Image.open(path)
        os.remove(path)
        return ret
    return None

def main():
    parser = argparse.ArgumentParser(description = __doc__)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--no-show", action = "store_false", dest = "show", help = "don't show the result in a window")
    group.add_argument("--no-save", action = "store_false", dest = "save", help = "don't save the image")

    parser.add_argument("--name", default = "mandelbrot_%(pixel_density)d.jpg", help = "name of the output file")
    parser.add_argument("--pixel-density", type = int, help = "pixel density of the image")
    parser.add_argument("--type", choices = ("dots", "normal"), default = "dots", help = "painting type")
    parser.add_argument("--max-iterations", type = int, help = "maximum number of iterations for a pixel")

    opts = parser.parse_args()

    if not opts.max_iterations:
        if opts.type == "dots":
            opts.max_iterations = 20
        else:
            opts.max_iterations = 100

    if not opts.pixel_density:
        if opts.type == "dots":
            opts.pixel_density = 21
        else:
            opts.pixel_density = 512

    filename = opts.name % {
        "pixel_density": opts.pixel_density
    }

    plot(
        paint_type = opts.type,
        pixel_density = opts.pixel_density,
        path = filename,
        show_image = opts.show,
    )

if __name__ == "__main__":
	main()

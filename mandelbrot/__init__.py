"""
Paint the Mandelbrot set.
"""
import argparse
import os
import sys
import time
from pathlib import Path
from typing import Callable, Literal

from PIL import Image, ImageEnhance

from .mandelbrot_set import Fractal, JuliaSet, MandelbrotSet
from .viewport import Viewport


class Palette:
    """
    A palette to paint the Mandelbrot set.
    """
    def __init__(
        self,
        colors: str | list[str] | list[tuple[int, int, int]],
        num_colors = 1024,
        function: Callable[[float], float] | Literal["square", "sqrt"] = lambda x: x,
        name = "",
    ):
        self.name = name
        if isinstance(colors, str):
            if "," not in colors:
                self.name = colors
                colors = getattr(self, colors)().colors
            else:
                colors = colors.split(",")
        colors = [
            tuple(int(x) for x in color.split("."))
            if isinstance(color, str) else color
            for color in colors
        ]
        self.colors = colors
        self.num_colors = num_colors
        if isinstance(function, str):
            self.function = {
                "square": lambda x: x ** 2,
                "sqrt": lambda x: x ** 0.25,
            }[function]
        else:
            self.function = function

        self.palette = []
        self._make_gradient()

    def _make_gradient(self):
        f = self.function
        for color_n in range(self.num_colors):
            index_f = f(color_n) / f(self.num_colors) * (len(self.colors) - 1)
            index = int(index_f)
            after = index_f % 1
            before = 1 - after
            self.palette.append(tuple(
                int(self.colors[index][x] * before + self.colors[index + 1][x] * after)
                for x in (0, 1, 2)
            ))

    def __iter__(self):
        yield from self.palette

    @classmethod
    def black_white(cls, *args, **kwargs):
        """
        Black and white palette.
        """
        return cls(
            [(0, 0, 0), (255, 255, 255)],
            *args,
            name = "black_white",
            **kwargs,
        )

    @classmethod
    def blue(cls, *args, **kwargs):
        """
        Blue palette.
        """
        return cls(
            [(0, 0, 0), (0, 120, 255), (25, 178, 255), (127, 247, 255), (255, 255, 255), (255, 224, 96), (208, 80, 0)],
            *args,
            name = "blue",
            **kwargs,
        )

    @classmethod
    def gold(cls, *args, **kwargs):
        """
        Gold palette.
        """
        return cls(
            [
                (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255),
                (127, 247, 255), (25, 178, 255), (0, 120, 255), (255, 224, 96), (208, 80, 0),
            ],
            *args,
            function = "sqrt",
            name = "gold",
            **kwargs,
        )

def paint(mandelbrot_set: Fractal, viewport: Viewport, palette: Palette | list[tuple[int, int, int]], smooth = True):
    """
    Paint the Mandelbrot set (add the pixels on the image).
    """
    if isinstance(palette, Palette):
        palette = list(palette)
    length = len(palette)
    length_1 = length - 1
    for pixel in viewport:
        stability = mandelbrot_set.stability(complex(pixel), smooth)
        pixel.color = palette[int(stability * length_1)] if stability != 1 else (0, 0, 0)

def show(
    center: complex = -0.75,
    width: float = 3.5,
    max_iterations = 100,
    escape_radius: float = 2,
    fractal: str = "mandelbrot",
    start: complex = 0j,
    parameter: complex = 0j,
    power: complex = 2,
    path: Path | str | None = None,
    palette: Palette = Palette.gold(),
    image_width = 512,
    image_height = 512,
    brightness: float = 1,
    show_image = False,
	progress = True,
):
    """
    Create and paint the Mandelbrot set and save the image.
    """
    print("This might take a while...")

    start_time = time.perf_counter()

    if fractal == "mandelbrot":
        mandelbrot_set = MandelbrotSet(max_iterations, escape_radius, power = power, start = start)
    else:
        mandelbrot_set = JuliaSet(max_iterations, escape_radius, parameter = parameter, power = power)

    image = Image.new(mode = "RGB", size = (image_width, image_height))
    viewport = Viewport(image, center = center, width = width, progress = progress)

    paint(mandelbrot_set, viewport, palette)

    if brightness != 1:
        image = ImageEnhance.Brightness(image).enhance(brightness)

    end_time = time.perf_counter()
    print(f"time = {end_time - start_time}s")

    if path is not None:
        image.save(path)

    if show_image:
        if not path:
            image.show()
        else:
            os.startfile(path)

    if path is None:
        return image
    return None

def show_palette(
    palette,
    image_width = 512,
    image_height = 512,
    path: Path | str | None = None,
    show_image = True,
):
    """
    Show a palette (for debugging).
    """
    palette = list(palette)
    image = Image.new(mode = "RGB", size = (image_width, image_height))
    len_1 = len(palette) - 1
    for x_pos in range(image_width):
        color = palette[int(x_pos / image_width * len_1)]
        for y_pos in range(image_height):
            image.putpixel((x_pos, y_pos), color)

    if path is not None:
        image.save(path)

    if show_image:
        if not path:
            image.show()
        else:
            os.startfile(path)

    if path is None:
        return image
    return None

class ComplexWithC(complex):
    """
    Complex number that starts with `c:` (for argparse).
    """
    def __new__(cls, real: str | float, imag: float = 0):
        if isinstance(real, str):
            if real.startswith("c:"):
                return complex(real.removeprefix("c:"))
            return complex(real)
        return complex(real, imag)

def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument("--fractal", type = str, default = "mandelbrot", help = "fractal type")
    parser.add_argument("--start", type = complex, default = 0, help = "first value of the formula (for the Mandelbrot set)")
    parser.add_argument("--parameter", type = complex, default = 0, help = "parameter in the formula (for Julia sets)")
    parser.add_argument("--power", type = complex, default = 2, help = "power in the formula")
    parser.add_argument("--center", type = ComplexWithC, help = "center of the painting")
    parser.add_argument("--width", type = float, help = "width of the painting")
    parser.add_argument("--max-iterations", type = int, default = 100, help = "maximum number of iterations for a pixel")
    parser.add_argument("--escape-radius", type = float, default = 2, help = "escape radius for a pixel")
    parser.add_argument("--image-width", type = int, default = 512, help = "width of the image")
    parser.add_argument("--image-height", type = int, default = 512, help = "height of the image")
    parser.add_argument("--palette", type = Palette, default = Palette.gold(), help = "palette to use")
    parser.add_argument("--name", type = str, default = "%(fractal)s_%(image_width)dx%(image_height)d_%(palette)s.jpg", help = "name of the output file")
    parser.add_argument("--show-palette", action = "store_true", help = "show the palette")
    parser.add_argument("--no-progress", action = "store_false", dest = "progress", help = "don't output a progress bar")
    parser.add_argument("--no-show", action = "store_false", dest = "show", help = "don't show the result in a window")

    opts = parser.parse_args()

    filename = opts.name % {
        "fractal": "palette" if opts.show_palette else opts.fractal,
        "image_width": opts.image_width,
        "image_height": opts.image_height,
        "palette": opts.palette.name or "other",
    }

    if opts.show_palette:
        show_palette(
            opts.palette,
            image_width = opts.image_width,
            image_height = opts.image_height,
            path = filename,
        )
        sys.exit()

    if opts.center is None:
        if opts.fractal == "mandelbrot":
            opts.center = -0.75
        else:
            opts.center = 0

    if opts.width is None:
        if opts.fractal == "mandelbrot":
            opts.width = 3
        else:
            opts.width = 2.25

    show(
        fractal = opts.fractal,
        start = opts.start,
        parameter = opts.parameter,
        power = opts.power,
        center = opts.center,
        width = opts.width,
        max_iterations = opts.max_iterations,
        escape_radius = opts.escape_radius,
        path = filename,
        palette = opts.palette,
        image_width = opts.image_width,
        image_height = opts.image_height,
        show_image = opts.show,
		progress = opts.progress,
    )

if __name__ == "__main__":
	main()

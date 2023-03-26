# mandelbrot_03.py

from __future__ import annotations  # Union type syntax

from dataclasses import dataclass
from math import log
from typing import Callable, Iterator


def default(comp: complex):
    """
    Placeholder function for `Fractal` class.
    """
    while True:
        yield comp

def mandelbrot(power: complex = 2, start: complex = 0j):
    """
    A specific Mandelbrot set with a power.
    """
    def wrapper(comp: complex):
        """
        Real function.
        """
        z = start
        while True:
            yield z
            z = z ** power + comp
    return wrapper

def julia(comp: complex, power: complex = 2):
    """
    A specific Julia set with start and power.
    """
    def wrapper(z_value: complex):
        """
        Real function.
        """
        while True:
            yield z_value
            z_value = z_value ** power + comp
    return wrapper

@dataclass
class Fractal:
    """
    A fractal.
    """
    max_iterations: int
    escape_radius: float = 2.0
    sequence: Callable[[complex], Iterator[complex]] = default

    def __contains__(self, candidate: complex) -> bool:
        return self.stability(candidate) == 1

    def stability(self, candidate: complex, smooth = False, clamp = True) -> float:
        """
        The stability of a pixel (1 = the pixel belongs to the set).
        """
        value = self.escape_count(candidate, smooth) / self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def escape_count(self, candidate: complex, smooth = False) -> int | float:
        seq = self.sequence(candidate)
        for iteration in range(self.max_iterations):
            z = next(seq)
            if abs(z) > self.escape_radius:
                if smooth:
                    return iteration + 1 - log(log(abs(z))) / log(2)
                return iteration
        return self.max_iterations

@dataclass
class MandelbrotSet(Fractal):
    """
    The Mandelbrot set.
    """
    power: complex = 2
    start: complex = 0j
    def __post_init__(self):
        self.sequence = mandelbrot(self.power, self.start)

@dataclass
class JuliaSet(Fractal):
    """
    A Julia set with a parameter (the value added after each iteration).
    """
    parameter: complex = 0
    power: complex = 2
    def __post_init__(self):
        self.sequence = julia(self.parameter, self.power)

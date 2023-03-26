# viewport.py

from dataclasses import dataclass

from PIL import Image
from tqdm import tqdm


@dataclass
class Viewport:
    """
    A viewport (a zone of a fractal).
    """
    image: Image.Image
    center: complex
    width: float
    progress: bool = False

    @property
    def height(self):
        """
        Height of the viewport in pixels.
        """
        return self.scale * self.image.height

    @property
    def offset(self):
        """
        Position at the top-left of the viewport.
        """
        return self.center + complex(-self.width, self.height) / 2

    @property
    def scale(self):
        """
        Scale of the viewport.
        """
        return self.width / self.image.width

    def __iter__(self):
        if self.progress:
            pbar = tqdm(total = len(self))
            for y_pos in range(self.image.height):
                for x_pos in range(self.image.width):
                    yield Pixel(self, x_pos, y_pos)
                    pbar.update(1)
        else:
            for y_pos in range(self.image.height):
                for x_pos in range(self.image.width):
                    yield Pixel(self, x_pos, y_pos)

    def __len__(self):
        return self.image.width * self.image.height


@dataclass
class Pixel:
    """
    A pixel in a viewport.
    """
    viewport: Viewport
    x_pos: int
    y_pos: int

    @property
    def color(self):
        """
        The color of the pixel.
        """
        return self.viewport.image.getpixel((self.x_pos, self.y_pos))

    @color.setter
    def color(self, value):
        self.viewport.image.putpixel((self.x_pos, self.y_pos), value)

    def __complex__(self):
        return (
            complex(self.x_pos, -self.y_pos) * self.viewport.scale
            + self.viewport.offset
        )

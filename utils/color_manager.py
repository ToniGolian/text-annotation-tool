from typing import List

from input_output.file_handler import FileHandler


class ColorManager:
    """
    Generates color schemes for tag-based applications using predefined color palettes.
    """

    def __init__(self, file_handler: FileHandler):
        """
        Initializes the generator with a file handler.

        Args:
            file_handler: An object that provides read_file and write methods.
        """
        self._file_handler = file_handler

    def _is_dark(self, hex_color: str) -> bool:
        """
        Determines if a color is dark based on perceived luminance.

        Args:
            hex_color (str): A hex color string like '#RRGGBB'.

        Returns:
            bool: True if color is dark, False if light.
        """
        hex_color = hex_color.lstrip("#")
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance < 128

    def create_color_scheme(self, tag_keys: List[str], colorset_name: str) -> None:
        """
        Creates and stores a color scheme for a given project and color set.

        Args:
            tag_keys (List[str]): A list of tag type strings.
            colorset_name (str): The name of the color palette to use.
            project (str): The name of the project.
        """
        color_sets = self._file_handler.read_file("color_sets")
        palette = color_sets.get(colorset_name)

        if not palette:
            raise ValueError(f"Color set '{colorset_name}' not found.")

        full_keys = tag_keys + ["search", "current_search"]
        color_scheme = {}

        palette_size = len(palette)
        num_keys = len(full_keys)
        step = max(palette_size // num_keys, 1)

        for idx, key in enumerate(full_keys):
            color_index = (idx * step) % palette_size
            background = palette[color_index]
            font = "#ffffff" if self._is_dark(background) else "#000000"
            color_scheme[key] = {
                "background_color": background,
                "font_color": font
            }

        # Wrap into outer dictionary
        output = {
            "tags": {key: color_scheme[key] for key in tag_keys},
            "search": color_scheme["search"],
            "current_search": color_scheme["current_search"]
        }

        filename = f"{colorset_name}_color_scheme.json"
        self._file_handler.write_file(
            "project_color_scheme_folder", output, filename)

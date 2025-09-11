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

    def _invert_color(self, hex_color: str) -> str:
        """
        Calculates an inverted (complementary) color.

        Args:
            hex_color (str): A hex color string.

        Returns:
            str: The inverted hex color.
        """
        hex_color = hex_color.lstrip("#")
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        return "#{:02x}{:02x}{:02x}".format(255 - r, 255 - g, 255 - b)

    def _brighten_color(self, hex_color: str, factor: float = 1.2) -> str:
        """
        Brightens a hex color by scaling its RGB values.

        Args:
            hex_color (str): Original hex color.
            factor (float): Brightening factor.

        Returns:
            str: Brightened hex color.
        """
        hex_color = hex_color.lstrip("#")
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        r = min(int(r * factor), 255)
        g = min(int(g * factor), 255)
        b = min(int(b * factor), 255)
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def create_color_scheme(self, tag_keys: List[str], colorset_name: str, complementary_search_color: bool) -> None:
        """
        Creates and stores a color scheme for a given project and color set.

        Args:
            tag_keys (List[str]): A list of tag type strings.
            colorset_name (str): The name of the color palette to use.
            complementary_search_color (bool): Whether to use a contrasting color for search highlights.
        """
        color_sets = self._file_handler.read_file("color_sets")
        palette = color_sets.get(colorset_name)

        if not palette:
            raise ValueError(f"Color set '{colorset_name}' not found.")

        color_scheme = {}

        palette_size = len(palette)
        num_tags = len(tag_keys)
        step = max(palette_size // num_tags, 1)

        # Distribute tag colors over the full palette
        for idx, key in enumerate(tag_keys):
            color_index = (idx * step) % palette_size
            background = palette[color_index]
            font = "#ffffff" if self._is_dark(background) else "#000000"
            color_scheme[key] = {
                "background_color": background,
                "font_color": font
            }

        if complementary_search_color:
            # Use average tag color as base for complementary
            avg_idx = (palette_size // 3)  # pick a mid-range tag color
            base_color = palette[avg_idx]
            inverted = self._invert_color(base_color)
            current = self._brighten_color(inverted, factor=1.2)

            search_font = "#ffffff" if self._is_dark(inverted) else "#000000"
            current_font = "#ffffff" if self._is_dark(current) else "#000000"

            color_scheme["search"] = {
                "background_color": inverted,
                "font_color": search_font
            }

            color_scheme["current_search"] = {
                "background_color": current,
                "font_color": current_font
            }
        else:
            # Distribute over full list
            full_keys = tag_keys + ["search", "current_search"]
            num_keys = len(full_keys)
            step = max(palette_size // num_keys, 1)
            for i, key in enumerate(["search", "current_search"]):
                idx = (num_tags + i) * step % palette_size
                background = palette[idx]
                font = "#ffffff" if self._is_dark(background) else "#000000"
                color_scheme[key] = {
                    "background_color": background,
                    "font_color": font
                }

        # Build output dictionary
        output = {
            "tags": {key: color_scheme[key] for key in tag_keys},
            "search": color_scheme["search"],
            "current_search": color_scheme["current_search"]
        }

        suffix = "_comp_search" if complementary_search_color else ""
        file_name = f"{colorset_name}{suffix}_color_scheme.json"
        self._file_handler.write_file(
            "project_color_scheme_directory", output, file_name)

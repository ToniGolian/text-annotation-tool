"""
text-annotation-tool

A lightweight text annotation tool for annotating spans of text with custom tags and attributes.

Author: Toni Golian
License: MIT
"""
from utils.app_builder import AppBuilder


def main():
    appbuilder = AppBuilder()
    app = appbuilder.build_app()
    app.mainloop()


# Entrypoint
if __name__ == "__main__":
    main()

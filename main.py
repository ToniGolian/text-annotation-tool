from utils.app_builder import AppBuilder


def main():
    appbuilder = AppBuilder()
    app = appbuilder.build_app()
    app.mainloop()


# Entrypoint
if __name__ == "__main__":
    main()

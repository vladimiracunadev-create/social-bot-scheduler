from .service import BotService


def main():
    """
    Función principal de arranque.
    Instantia el servicio y le cede el control.
    """
    service = BotService()
    service.run()


if __name__ == "__main__":
    main()

from wireup import initialize_container, create_container

from app.core.database import Database
from app import repositories, services
from configs.settings import Settings


def init_dependencies() -> None:
    container = create_container()
    container.register(Settings)
    container.register(Database)
    initialize_container(container, service_modules=[repositories, services])

    return container


container = init_dependencies()

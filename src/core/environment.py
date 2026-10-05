# src/core/environment.py
import os
import abc

class EnvironmentStrategy(abc.ABC):
    @abc.abstractmethod
    def get_max_memory(self) -> str:
        pass

class DockerEnvironment(EnvironmentStrategy):
    def get_max_memory(self) -> str:
        return "28MB"

class LocalEnvironment(EnvironmentStrategy):
    def get_max_memory(self) -> str:
        return "200MB"

class EnvironmentFactory:
    @staticmethod
    def get_strategy() -> EnvironmentStrategy:
        is_docker = os.environ.get("DOCKER_ENV", "false").lower() == "true"
        return DockerEnvironment() if is_docker else LocalEnvironment()
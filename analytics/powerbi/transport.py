"""Transportes para alcanzar el motor de un caso, y el guardia de solo lectura.

Restricciones de diseño de este módulo:

* **Solo lectura por construcción.** Toda sentencia que envía un adaptador pasa
  primero por :func:`assert_read_only`. Una sentencia que no sea un único
  ``SELECT`` (o un ``WITH`` que termine en uno) se rechaza antes de llegar al
  motor.
* **Sin dependencias nuevas en tiempo de ejecución.** El laboratorio es
  Docker-first, así que el transporte por defecto ejecuta el cliente que ya
  viene dentro del contenedor de cada caso (``docker exec``). Un adaptador
  puede ofrecer un transporte directo más rápido cuando la librería cliente o
  el puerto publicado estén disponibles.
* **Volumen acotado.** Las consultas siempre las pagina quien llama; aquí solo
  se impone un tiempo límite para que una consulta desbocada no cuelgue la
  exportación.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field

# Segundos que puede tardar una consulta antes de abortarse.
DEFAULT_TIMEOUT = 120

_FORBIDDEN_KEYWORD = re.compile(
    r"\b("
    r"alter|attach|call|comment|copy|create|delete|detach|drop|exec|execute|"
    r"grant|insert|into|merge|optimize|rename|replace|revoke|set|truncate|"
    r"update|upsert|vacuum"
    r")\b",
    re.IGNORECASE,
)

_LEADING_KEYWORD = re.compile(r"^\s*(select|with)\b", re.IGNORECASE)


class ReadOnlyViolation(ValueError):
    """Se lanza cuando una sentencia no es una lectura pura."""


class TransportError(RuntimeError):
    """Se lanza cuando no se pudo alcanzar el motor o este respondió con error."""


def assert_read_only(statement: str) -> str:
    """Valida que ``statement`` sea una única consulta de solo lectura.

    Devuelve la sentencia normalizada (sin punto y coma final) para que quien
    llama pueda pasar el resultado directo al cliente.
    """
    text = statement.strip().rstrip(";").strip()
    if not text:
        raise ReadOnlyViolation("sentencia vacía")
    if ";" in text:
        raise ReadOnlyViolation("no se permiten varias sentencias")
    if not _LEADING_KEYWORD.match(text):
        raise ReadOnlyViolation("la sentencia debe empezar por SELECT o WITH")
    found = _FORBIDDEN_KEYWORD.search(text)
    if found:
        raise ReadOnlyViolation(
            f"palabra clave prohibida en una consulta de lectura: {found.group(1)!r}"
        )
    return text


@dataclass
class CommandResult:
    """Resultado de un comando externo."""

    returncode: int
    stdout: str
    stderr: str


@dataclass
class CommandRunner:
    """Envoltorio fino y sustituible en pruebas sobre :mod:`subprocess`."""

    timeout: int = DEFAULT_TIMEOUT

    def run(self, argv: list[str], env: dict[str, str] | None = None) -> CommandResult:
        try:
            completed = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env,
                check=False,
            )
        except FileNotFoundError as exc:  # pragma: no cover - problema de entorno
            raise TransportError(f"comando no encontrado: {argv[0]}") from exc
        except subprocess.TimeoutExpired as exc:
            raise TransportError(
                f"el comando excedió {self.timeout}s: {' '.join(argv[:3])}"
            ) from exc
        return CommandResult(completed.returncode, completed.stdout, completed.stderr)


@dataclass
class DockerExecTransport:
    """Ejecuta un cliente dentro del contenedor de un caso.

    Los valores de ``env`` se pasan con ``docker exec -e NOMBRE`` **sin valor**:
    esa forma le dice a Docker que tome el valor del entorno del proceso
    cliente. El secreto viaja entonces por el entorno del ``docker`` que se
    lanza y nunca aparece en ``argv``, así que no queda visible en la tabla de
    procesos del anfitrión —cosa que sí ocurriría tanto con un argumento
    ``--password`` como con ``-e NOMBRE=valor``.
    """

    container: str
    runner: CommandRunner = field(default_factory=CommandRunner)
    docker_binary: str = "docker"

    def available(self) -> bool:
        """``True`` cuando Docker está instalado y el contenedor está en marcha."""
        if shutil.which(self.docker_binary) is None:
            return False
        result = self.runner.run(
            [
                self.docker_binary,
                "ps",
                "--filter",
                f"name=^{self.container}$",
                "--format",
                "{{.Names}}",
            ]
        )
        return result.returncode == 0 and self.container in result.stdout.split()

    def exec(self, argv: list[str], env: dict[str, str] | None = None) -> str:
        """Ejecuta ``argv`` dentro del contenedor y devuelve su salida estándar."""
        command = [self.docker_binary, "exec"]
        entorno: dict[str, str] | None = None
        if env:
            # -e NOMBRE (sin "=valor"): Docker copia el valor desde el entorno
            # de este proceso cliente, de modo que el secreto no entra en argv.
            for name in env:
                command += ["-e", name]
            entorno = {**os.environ, **env}
        command += [self.container, *argv]
        result = self.runner.run(command, entorno)
        if result.returncode != 0:
            raise TransportError(
                f"{self.container}: el cliente terminó con código "
                f"{result.returncode}: {result.stderr.strip()[:400]}"
            )
        return result.stdout


def require_container(container: str, transport: DockerExecTransport) -> None:
    """Lanza un error legible cuando el stack del caso no está levantado."""
    if not transport.available():
        raise TransportError(
            f"el contenedor {container!r} no está en marcha. Levanta primero el "
            f"caso, por ejemplo con 'docker compose --profile caseNN up -d'."
        )

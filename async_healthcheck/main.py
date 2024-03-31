"""A simple healthcheck server for Python asyncio applications."""
import asyncio
import logging
from http import HTTPStatus
from typing import List, Callable, Awaitable

logger = logging.getLogger("async_healthcheck")


class HealthCheckServer:
    """A simple healthcheck server."""
    def __init__(
        self,
        sync_callables: List[Callable[[], bool]] = None,
        async_callables: List[Callable[[], Awaitable[bool]]] = None,
        host: str = "127.0.0.1",
        path: str = "/healthcheck",
        port: int = 8000,
        success_code: int = 200,
        error_code: int = 500,
    ):
        if sync_callables is None:
            sync_callables = []
        if async_callables is None:
            async_callables = []
        self.sync_callables = sync_callables
        self.async_callables = async_callables
        self.healthcheck_path = path
        self.success_code = HTTPStatus(success_code)
        self.error_code = HTTPStatus(error_code)
        self.server = None
        self.host = host
        self.port = port

    async def handle_request(self, reader, writer):
        """Handle an incoming HTTP request."""
        request_line = await reader.readline()
        method, path, _ = request_line.decode().split()

        if method == "GET" and path == self.healthcheck_path:
            # Check all asynchronous callables
            for async_check in self.async_callables:
                if not await async_check():
                    self.send_response(writer, self.error_code)
                    return

            # Check all synchronous callables
            for sync_check in self.sync_callables:
                if not sync_check():
                    self.send_response(writer, self.error_code)
                    return

            self.send_response(writer, self.success_code)
        else:
            self.send_response(writer, HTTPStatus.NOT_FOUND)

    async def start(self):
        """Start the healthcheck server."""
        self.server = await asyncio.start_server(
            self.handle_request, self.host, self.port
        )
        logger.info(f"Healthcheck server started at http://{self.host}:{self.port}")

    async def cleanup(self):
        """Stop the healthcheck server."""
        self.server.close()
        await self.server.wait_closed()
        logger.info("Healthcheck server stopped.")

    def send_response(self, writer, status):
        """Send an HTTP response."""
        writer.write(f"HTTP/1.1 {status.value} {status.phrase}\r\n\r\n".encode())
        if status == self.success_code:
            logger.info(f"Healthcheck response: {status.value} {status.phrase}")
        else:
            logger.error(f"Healthcheck response: {status.value} {status.phrase}")
        writer.close()


async def start_healthcheck(
    sync_callables: List[Callable[[], bool]] = None,
    async_callables: List[Callable[[], Awaitable[bool]]] = None,
    host: str = "127.0.0.1",
    path: str = "/healthcheck",
    port: int = 8000,
    success_code: int = 200,
    error_code: int = 500,
):
    """Start the healthcheck server.
    :param sync_callables: A list of synchronous functions to check.
        The functions should return True if the check passes.
    :param async_callables: A list of asynchronous callables to check.
        The functions should return True if the check passes.
    :param host: The host to bind the healthcheck server to.
    :param path: The path to use for the healthcheck endpoint.
    :param port: The port to bind the healthcheck server to.
    :param success_code: The HTTP status code to return if all checks pass.
    :param error_code: The HTTP status code to return if any checks fail.
    """
    if sync_callables is None:
        sync_callables = []
    if async_callables is None:
        async_callables = []
    server = HealthCheckServer(
        sync_callables,
        async_callables,
        host,
        path,
        port,
        success_code,
        error_code,
    )
    await server.start()
    return server

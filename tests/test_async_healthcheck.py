import unittest
import logging
import http.client
import asyncio
from async_healthcheck import start_healthcheck

logging.basicConfig(level=logging.INFO)


class TestStartHealthCheck(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.sync_callable_true = self.sync_check_true
        self.async_callable_true = self.async_check_true
        self.sync_callable_false = self.sync_check_false
        self.async_callable_false = self.async_check_false
        self.server = None

    @staticmethod
    def sync_check_true():
        return True

    @staticmethod
    async def async_check_true():
        return True

    @staticmethod
    def sync_check_false():
        return False

    @staticmethod
    async def async_check_false():
        return False

    def make_request(self):
        conn = http.client.HTTPConnection("127.0.0.1", 8000)
        conn.request("GET", "/healthcheck")
        response = conn.getresponse()
        conn.close()
        return response

    async def test_healthcheck_success(self):
        self.server = await start_healthcheck(
            sync_callables=[self.sync_callable_true],
            async_callables=[self.async_callable_true],
        )
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, self.make_request)
        response = await future
        self.assertEqual(response.status, 200)

    async def test_healthcheck_success_default(self):
        self.server = await start_healthcheck()
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, self.make_request)
        response = await future
        self.assertEqual(response.status, 200)

    async def test_healthcheck_failure(self):
        self.server = await start_healthcheck(
            sync_callables=[self.sync_callable_false],
            async_callables=[self.async_callable_false],
        )
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, self.make_request)
        response = await future
        self.assertEqual(response.status, 500)

    async def asyncTearDown(self):
        if self.server:
            await self.server.cleanup()


if __name__ == "__main__":
    unittest.main()

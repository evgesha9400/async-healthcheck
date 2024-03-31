# async-healthcheck

`async-healthcheck` is a compact asynchronous health check library built using only the Python standard library. It provides a simple way to monitor the health of your application by checking the status of various synchronous and asynchronous functions.

## Installation

You can install `async-healthcheck` directly from PyPI:

```bash
pip install async-healthcheck
```

## Usage

Here is a basic usage example:

```python
from async_healthcheck import start_healthcheck

def sync_check():
    # Perform some synchronous health check (e.g., check database connection)
    return True

async def async_check():
    # Perform some asynchronous health check (e.g., check API availability)
    return True

async def main():
    server = await start_healthcheck(
        sync_callables=[sync_check],
        async_callables=[async_check],
        host="127.0.0.1",
        path="/healthcheck",
        port=8000,
    )
    # The server is now running and can be accessed at http://127.0.0.1:8000/healthcheck

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

In this example, `start_healthcheck` starts a health check server that runs the provided synchronous and asynchronous checks when a GET request is made to the specified path (default is `/healthcheck`). If all checks pass, it returns a 200 status code; if any check fails, it returns a 500 status code.

## Testing

Tests are located in the `tests` directory and can be run using the standard Python unittest module:

```bash
PYTHONPATH="async_healthcheck" poetry run python -m unittest discover -s tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
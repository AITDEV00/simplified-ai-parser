import socket
import uvicorn


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("localhost", port)) == 0


if __name__ == "__main__":
    port = 7656
    if not is_port_in_use(port):
        # workers=4: each worker is a separate process with its own GIL, enabling
        # true multi-core parallelism for CPU-bound parsing. asyncio.to_thread
        # handles concurrency within each worker. Lightweight service, ~100MB/worker.
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False, workers=4)
    else:
        print(f"Port {port} is already in use. Please free up the port and try again.")

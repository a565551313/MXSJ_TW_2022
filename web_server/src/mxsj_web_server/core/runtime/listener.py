"""Bounded threaded HTTP listeners; TLS belongs to an explicitly trusted proxy."""

from __future__ import annotations

import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import unquote, urlsplit


class BoundedServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    block_on_close = False
    request_queue_size = 16
    allow_reuse_address = True

    def __init__(self, address, handler, callback):
        self.callback = callback
        self.slots = threading.BoundedSemaphore(16)
        self.clients = set()
        self.clients_lock = threading.Lock()
        if ":" in address[0]:
            self.address_family = socket.AF_INET6
        super().__init__(address, handler)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        request.settimeout(3)
        with self.clients_lock:
            self.clients.add(request)
        try:
            super().process_request(request, client_address)
        except BaseException:
            with self.clients_lock:
                self.clients.discard(request)
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            with self.clients_lock:
                self.clients.discard(request)
            self.slots.release()

    def handle_error(self, request, client_address):
        # Never print a traceback or request headers to stderr.
        pass


class Handler(BaseHTTPRequestHandler):
    server_version = "MXSJWeb"
    sys_version = ""
    protocol_version = "HTTP/1.0"

    def log_message(self, format, *args):
        pass

    def do_GET(self):  # noqa: N802  # HTTP handler hook.
        self.dispatch()

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET
    do_OPTIONS = do_GET
    do_TRACE = do_GET

    def dispatch(self):
        try:
            if len(self.path) > 2048 or self.headers.get("Transfer-Encoding"):
                self.send_error(400)
                return
            lengths = self.headers.get_all("Content-Length", [])
            if len(lengths) > 1 or (lengths and not lengths[0].isdigit()):
                self.send_error(400)
                return
            size = int(lengths[0]) if lengths else 0
            if size > 1024 * 1024:
                self.send_error(413)
                return
            body = self.rfile.read(size) if size else b""
            if len(body) != size:
                self.send_error(400)
                return
            path = unquote(urlsplit(self.path).path)
            status, headers, response = self.server.callback(
                self.command, path, self.headers, body, self.client_address[0]
            )
            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            if status != 304:
                self.send_header("Content-Length", str(len(response)))
            self.send_header("Connection", "close")
            self.end_headers()
            if self.command != "HEAD" and status != 304:
                self.wfile.write(response)
        except (OSError, ValueError):
            self.close_connection = True


class Listener:
    def __init__(self, config, callback):
        self.server = BoundedServer((config["host"], config["port"]), Handler, callback)
        self.thread = threading.Thread(
            target=self.server.serve_forever, kwargs={"poll_interval": 0.1}, daemon=True
        )
        try:
            self.thread.start()
        except BaseException:
            self.server.server_close()
            raise

    def stop(self):
        self.server.shutdown()
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            with self.server.clients_lock:
                if not self.server.clients:
                    break
            time.sleep(0.05)
        with self.server.clients_lock:
            for connection in tuple(self.server.clients):
                try:
                    connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                connection.close()
        self.server.server_close()
        self.thread.join(timeout=2)

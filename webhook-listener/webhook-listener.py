#!/usr/bin/env python3
import atexit
import os
import tempfile
import subprocess
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 4000
PID_FILE = "/tmp/server.pid"

def write_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def remove_pid():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))

        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body.decode('utf-8'))
            self._process_webhook(payload)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')

        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()

    def _process_webhook(self, payload):
        event_type = self.headers.get('X-GitHub-Event', 'unknown')
        branch = payload.get('ref', '').replace('refs/heads/', '')

        if !branch.startswith("webhooks_devops_assignment"):
            return

        if event_type == 'push':
            deploy_ref = payload.get('head_commit', {}).get('id', 'NA')
            self._handle_push_event(payload, deploy_ref)
        else:
            print(f"   ℹ️  Событие '{event_type}' - базовое логирование")

    def _handle_push_event(self, payload, deploy_ref):
        branch = payload.get('ref', '').replace('refs/heads/', '')
        clone_url = payload.get('repository', {}).get('clone_url', 'unknown')

        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(
                ["git", "clone", clone_url, tmpdir],
                check=True
            )

            subprocess.run(
                ["git", "checkout", branch],
                cwd=tmpdir,
                check=True
            )

            env = os.environ.copy()
            env['DEPLOY_REF'] = deploy_ref

            subprocess.run(
                ["make", "build"],
                cwd=tmpdir,
                check=True,
                env=env
            )

            subprocess.run(
                ["make", "rm"],
                cwd=tmpdir,
                check=True
            )

            subprocess.run(
                ["make", "run"],
                cwd=tmpdir,
                check=True,
                env=env
            )


def main():
    try:
        if os.path.exists(PID_FILE):
            raise RuntimeError(f"Warning: PID file ${PID_FILE} exists, checking if process is running...")

        atexit.register(remove_pid)  # вызов при нормальном завершении
        write_pid()
        server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Сервер остановлен")

if __name__ == '__main__':
    main()
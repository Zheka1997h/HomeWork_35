"""
Простое веб-приложение на стандартной библиотеке Python.
"""

import os
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

# ─── Пути ───────────────────────────────────────────────
# Папка, где лежит server.py (src/)
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
# Корневая папка проекта (на уровень выше src/)
BASE_DIR = os.path.dirname(SRC_DIR)
# Папка с шаблонами
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


# ─── Чтение шаблонов ──────────────────────────────────
def read_template(filename: str) -> str:
    """Читает HTML-шаблон из файла через контекстный менеджер."""
    filepath = os.path.join(TEMPLATES_DIR, filename)

    # Отладка: выводим путь в консоль
    print(f"[DEBUG] Ищем файл: {filepath}")
    print(f"[DEBUG] TEMPLATES_DIR: {TEMPLATES_DIR}")
    print(f"[DEBUG] Файл существует: {os.path.isfile(filepath)}")

    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


# ─── Обработчик запросов ───────────────────────────────
class MyHandler(BaseHTTPRequestHandler):

    ROUTES = {
        "/": "index.html",
        "/contacts": "contacts.html",
    }

    def do_GET(self):
        """Обработка GET-запросов."""
        try:
            # Статические файлы (CSS)
            if self.path.startswith("/static/"):
                self._serve_static_file()
                return

            # HTML-страницы
            template_name = self.ROUTES.get(self.path)

            if template_name is None:
                self._send_error_page(404, "404.html")
                return

            html_content = read_template(template_name)

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))

        except FileNotFoundError:
            self._send_error_page(404, "404.html")
        except Exception as e:
            print(f"[ERROR] Ошибка при обработке GET: {e}")
            self._send_error_page(500, "500.html")

    def do_POST(self):
        """Обработка POST-запросов. Данные выводятся в консоль."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            parsed_data = parse_qs(body)

            print("\n" + "=" * 50)
            print(f"[POST] Получен запрос на: {self.path}")
            print("[POST] Данные от пользователя:")
            for key, values in parsed_data.items():
                print(f"  {key}: {values[0]}")
            print("=" * 50 + "\n")

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            response = (
                "<html><body style='font-family:Arial;padding:40px;text-align:center;'>"
                "<h1>Спасибо за обращение!</h1>"
                "<p>Ваши данные успешно получены.</p>"
                "<a href='/contacts'>← Вернуться к контактам</a>"
                "</body></html>"
            )
            self.wfile.write(response.encode("utf-8"))

        except Exception as e:
            print(f"[ERROR] Ошибка при обработке POST: {e}")
            self._send_error_page(500, "500.html")

    def _serve_static_file(self):
        """Отдаёт статические файлы (CSS)."""
        # Убираем /static/ из пути
        relative_path = self.path.replace("/static/", "", 1)
        # Ищем файл в папке src/
        file_path = os.path.join(SRC_DIR, relative_path)

        # Защита от выхода за пределы директории
        real_src = os.path.realpath(SRC_DIR)
        real_file = os.path.realpath(file_path)
        if not real_file.startswith(real_src):
            self._send_error_page(404, "404.html")
            return

        if not os.path.isfile(file_path):
            self._send_error_page(404, "404.html")
            return

        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = "application/octet-stream"

        with open(file_path, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_error_page(self, status_code: int, template_name: str):
        """Отправляет страницу ошибки."""
        try:
            html_content = read_template(template_name)
            self.send_response(status_code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))
        except Exception:
            self.send_response(status_code)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"Error {status_code}".encode("utf-8"))

    def log_message(self, format, *args):
        """Логирование запросов."""
        print(f"[{self.log_date_time_string()}] {format % args}")


# ── Запуск сервера ────────────────────────────────────
def run_server(host: str = "127.0.0.1", port: int = 8080):
    """Запускает HTTP-сервер."""
    server = HTTPServer((host, port), MyHandler)
    print(f"Сервер запущен: http://{host}:{port}")
    print("Нажмите Ctrl+C для остановки.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
        server.server_close()


if __name__ == "__main__":
    run_server()
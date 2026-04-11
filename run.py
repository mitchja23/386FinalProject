import os
import time
import threading
import webbrowser
import http.server
import socketserver

ROOT    = os.path.dirname(os.path.abspath(__file__))
VIS = os.path.join(ROOT, 'visualizations')
DATA    = os.path.join(VIS, 'data', 'crime_data.json')
PORT    = 8000
URL     = f'http://localhost:{PORT}/index.html'


if not os.path.exists(DATA):
    from visualizations.data_loader import DataLoader
    from visualizations.exporter import Exporter

    Exporter(DataLoader().load()).run()
else:
    print(f"Data already built")
  
os.chdir(VIS)

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass   

server = socketserver.TCPServer(('', PORT), QuietHandler)
server.allow_reuse_address = True

thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()

time.sleep(0.4)
webbrowser.open(URL)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    server.shutdown()

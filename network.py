import socket
import threading
import time
import json

import sys
import os

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "Hokimiyat_Data")
if not os.path.exists(DATA_DIR):
    try: os.makedirs(DATA_DIR)
    except: pass

CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
FILES_DIR = os.path.join(DATA_DIR, "Files")
if not os.path.exists(FILES_DIR): os.makedirs(FILES_DIR)

import pickle
import database
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer, SimpleHTTPRequestHandler

DISCOVERY_PORT = 55555
RPC_PORT = 5050
FILE_SERVER_PORT = 5051


# =======================
# 1. RPC HTTP Server
# =======================
class RPCHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Suppress logging

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            payload = pickle.loads(post_data)
            
            func_name = payload.get("func")
            args = payload.get("args", [])
            kwargs = payload.get("kwargs", {})
            
            if hasattr(database, func_name):
                func = getattr(database, func_name)
                # Unwrap if it has the decorator
                if hasattr(func, '__wrapped__'):
                    func = getattr(func, '__wrapped__')
                
                # Execute the local sqlite function
                result = func(*args, **kwargs)
                response = pickle.dumps(result)
            else:
                response = pickle.dumps({"error": f"Function {func_name} not found"})
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.end_headers()
            self.wfile.write(response)
        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.end_headers()
                self.wfile.write(pickle.dumps({"error": err_msg}))
            except:
                pass

def start_rpc_server():
    server = ThreadingHTTPServer(('0.0.0.0', RPC_PORT), RPCHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

# =======================

# =======================
# 1.5 File HTTP Server
# =======================
class FileHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FILES_DIR, **kwargs)
        
    def log_message(self, format, *args):
        pass
        
    def do_POST(self):
        try:
            filename = self.path.lstrip('/')
            if not filename:
                self.send_response(400)
                self.end_headers()
                return
            
            content_length = int(self.headers['Content-Length'])
            
            filepath = os.path.join(FILES_DIR, filename)
            with open(filepath, 'wb') as f:
                bytes_read = 0
                while bytes_read < content_length:
                    chunk = self.rfile.read(min(65536, content_length - bytes_read))
                    if not chunk: break
                    f.write(chunk)
                    bytes_read += len(chunk)
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

def start_file_server():
    server = ThreadingHTTPServer(('0.0.0.0', FILE_SERVER_PORT), FileHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

# 2. UDP Discovery Server
# =======================
def start_discovery_server(db_name):
    def listener():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Support broadcast on Windows
            try:
                s.bind(('', DISCOVERY_PORT))
            except:
                pass
            
            while True:
                try:
                    data, addr = s.recvfrom(1024)
                    if data.decode('utf-8') == "WHO_IS_SERVER":
                        reply = json.dumps({"name": db_name, "ip": socket.gethostbyname(socket.gethostname())})
                        s.sendto(reply.encode('utf-8'), addr)
                except:
                    pass
    t = threading.Thread(target=listener, daemon=True)
    t.start()

def get_all_ips():
    ips_info = []
    try:
        hostname = socket.gethostname()
        _, _, ips = socket.gethostbyname_ex(hostname)
        for ip in ips:
            if ip.startswith("127."): continue
            if ip.startswith("100."):
                ips_info.append(f"{ip} (Tailscale)")
            elif ip.startswith("26."):
                ips_info.append(f"{ip} (Radmin VPN)")
            else:
                ips_info.append(f"{ip} (Lokal / Wi-Fi)")
    except:
        pass
    return " | ".join(ips_info) if ips_info else "Noma'lum"

# =======================
# 3. UDP Discovery Client
# =======================
def discover_servers():
    servers = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(2.0)
        
        # Broadcast to all known local subnets (critical for Radmin VPN and other virtual networks)
        try:
            hostname = socket.gethostname()
            _, _, ips = socket.gethostbyname_ex(hostname)
            for ip in ips:
                parts = ip.split('.')
                if len(parts) == 4:
                    bcast24 = f"{parts[0]}.{parts[1]}.{parts[2]}.255"
                    try: s.sendto(b"WHO_IS_SERVER", (bcast24, DISCOVERY_PORT))
                    except: pass
                    # Radmin VPN uses Class A subnet (255.0.0.0) on 26.x.x.x
                    if parts[0] == '26':
                        try: s.sendto(b"WHO_IS_SERVER", ("26.255.255.255", DISCOVERY_PORT))
                        except: pass
                    # Tailscale uses Class A subnet (255.0.0.0) or CGNAT on 100.x.x.x
                    if parts[0] == '100':
                        try: s.sendto(b"WHO_IS_SERVER", ("100.255.255.255", DISCOVERY_PORT))
                        except: pass
        except:
            pass
            
        # Fallback normal broadcast
        try:
            s.sendto(b"WHO_IS_SERVER", ('<broadcast>', DISCOVERY_PORT))
        except:
            pass
        try:
            s.sendto(b"WHO_IS_SERVER", ('255.255.255.255', DISCOVERY_PORT))
        except:
            pass
            
        start_time = time.time()
        while time.time() - start_time < 2:
            try:
                data, addr = s.recvfrom(1024)
                info = json.loads(data.decode('utf-8'))
                # Replace with the real remote IP instead of what the server thinks its IP is
                # (in case of Radmin VPN interface priority issues)
                info['ip'] = addr[0]
                servers.append(info)
            except socket.timeout:
                break
            except:
                pass
    
    # Remove duplicates
    unique_servers = {}
    for srv in servers:
        unique_servers[srv['ip']] = srv
    return list(unique_servers.values())

def host_database(db_name):
    # Starts the local RPC server and Discovery listener
    start_rpc_server()
    start_discovery_server(db_name)
    database.REMOTE_SERVER_URL = None # Just in case

def connect_to_database(ip):
    # Sets the app to client mode
    database.REMOTE_SERVER_URL = f"http://{ip}:{RPC_PORT}"

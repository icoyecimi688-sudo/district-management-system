import os
import urllib.request
import urllib.parse
from network import FILES_DIR, FILE_SERVER_PORT
import database

def get_file_url(filename):
    if not database.REMOTE_SERVER_URL:
        # Local
        return None
    # Remote
    host = database.REMOTE_SERVER_URL.split("://")[1].split(":")[0]
    return f"http://{host}:{FILE_SERVER_PORT}/{urllib.parse.quote(filename)}"

def load_file_bytes(filename):
    if not filename: return None
    
    if not database.REMOTE_SERVER_URL:
        # Load locally
        filepath = os.path.join(FILES_DIR, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    return f.read()
            except: pass
        return None
    else:
        # Load remote
        url = get_file_url(filename)
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                if resp.status == 200:
                    return resp.read()
        except: pass
        return None

def upload_file_bytes(filename, data, progress_callback=None):
    if not data or not filename: return False
    
    if not database.REMOTE_SERVER_URL:
        # Save locally
        filepath = os.path.join(FILES_DIR, filename)
        try:
            with open(filepath, 'wb') as f:
                f.write(data)
            if progress_callback: progress_callback(1.0)
            return True
        except: return False
    else:
        # Upload remote
        url = get_file_url(filename)
        import socket
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or 80
        path = parsed.path
        if parsed.query: path += '?' + parsed.query
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # No general timeout, just socket operation timeout
                s.settimeout(60)
                s.connect((host, port))
                
                headers = f"POST {path} HTTP/1.1\r\n"
                headers += f"Host: {host}:{port}\r\n"
                headers += f"Content-Length: {len(data)}\r\n"
                headers += "Connection: close\r\n\r\n"
                s.sendall(headers.encode('utf-8'))
                
                chunk_size = 65536
                uploaded = 0
                total = len(data)
                
                for i in range(0, total, chunk_size):
                    chunk = data[i:i+chunk_size]
                    s.sendall(chunk)
                    uploaded += len(chunk)
                    if progress_callback:
                        progress_callback(uploaded / total)
                        
                response = s.recv(4096)
                return b"200 OK" in response
        except: return False

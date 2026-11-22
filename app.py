"""Local standard-library server. Run: python app.py"""
import argparse,json,sqlite3
from core.recognitions import operate, export_csv
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from core.instrument import compute
from core.tokens import session, csv_export

class Handler(BaseHTTPRequestHandler):
    def send(self,code,body,mime):
        self.send_response(code);self.send_header("Content-Type",mime);self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if self.path=="/recognition":
            return self.send(200,(Path(__file__).parent/"ui/recognition.html").read_bytes(),"text/html; charset=utf-8")
        if self.path=="/tokens":
            return self.send(200,(Path(__file__).parent/"ui/tokens.html").read_bytes(),"text/html; charset=utf-8")
        if self.path=="/elements.json":
            from core.elements import DATA_PATH
            return self.send(200,DATA_PATH.read_bytes(),"application/json")
        if self.path!="/":return self.send(404,b"Not found","text/plain")
        self.send(200,(Path(__file__).parent/"ui/index.html").read_bytes(),"text/html; charset=utf-8")
    def do_POST(self):
        if self.path not in ("/api/calculate","/api/tokens","/api/tokens.csv","/api/recognition","/api/recognition.csv"):return self.send(404,b"Not found","text/plain")
        try:
            n=int(self.headers.get("Content-Length","0"))
            if n>128000:raise ValueError("Request too large.")
            payload=json.loads(self.rfile.read(n))
            if self.path.startswith("/api/recognition"):
                if self.path.endswith(".csv"):
                    record=operate({"action":"read","event":payload["event"]})
                    return self.send(200,export_csv(record).encode(),"text/csv; charset=utf-8")
                return self.send(200,json.dumps(operate(payload),allow_nan=False).encode(),"application/json")
            result=compute(payload) if self.path=="/api/calculate" else session(payload)
            if self.path=="/api/tokens.csv":
                return self.send(200,csv_export(result).encode(),"text/csv; charset=utf-8")
            body=json.dumps(result,allow_nan=False).encode()
        except (sqlite3.Error,OSError,ValueError,TypeError,KeyError,ArithmeticError,RecursionError,AttributeError) as exc:
            return self.send(400,json.dumps({"error":str(exc) or "Invalid request."}).encode(),"application/json")
        self.send(200,body,"application/json")
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--port",type=int,default=8765);parser.add_argument("--open",action="store_true");args=parser.parse_args()
    server=ThreadingHTTPServer(("127.0.0.1",args.port),Handler)
    print(f"Ultimodel Calculator / Grapher: http://127.0.0.1:{args.port}  (Ctrl+C to stop)",flush=True)
    if args.open:
        import webbrowser
        webbrowser.open(f"http://127.0.0.1:{args.port}/")
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


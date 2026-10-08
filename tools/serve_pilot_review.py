#!/usr/bin/env python3
"""Serve one generated review file, without exposing the corpus or directory."""
import argparse
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('html',type=Path);args=p.parse_args();data=args.html.read_bytes()
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path not in ['/','/NAVigator-pilot.html']:
   self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('X-Robots-Tag','noindex, nofollow');self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'");self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass
s=HTTPServer(('127.0.0.1',0),Handler);print('REVIEW_URL=http://127.0.0.1:'+str(s.server_port),flush=True);s.serve_forever()

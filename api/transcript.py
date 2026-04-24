from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        video_id = params.get('videoId', [None])[0]

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if not video_id:
            self.wfile.write(json.dumps({'error': 'videoId required'}).encode())
            return

        try:
            url = f'https://youtubetotranscript.com/transcript?v={video_id}'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8')
            
            # 자막 텍스트 추출
            import re
            pattern = r'<text[^>]*>(.*?)</text>'
            texts = re.findall(pattern, html, re.DOTALL)
            
            if not texts:
                # 다른 패턴 시도
                pattern2 = r'"transcript":"(.*?)"'
                match = re.search(pattern2, html)
                if match:
                    text = match.group(1).replace('\\n', ' ')
                else:
                    self.wfile.write(json.dumps({'error': '자막을 찾을 수 없어요'}).encode())
                    return
            else:
                text = ' '.join(texts)
                # HTML 태그 제거
                text = re.sub(r'<[^>]+>', '', text)
            
            self.wfile.write(json.dumps({'transcript': text, 'lang': 'ko'}).encode())
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

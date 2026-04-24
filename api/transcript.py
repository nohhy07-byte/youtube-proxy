from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from youtube_transcript_api import YouTubeTranscriptApi

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
            ytt_api = YouTubeTranscriptApi()
            fetched = ytt_api.fetch(video_id, languages=['ko', 'en'])
            text = ' '.join([t.text for t in fetched])
            self.wfile.write(json.dumps({'transcript': text, 'lang': 'ko'}).encode())
        except Exception as e:
            try:
                ytt_api = YouTubeTranscriptApi()
                fetched = ytt_api.fetch(video_id)
                text = ' '.join([t.text for t in fetched])
                self.wfile.write(json.dumps({'transcript': text, 'lang': 'auto'}).encode())
            except Exception as e2:
                self.wfile.write(json.dumps({'error': str(e2)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

from flask import Flask, request, jsonify, render_template_string
import yt_dlp

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Saver Pro</title>
    <style>
        body { font-family: sans-serif; background: #000; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #111; padding: 25px; border-radius: 15px; width: 90%; max-width: 350px; text-align: center; border: 1px solid #fe2c55; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 8px; border: none; box-sizing: border-box; }
        button { background: #fe2c55; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; }
        #result { display: none; margin-top: 20px; }
        .download-link { display: block; background: #25f4ee; color: black; padding: 10px; margin-top: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>TikTok <span style="color:#fe2c55">Saver</span></h2>
        <input type="text" id="url" placeholder="Pega el link de TikTok aquí">
        <button onclick="descargar()">Obtener Video</button>
        <div id="loading" style="display:none; margin-top:10px;">⚡ Procesando...</div>
        <div id="result">
            <img id="thumb" src="" style="width:100%; border-radius:10px;">
            <a id="link" class="download-link" href="" target="_blank">Descargar Video Sin Marca</a>
        </div>
    </div>
    <script>
        async function descargar() {
            const url = document.getElementById('url').value;
            if(!url) return alert("Pega un link");
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            try {
                const res = await fetch('/download', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url})
                });
                const data = await res.json();
                if(data.error) throw new Error();
                document.getElementById('thumb').src = data.thumbnail;
                document.getElementById('link').href = data.url;
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
            } catch {
                alert("Error al obtener el video. Intenta con otro link.");
                document.getElementById('loading').style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Referer': 'https://www.tiktok.com/'
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            
            # Buscar el formato específico sin marca de agua
            for f in info.get('formats', []):
                if f.get('format_id') == 'download_addr-0':
                    video_url = f.get('url')
                    break
            
            return jsonify({
                "url": video_url,
                "thumbnail": info.get('thumbnail'),
                "title": info.get('title')
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()

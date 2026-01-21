from flask import Flask, request, jsonify, render_template_string
import yt_dlp

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Saver - Sin Marca de Agua</title>
    <style>
        body { 
            font-family: 'Segoe UI', sans-serif; background: #010101; 
            color: white; display: flex; justify-content: center; 
            align-items: center; height: 100vh; margin: 0; 
        }
        .card { 
            background: #121212; padding: 30px; border-radius: 20px; 
            box-shadow: 0 0 20px rgba(254, 44, 85, 0.2); 
            width: 100%; max-width: 380px; text-align: center; border: 1px solid #333;
        }
        h1 { color: #fff; font-size: 26px; margin-bottom: 10px; }
        .accent { color: #fe2c55; } /* Rojo TikTok */
        input { 
            width: 100%; padding: 15px; border: 2px solid #333; border-radius: 10px; 
            margin-bottom: 20px; box-sizing: border-box; outline: none;
            background: #1e1e1e; color: white; font-size: 16px;
        }
        input:focus { border-color: #25f4ee; } /* Cian TikTok */
        button { 
            background: #fe2c55; color: white; border: none; padding: 15px; 
            border-radius: 10px; cursor: pointer; font-weight: bold; width: 100%;
            font-size: 16px; transition: 0.3s;
        }
        button:hover { background: #ef2950; transform: scale(1.02); }
        #result { margin-top: 25px; display: none; }
        .thumb { width: 100%; border-radius: 15px; margin-bottom: 15px; border: 1px solid #444; }
        .download-btn { 
            display: block; background: #25f4ee; color: #000; 
            text-decoration: none; padding: 12px; border-radius: 10px; 
            font-weight: bold; margin-bottom: 10px;
        }
        .loader { display: none; color: #25f4ee; margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h1>TikTok <span class="accent">Saver</span></h1>
        <p style="color: #888; font-size: 13px;">Descarga videos sin marca de agua</p>
        <input type="text" id="videoUrl" placeholder="Pega el enlace de TikTok aquí...">
        <button id="btnAction" onclick="getTikTok()">Obtener Video</button>
        <div id="loader" class="loader">Procesando...</div>

        <div id="result">
            <img id="preview" class="thumb" src="">
            <p id="title" style="font-size: 14px; margin-bottom: 15px;"></p>
            <a id="downloadBtn" class="download-btn" href="" target="_blank">⬇️ Descargar MP4</a>
            <button onclick="location.reload()" style="background: transparent; color: #888; font-size: 12px; border: none;">Limpiar</button>
        </div>
    </div>

    <script>
        async function getTikTok() {
            const url = document.getElementById('videoUrl').value;
            if (!url) return alert("Por favor pega un enlace");
            
            document.getElementById('btnAction').style.display = 'none';
            document.getElementById('loader').style.display = 'block';

            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                document.getElementById('loader').style.display = 'none';

                if (data.error) {
                    alert("No se pudo obtener el video. Asegúrate de que el link sea correcto.");
                    document.getElementById('btnAction').style.display = 'block';
                } else {
                    document.getElementById('preview').src = data.thumbnail;
                    document.getElementById('title').innerText = data.title;
                    document.getElementById('downloadBtn').href = data.url;
                    document.getElementById('result').style.display = 'block';
                }
            } catch (e) {
                alert("Error de conexión");
                document.getElementById('btnAction').style.display = 'block';
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
    video_url = data.get('url')
    
    # Configuramos yt-dlp para simular un dispositivo móvil
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
            'Referer': 'https://www.tiktok.com/'
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Intentamos buscar el link directo sin marca (normalmente el 'url' principal en TikTok)
            clean_url = info.get('url')
            
            # Si hay una lista de formatos, buscamos el que no tenga marca de agua
            for f in info.get('formats', []):
                if f.get('format_id') == 'download_addr-0': # ID común para video limpio
                    clean_url = f.get('url')
                    break
            
            return jsonify({
                "title": info.get('title', 'Video de TikTok'),
                "url": clean_url,
                "thumbnail": info.get('thumbnail')
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw
import os
import io

app = Flask(__name__)

# Chemin du dossier où les fichiers seront enregistrés
UPLOAD_FOLDER = 'uploads'

# Créez le dossier si il n'existe pas
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configuration de Flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route pour la page principale
@app.route('/')
def index():
    return render_template('index.html')

# Route pour télécharger le fichier
@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Récupérez le fichier téléchargé
        file = request.files['file']
        # Enregistrez le fichier dans le dossier uploads
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        # Ouvrez le fichier et affichez son contenu
        with open(os.path.join(app.config['UPLOAD_FOLDER'], file.filename), 'r') as f:
            content = f.read()
        # Rendrez la page avec le contenu du fichier
        return render_template('editor.html', content=content, filename=file.filename)

# Route pour enregistrer les modifications
@app.route('/save', methods=['POST'])
def save_file():
    if request.method == 'POST':
        # Récupérez le contenu modifié et le nom du fichier
        content = request.form['content']
        filename = request.form['filename']
        # Enregistrez les modifications dans le fichier
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'w') as f:
            f.write(content)
        # Générez l'image à partir du fichier modifié
        image = generate_image(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Rendrez la page avec l'image générée
        return send_file(io.BytesIO(image), mimetype='image/png')

# Fonction pour générer l'image à partir du fichier
def generate_image(file_path):
    # Ouvrez le fichier et lisez son contenu
    with open(file_path, 'r') as f:
        data = f.read().splitlines()
    # Créez une nouvelle image
    image = Image.new('RGB', (len(data[0]) * 10, len(data) * 10), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    # Dessinez les cellules
    for y in range(len(data)):
        for x in range(len(data[y])):
            cell = int(data[y][x])
            if cell == 0:
                draw.rectangle((x * 10, y * 10, (x + 1) * 10, (y + 1) * 10), fill=(255, 255, 255))
            elif cell == 1:
                draw.rectangle((x * 10, y * 10, (x + 1) * 10, (y + 1) * 10), fill=(0, 0, 0))
            elif cell == 3:
                draw.polygon([(x * 10, (y + 1) * 10), ((x + 1) * 10, (y + 1) * 10), ((x + 1) * 10, y * 10)], fill=(0, 0, 0))
            elif cell == 4:
                draw.polygon([(x * 10, y * 10), ((x + 1) * 10, y * 10), ((x + 1) * 10, (y + 1) * 10)], fill=(0, 0, 0))
            elif cell == 5:
                draw.polygon([(x * 10, y * 10), ((x + 1) * 10, y * 10), (x * 10, (y + 1) * 10)], fill=(0, 0, 0))
            elif cell == 6:
                draw.polygon([(x * 10, (y + 1) * 10), (x * 10, y * 10), ((x + 1) * 10, (y + 1) * 10)], fill=(0, 0, 0))
    # Renvoyez l'image sous forme de bytes
    bytes_io = io.BytesIO()
    image.save(bytes_io, format='PNG')
    return bytes_io.getvalue()

if __name__ == '__main__':
    app.run(debug=True)

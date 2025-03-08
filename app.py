from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime
import matplotlib
matplotlib.use("Agg")  # Desativa a interface gráfica



app = Flask(__name__)
DATA_FILE = "data.json"
STATIC_FOLDER = "static"
GRAPH_FILE = os.path.join(STATIC_FOLDER, "grafico.png")

if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

@app.route('/', methods=['GET', 'POST'])
def index():
    global data
    if request.method == 'POST':
        if 'json_file' in request.files:
            file = request.files['json_file']
            if file.filename.endswith('.json'):
                data = json.load(file)
                save_data(data)
                return redirect(url_for('index'))
        else:
            nome = request.form['nome']
            horario = request.form['horario']
            glicemia = int(request.form['glicemia'])
            
            # Verificar se o pet já existe
            existing_pet = next((pet for pet in data if pet['Nome'] == nome), None)
            
            if existing_pet:
                existing_pet['Horários'].append({"Horário": horario, "Glicemia": glicemia})
            else:
                new_entry = {
                    "Nome": nome,
                    "Tipo": request.form['tipo'],
                    "Raça": request.form['raça'],
                    "Idade": request.form['idade'],
                    "Peso": request.form['peso'],
                    "Horários": [{"Horário": horario, "Glicemia": glicemia}]
                }
                data.append(new_entry)
            
            save_data(data)
            return redirect(url_for('index'))
    
    df = []
    img_path = None
    if data:
        horarios = []
        glicemias = []
        for pet in data:
            for entry in pet['Horários']:
                horarios.append(entry['Horário'])
                glicemias.append(entry['Glicemia'])
        df = pd.DataFrame({'Horário': horarios, 'Glicemia': glicemias})
        df = df.sort_values(by="Horário")
        plt.figure()
        plt.plot(df["Horário"], df["Glicemia"], marker='o', linestyle='-', color='b')
        plt.xlabel("Horário")
        plt.ylabel("Glicemia (mg/dL)")
        plt.title("Curva Glicêmica")
        plt.xticks(rotation=45)
        plt.savefig(GRAPH_FILE)
        img_path = GRAPH_FILE + "?v=" + str(datetime.now().timestamp())
    
    return render_template('index.html', data=data, img_path=img_path)

@app.route('/get_pet/<nome>')
def get_pet(nome):
    pet = next((pet for pet in data if pet['Nome'] == nome), None)
    return jsonify(pet) if pet else jsonify({})


@app.route('/clear', methods=['POST'])
def clear_data():
    global data
    data = []
    save_data(data)
    if os.path.exists(GRAPH_FILE):
        os.remove(GRAPH_FILE)
    return redirect(url_for('index'))

@app.route('/export')
def export_json():
    if data:
        pet_name = data[0]["Nome"].replace(" ", "_") if "Nome" in data[0] else "dados_pet"
        file_name = f"{pet_name}.json"
        return send_file(DATA_FILE, as_attachment=True, download_name=file_name)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
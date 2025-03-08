from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime

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
        new_entry = {
            "Nome": request.form['nome'],
            "Tipo": request.form['tipo'],
            "Raça": request.form['raça'],
            "Idade": request.form['idade'],
            "Peso": request.form['peso'],
            "Horário": request.form['horario'],
            "Glicemia": int(request.form['glicemia'])
        }
        data.append(new_entry)
        save_data(data)
        return redirect(url_for('index'))
    
    df = pd.DataFrame(data)
    img_path = None
    if not df.empty:
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

@app.route('/clear', methods=['POST'])
def clear_data():
    global data
    data = []
    save_data(data)
    if os.path.exists(GRAPH_FILE):
        os.remove(GRAPH_FILE)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
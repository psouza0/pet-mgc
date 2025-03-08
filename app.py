from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

app = Flask(__name__)

data = []  # Lista para armazenar os dados temporariamente

@app.route('/', methods=['GET', 'POST'])
def index():
    global data
    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        raça = request.form['raça']
        idade = request.form['idade']
        peso = request.form['peso']
        horario = request.form['horario']
        glicemia = request.form['glicemia']
        
        data.append({
            "Nome": nome,
            "Tipo": tipo,
            "Raça": raça,
            "Idade": idade,
            "Peso": peso,
            "Horário": horario,
            "Glicemia": int(glicemia)
        })
        return redirect(url_for('index'))
    
    df = pd.DataFrame(data)
    img_path = None
    if not df.empty:
        plt.figure()
        plt.plot(df["Horário"], df["Glicemia"], marker='o', linestyle='-', color='b')
        plt.xlabel("Horário")
        plt.ylabel("Glicemia (mg/dL)")
        plt.title("Curva Glicêmica")
        plt.xticks(rotation=45)
        img_path = os.path.join('static', 'grafico.png')
        plt.savefig(img_path)
    
    return render_template('index.html', data=data, img_path=img_path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

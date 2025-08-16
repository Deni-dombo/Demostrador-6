python 
from flask import Flask, render_template, request, redirect
import json
import os
import uuid

app = Flask(__name__)

DATABASE_FILE = "database.json"

def carregar_dados():
    if not os.path.exists(DATABASE_FILE):
        return {}
    with open(DATABASE_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def salvar_dados(dados):
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        url_destino = request.form.get("url_destino", "").strip()

        if not titulo or not url_destino:
            return "Erro: Todos os campos são obrigatórios.", 400

        codigo = str(uuid.uuid4())[:6]

        dados = carregar_dados()
        dados[codigo] = {
            "titulo": titulo,
            "url_destino": url_destino,
            "leads": []
        }
        salvar_dados(dados)
        link_funil = request.host_url + "go/" + codigo
        return f"Link do funil criado: <a href='{link_funil}' target='_blank'>{link_funil}</a>"

    return render_template("index.html")

@app.route("/go/<codigo>", methods=["GET", "POST"])
def funil(codigo):
    dados = carregar_dados()
    if codigo not in dados:
        return "Link não encontrado.", 404

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            return "Por favor, insira um e-mail válido.", 400

        if email not in dados[codigo]["leads"]:
            dados[codigo]["leads"].append(email)
            salvar_dados(dados)

        return render_template("obrigado.html", destino=dados[codigo]["url_destino"])

    return render_template("funil.html", titulo=dados[codigo]["titulo"], codigo=codigo)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

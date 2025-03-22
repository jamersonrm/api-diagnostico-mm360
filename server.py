
from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

app = Flask(__name__)

# Configurações da planilha
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "/etc/secrets/credenciais.json" if os.getenv("RENDER") else "credenciais.json"
SHEET_NAME = "Planilha de Diagnóstico Leads"
ABA = "Leads"

# Autentica no Google Sheets
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(ABA)

def formatar_diagnostico(lead):
    return f"""
🧠 Diagnóstico do Lead: {lead['Nome do Lead']}

📊 Desafio: {lead['Maior Desafio']}
💰 Faturamento: {lead['Faturamento']}
🚫 Já investiu antes? {lead['Já investiu em marketing digital antes?']}

📱 Instagram:
  - Bio otimizada: {lead['Bio otimizada (SIM/NÃO)']}
  - Destaques organizados: {lead['Destaques organizados (SIM/NÃO)']}
  - Frequência de postagens: {lead['Frequência de postagens (Alta/Média/Baixa)']}
  - Engajamento real: {lead['Engajamento real (SIM/NÃO)']}
  - Conteúdo focado em vendas: {lead['Conteúdo focado em vendas (SIM/NÃO)']}

🌐 Site:
  - Link: {lead['Site/Landing Page']}
  - Mobile-friendly: {lead['Site mobile-friendly (SIM/NÃO)']}
  - Carregamento rápido: {lead['Carregamento rápido (SIM/NÃO)']}
  - Botões de conversão claros: {lead['Botões de conversão claros (SIM/NÃO)']}
  - SEO otimizado: {lead['SEO otimizado (SIM/NÃO)']}
  - Prova social: {lead['Possui prova social (SIM/NÃO)']}

📍 Google Meu Negócio:
  - Perfil atualizado: {lead['Perfil atualizado (SIM/NÃO)']}
  - Boas avaliações: {lead['Boas avaliações (SIM/NÃO)']}
  - Aparece nas buscas relevantes: {lead['Aparece nas buscas relevantes (SIM/NÃO)']}
  - Fotos e informações completas: {lead['Fotos e informações completas (SIM/NÃO)']}

📈 Tráfego Pago:
  - Pixel instalado: {lead['Pixel/Google Tag instalado (SIM/NÃO)']}
  - Anúncios ativos: {lead['Anúncios ativos (SIM/NÃO)']}
  - Faz remarketing: {lead['Faz remarketing? (SIM/NÃO)']}

🏁 Concorrência:
  - 1: {lead['Concorrente 1']}
  - 2: {lead['Concorrente 2']}
  - 3: {lead['Concorrente 3']}
  - O que fazem melhor: {lead['O que os concorrentes fazem melhor?']}

⭐ Diferenciais: {lead['Diferenciais do lead']}
📝 Observações: {lead['Observações Gerais']}
"""

@app.route("/")
def home():
    return "API de Diagnóstico Online. Use /gerar_diagnostico?linha=X ou /gerar_diagnostico?nome=Fulano"

@app.route("/gerar_diagnostico", methods=["GET"])
def gerar_diagnostico():
    try:
        raw_data = sheet.get_all_values()
        headers = raw_data[0]
        values = raw_data[1:]

        df = pd.DataFrame(values, columns=headers)
        df = df[df['Nome do Lead'].str.strip() != ""]  # remove linhas vazias

        # Busca por linha
        if 'linha' in request.args:
            linha = int(request.args.get("linha"))
            if linha < 2 or linha > (len(df) + 1):
                return f"Linha {linha} não encontrada. Total de linhas: {len(df)}"
            lead = df.iloc[linha - 2]
            return f"<pre>{formatar_diagnostico(lead)}</pre>"

        # Busca por nome
        elif 'nome' in request.args:
            nome = request.args.get("nome").strip().lower()
            match = df[df["Nome do Lead"].str.strip().str.lower() == nome]
            if match.empty:
                return f"Lead com nome '{nome}' não encontrado."
            lead = match.iloc[0]
            return f"<pre>{formatar_diagnostico(lead)}</pre>"

        else:
            return "Parâmetro 'linha' ou 'nome' obrigatório."

    except Exception as e:
        return f"Erro ao gerar diagnóstico: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)


from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import unicodedata

app = Flask(__name__)

# Configurações
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "/etc/secrets/credenciais.json" if os.getenv("RENDER") else "credenciais.json"

# Planilhas
PLANILHA_LEADS = "Planilha de Diagnóstico Leads"
ABA_LEADS = "Leads"
PLANILHA_PERSUASAO = "Biblioteca de Diagnósticos Persuasivos - MM360"

# Autenticação
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
client = gspread.authorize(creds)

def normalizar(texto):
    return unicodedata.normalize('NFKD', texto.strip().lower()).encode('ASCII', 'ignore').decode('utf-8')

def formatar_bloco_persuasivo(bloco):
    return f"""
🧩 Diagnóstico Persuasivo MM360

🔥 Dor Comum: {bloco.get("Dor Comum", "")}
📊 Leitura Estratégica: {bloco.get("Leitura Estratégica", "")}
🚀 Solução com Tráfego Pago: {bloco.get("Solução com Tráfego Pago", "")}
🧭 Jornada do Cliente: {bloco.get("Jornada do Cliente", "")}
💬 Frase Pronta: {bloco.get("Frases Persuasivas Prontas", "")}
📈 Projeção de Retorno: {bloco.get("Projeção de Retorno Sugerida", "")}
✅ CTA Final: {bloco.get("CTA Final de Fechamento", "")}
📝 Observações: {bloco.get("Observações Adicionais", "")}
"""

def formatar_diagnostico(lead, bloco=None):
    bloco_final = formatar_bloco_persuasivo(bloco) if bloco else ""
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

{bloco_final}
"""

@app.route("/gerar_diagnostico", methods=["GET"])
def gerar_diagnostico():
    try:
        aba_leads = client.open(PLANILHA_LEADS).worksheet(ABA_LEADS)
        raw_data = aba_leads.get_all_values()
        headers = raw_data[0]
        values = raw_data[1:]
        df = pd.DataFrame(values, columns=headers)
        df = df[df['Nome do Lead'].str.strip() != ""]

        if 'linha' not in request.args:
            return "Parâmetro 'linha' obrigatório."
        linha = int(request.args.get("linha"))
        if linha < 2 or linha > (len(df) + 1):
            return f"Linha {linha} não encontrada. Total de linhas: {len(df)}"
        lead = df.iloc[linha - 2]

        nicho_manual = lead.get("Nicho", "").strip().lower()
        campos_texto = " ".join([lead.get("Bio otimizada (SIM/NÃO)", ""),
                                 lead.get("Conteúdo focado em vendas (SIM/NÃO)", ""),
                                 lead.get("Observações Gerais", "")]).lower()

        possiveis_nichos = ["terapeutas", "psicólogos", "estética", "beleza", "tatuadores", "dentistas", "crossfit"]
        nicho_detectado = ""

        if nicho_manual:
            nicho_detectado = nicho_manual
        else:
            for n in possiveis_nichos:
                if n in campos_texto:
                    nicho_detectado = n
                    break

        if not nicho_detectado:
            nicho_detectado = "modelo geral"

        planilha_persuasao = client.open(PLANILHA_PERSUASAO)
        try:
            aba_nicho = planilha_persuasao.worksheet(nicho_detectado.title())
        except:
            headers = ["Dor Comum","Leitura Estratégica","Solução com Tráfego Pago","Jornada do Cliente",
                       "Frases Persuasivas Prontas","Projeção de Retorno Sugerida",
                       "CTA Final de Fechamento","Observações Adicionais"]
            aba_nicho = planilha_persuasao.add_worksheet(title=nicho_detectado.title(), rows="100", cols=str(len(headers)))
            aba_nicho.append_row(headers)

        dados_persuasao = aba_nicho.get_all_records()
        bloco = dados_persuasao[0] if dados_persuasao else {}

        return f"<pre>{formatar_diagnostico(lead, bloco)}</pre>"

    except Exception as e:
        return f"Erro ao gerar diagnóstico: {str(e)}"

@app.route("/")
def home():
    return "API MM360 ativa. Use /gerar_diagnostico?linha=X para rodar o diagnóstico completo."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

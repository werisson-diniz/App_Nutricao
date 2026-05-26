import streamlit as st
import pandas as pd
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF

# =============================
# CONFIG
# =============================

st.set_page_config(page_title="Nutri AI", page_icon="🍎", layout="wide")

client = OpenAI(api_key="xxxxxxxxxx")

# =============================
# PDF
# =============================

def exportar_pdf(mensagens):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0,10,"Relatório Nutri AI", ln=True)

    pdf.ln(10)

    for msg in mensagens:

        role = "Usuário" if msg["role"] == "user" else "Nutricionista"

        pdf.set_font("Arial","B",12)
        pdf.cell(0,10,f"{role}:", ln=True)

        pdf.set_font("Arial","",12)

        texto = str(msg["content"]).encode("latin-1","replace").decode("latin-1")

        pdf.multi_cell(0,8,texto)

        pdf.ln(4)

    return bytes(pdf.output(dest="S"))

# =============================
# CARREGAR DATASET
# =============================

@st.cache_data
def carregar_dados():

    df = pd.read_pickle("alimentos_embeddings.pkl")

    return df

# =============================
# EMBEDDING PERGUNTA
# =============================

def gerar_embedding(texto):

    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )

    return resp.data[0].embedding

# =============================
# BUSCA SEMÂNTICA
# =============================

def buscar_alimentos(query, df, top_k=5):

    emb_query = gerar_embedding(query)

    matriz = list(df["embedding"])

    scores = cosine_similarity([emb_query], matriz)[0]

    df["score"] = scores

    return df.sort_values("score", ascending=False).head(top_k)

# =============================
# CHAT NUTRICIONAL
# =============================

def responder(pergunta, df):

    top = buscar_alimentos(pergunta, df)

    contexto = ""

    for _, row in top.iterrows():

        contexto += f"""
        Alimento: {row['nome']}
        Calorias: {row['energia_kcal']} kcal
        Proteína: {row['proteina_g']} g
        Carboidrato: {row['carboidrato_g']} g
        colesterol: {row['colesterol_mg']} g
        calcio: {row['calcio_mg']} mg
        perfil: {row['perfil_nutricional']} 
        Similaridade: {row['score']:.2f}
        """


    prompt = f"""
Você é um recomendador de alimentos brasileiro especializado em nutrição.

REGRAS GERAIS
1. Responda apenas perguntas relacionadas a alimentação, nutrição, dieta, nutrientes e saúde alimentar.
2. Se a pergunta não for sobre alimentação ou nutrição, responda:
   "Posso ajudar apenas com assuntos relacionados a alimentação e nutrição."
3. Use os alimentos do CONTEXTO abaixo sempre que possível.
4. Caso os alimentos do contexto não sejam suficientes, utilize conhecimentos gerais de nutrição.

FUNCIONALIDADES
Você também pode:

• Calcular o IMC (Índice de Massa Corporal) quando o usuário informar peso e altura.

Fórmula:
IMC = peso / (altura²)

Classificação:
- Abaixo de 18.5 → Abaixo do peso
- 18.5 – 24.9 → Peso normal
- 25 – 29.9 → Sobrepeso
- 30 ou mais → Obesidade

• Estimar necessidades calóricas diárias com base no peso, objetivo e nível de atividade física.

Objetivos possíveis:
- emagrecimento
- manutenção de peso
- ganho de massa muscular

• Recomendar alimentos adequados ao objetivo nutricional.

FORMATAÇÃO DA RESPOSTA

Sempre que recomendar alimentos, apresente em **tabela** no seguinte formato:

| Alimento | Calorias | Proteína | Carboidrato | Gordura |
|----------|----------|----------|-------------|---------|

Explique brevemente por que os alimentos são recomendados.

CONTEXTO DE ALIMENTOS:
{contexto}

Pergunta do usuário:
{pergunta}
"""

    messages = st.session_state.messages + [
        {"role":"user","content":prompt}
    ]

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    return resp.choices[0].message.content

# =============================
# INTERFACE
# =============================

st.title("🍎 Nutri AI - Recomendador Alimentar Inteligente")

df = carregar_dados()

if "messages" not in st.session_state:
    st.session_state.messages = []

# =============================
# SIDEBAR
# =============================

with st.sidebar:

    st.header("⚙️ Opções")

    if st.button("Limpar conversa"):
        st.session_state.messages = []
        st.rerun()

    # Botão para baixar PDF
    if st.session_state.messages:

        pdf_bytes = exportar_pdf(st.session_state.messages)

        st.download_button(
            label="📄 Baixar PDF da conversa",
            data=pdf_bytes,
            file_name="dieta.pdf",
            mime="application/pdf"
        )

    st.info("""
**Exemplos de perguntas**

- Alimentos para emagrecimento
- Pode sugerir alimentos para um plano alimentar focado em ganho de massa muscular?
- Quais alimentos ricos em proteína e com boas calorias são indicados para quem quer ganhar massa muscular?
- Quais alimentos são bons para melhorar a visão e fortalecer os ossos?
- Qual o alimento com perfil melhor para quem tem diabetes?
""")

# =============================
# HISTÓRICO
# =============================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =============================
# INPUT
# =============================

if pergunta := st.chat_input("Digite sua pergunta sobre alimentação"):

    st.session_state.messages.append({
        "role":"user",
        "content":pergunta
    })

    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):

        resposta = responder(pergunta, df)

        st.markdown(resposta)

    st.session_state.messages.append({
        "role":"assistant",
        "content":resposta
    })

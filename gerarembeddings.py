import pandas as pd
from openai import OpenAI

client = OpenAI(api_key="xxxxxxx")

df = pd.read_csv("alimentos.csv")

embeddings = []

for _, row in df.iterrows():

    texto = f"""
    alimento: {row['nome']}
    calorias: {row['energia_kcal']} kcal
    proteína: {row['proteina_g']} g
    carboidrato: {row['carboidrato_g']} g
    colesterol: {row['colesterol_mg']} mg
    calcio: {row['calcio_mg']} mg
    perfil: {row['perfil_nutricional']} 
    """

    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )

    embeddings.append(resp.data[0].embedding)

df["embedding"] = embeddings

df.to_pickle("alimentos_embeddings.pkl")

print("Embeddings gerados com sucesso")

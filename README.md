# Nutri AI - Recomendador Alimentar Inteligente
para instalar precisa fazer os seguintes passos no linux.
passo 1: 
Faça o download dos arquivos do aplicativo

passo 2: 
no seu computador use o seu diretorio para criar a pasta com o nome:recomendacao_01
ex: /home/seunome/recomendacao_01

passo 3: 
Copie todos os arquivos baixados para dentro do diretorio /home/seunome/recomendacao_01 

passo 4: 
dentro do diretorio /home/seunome/recomendacao_01 Crie um ambiente virtual: 
python3 -m venv venv

passo 6: para ativar o ambiente virtual digite:
source venv/bin/activate

passo 7:Instale as dependências do projeto:
pip install -r requirements.txt

passo 8: execute o comando
streamlit run app.py

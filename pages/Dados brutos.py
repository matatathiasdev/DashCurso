# BIBLIOTECAS
from datetime import datetime as dt
import streamlit as st
import pandas as pd
import requests

# TITULO DA PAGINA
st.title('DADOS BRUTOS')

# LEITURA DOS DADOS USANDO REQUESTS PARA ACESSAR UM ARQUIVOS JSON E PASSAR PARA DATAFRAME PANDAS
url = 'https://labdados.com/produtos'

## REQUISICAO DA URL
response = requests.get(url)

## CRIACAO DE DATAFRAME APARTIR DO JSON OBTIDO NO RETORNO DA URL
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

# CRIANDO MENU SUSPENSO COM EXPANDER 
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

# CRIANDO MENU LATERAL DE FILTROS COM MENU EXPANDER
## TITULO DO MENU EXPANDER DE FILTROS
st.sidebar.title('Filtros')

## CRIAR FILTRO DE NOME DO PRODUTO
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

## CRIAR FILTRO DE CATEGOIRIA DO PRODUTO
with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

## CRIAR FILTRO DE PRECO
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000))

## CRIAR FILTRO DE VALOR DE FRETE
with st.sidebar.expander('Frete da venda'):
    frete = st.slider('Frete', 0,250, (0,250))

## CRIA FILTRO DE DATA DA COMPRA
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

## CRIAR FILTRO DE VENDEDOR
with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())

## CRIAR FILTRO DE LOCAL DA COMPRA
with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

## CRIAR FILTRO DE AVALIACAO DA COMPRA
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação da compra',1,5, value = (1,5))

## CRIAR FILTRO DE TIPO DE PAGAMENTO
with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

## CRIAR FILTRO DE QUANTIDADE DE PARCELAS
with st.sidebar.expander('Quantidade de parcelas'):
    qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))

# APLICANDO OS FILTROS 
## APLICA SELECAO DE COLUNAS
if colunas:
    dados = dados[colunas]

## APLICA FILTRO DE PRODUTO
if produtos:
    dados = dados[dados['Produto'].isin(produtos)]

## APLICA FILTRO DE CATEGORIA
if categoria:
    dados = dados[dados['Categoria do Produto'].isin(categoria)]

## APLICA FILTRO DE PRECO
if preco:
    dados = dados[dados['Preço'].between(preco[0], preco[1])]

## APLICA FILTRO DE FRETE
if preco:
    dados = dados[dados['Frete'].between(frete[0], frete[1])]

## APLICA FILTRO DE DATA 
if data_compra:
    dt_ini = dt.strftime(data_compra[0], '%Y-%m-%d')
    dt_fim = dt.strftime(data_compra[1], '%Y-%m-%d')
    dados = dados[dados['Data da Compra'].between(dt_ini, dt_fim)]

## APLICA FILTRO DE VENDEDOR
if vendedores:
    dados = dados[dados['Vendedor'].isin(vendedores)]

## APLICA FILTRO DE LOCAL DA COMPRA 
if local_compra:
    dados = dados[dados['Local da compra'].isin(local_compra)]

## APLICA FILTRO DE AVALIACAO DA COMPRA 
if avaliacao:
    dados = dados[dados['Avaliação da compra'].between(avaliacao[0], avaliacao[1])]

## APLICA FILTRO DE TIPO DE PAGAMENTO
if tipo_pagamento:
    dados = dados[dados['Tipo de pagamento'].isin(tipo_pagamento)]

## APLICA FILTRO DE QUANTIDADE DE PARCELAS
if qtd_parcelas:
    dados = dados[dados['Quantidade de parcelas'].between(qtd_parcelas[0], qtd_parcelas[1])]

# APRESENTAR O DATAFRAME
st.dataframe(dados)

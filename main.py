# BIBLIOTECAS
import plotly.express as px
import streamlit as st
import pandas as pd
import requests

# LAYOUT DA PAGINA
st.set_page_config(layout='wide')

# FUNCAO FORMATA NUMERO
def formata_numero(valor, prefixo = ''):
    for unidade in ['','mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

# shopping_trolley ADCIONAR UM EMOJI DE UM CARRINHO DE COMPRA 
st.title('DASHBOAR DE VENDAS :shopping_trolley:')

# LEITURA DOS DADOS USANDO REQUESTS PARA ACESSAR UM ARQUIVOS JSON E PASSAR PARA DATAFRAME PANDAS
url = 'https://labdados.com/produtos'
regioes = ['Brasil','Centro-Oeste','Nordeste','Norte','Sudeste','Sul']

## CRIA O MENU LATERAL DE FILTROS
st.sidebar.title('Filtros')

## FILTRO - CRIA UMA CAIXA DE SELEÇÃO E VALIDA SE A REGIAO SELECIONADA E BRASIL CASO SEKA A VARIAVEL REGIAO FICA VAZIA
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = ''

## FILTRO - CRIA UM CHECKBOX E VALIDA SE O MESMO ESTA SELECIONADO CASO NAO ESTEJA CRIA UMA BARRA DE SELEÇAO DE ANO
todos_anos = st.sidebar.checkbox('Dados de todo o periodo', value=True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

## CRIA A QUERY QUE SERA USADA COMO PARAMETRO NA REQUISICAO DA URL
query_string = {
    'regiao':regiao.lower(),
    'ano':ano
}

## REQUISICAO DA URL
response = requests.get(url, params=query_string)

## CRIACAO DE DATAFRAME APARTIR DO JSON OBTIDO NO RETORNO DA URL
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

## FILTRO - CRIA O FILTRO DE VENDEDORES
filtro_vendedores = st.sidebar._multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# TABELAS
## TABELAS - RECEITAS
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']]\
                       .merge(receita_estados, left_on='Local da compra', right_index=True)\
                       .sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

## TABELAS - QUANTIDADES
quantidade_estados = dados.groupby('Local da compra').size().reset_index(name='Qtd Compra')
quantidade_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']]\
                          .merge(quantidade_estados, on=['Local da compra']).sort_values('Qtd Compra', ascending=False)

quantidade_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Produto'].count().reset_index(name='Qtd Compra')
quantidade_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
quantidade_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

quantidade_categorias = dados.groupby('Categoria do Produto')[['Preço']].count()
quantidade_categorias = quantidade_categorias.rename(columns={'Preço': 'Qtd Compra'})

## TABELAS - VENDEDORES
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))

# GRAFICOS
## GRAFICOS - RECEITAS
fig_mapa_receita = px.scatter_geo(
    receita_estados,
    lat='lat',
    lon='lon',
    scope='south america',
    size='Preço',
    template='seaborn',
    hover_name='Local da compra',
    hover_data={'lat':False, 'lon':False},
    title='Receita por estado'
)

fig_receita_mensal = px.line(
    receita_mensal,
    x='Mes',
    y='Preço',
    markers=True,
    range_y=(0,receita_mensal.max()),
    color='Ano',
    line_dash='Ano',
    title='Receita mensal'
)

fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_receita_estado = px.bar(
    receita_estados.head(5), 
    x='Local da compra',
    y='Preço',
    text_auto=True,
    title='Top estados (receita)'
)

fig_receita_estado.update_layout(yaxis_title='Receita')

fig_receita_categorias = px.bar(
    receita_categorias,
    text_auto=True,
    title='Receita por categorias'
)

fig_receita_categorias.update_layout(yaxis_title='Receita')

## GRAFICOS - QUANTIDADE
fig_mapa_quantidade = px.scatter_geo(
    quantidade_estados,
    lat='lat',
    lon='lon',
    scope='south america',
    size='Qtd Compra',
    template='seaborn',
    hover_name='Local da compra',
    hover_data={'lat':False, 'lon':False},
    title='Quantidade por estado'
)

fig_quantidade_mensal = px.line(
    quantidade_mensal,
    x='Mes',
    y='Qtd Compra',
    markers=True,
    range_y=(0,quantidade_mensal.max()),
    color='Ano',
    line_dash='Ano',
    title='Quantidade mensal'
)

fig_quantidade_mensal.update_layout(yaxis_title='Quantidade')

fig_quantidade_estado = px.bar(
    quantidade_estados.head(5), 
    x='Local da compra',
    y='Qtd Compra',
    text_auto=True,
    title='Top estados (Quantidade)'
)

fig_quantidade_estado.update_layout(yaxis_title='Quantidade')

fig_quantidade_categorias = px.bar(
    quantidade_categorias,
    text_auto=True,
    title='Quantidade por categorias'
)


# VISUALIZACAO STREAMLIT
aba1, aba2, aba3 = st.tabs(['Receita','Quantidade de vendas','Vendedores'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estado, use_container_width=True)
    with coluna2:
        st.metric('Quantidade', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)
with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_quantidade, use_container_width=True)
        st.plotly_chart(fig_quantidade_estado, use_container_width=True)
    with coluna2:
        st.metric('Quantidade', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_quantidade_mensal, use_container_width=True)
        st.plotly_chart(fig_quantidade_categorias, use_container_width=True)
with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)

    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        # GRAFICO COM INPUT DO USUARIO
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores), 
                                        x='sum',
                                        y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade', formata_numero(dados.shape[0]))
        # GRAFICO COM INPUT DO USUARIO
        fig_venda_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores), 
                                        x='count',
                                        y=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_venda_vendedores)



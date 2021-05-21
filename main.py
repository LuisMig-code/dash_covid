#fazendo os imports necessários:
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# lendo os dados:
df_2019 = pd.read_csv("obitos-2019.csv")
df_2019["ano"] = 2019

df_2020 = pd.read_csv("obitos-2020.csv")
df_2020["ano"] = 2020

df_2021 = pd.read_csv("obitos-2021.csv")
df_2021["ano"] = 2021

# agrupando os dados
df_tot = pd.concat([df_2019 , df_2020 , df_2021])

# retirando dados nulos
df_tot.dropna(inplace=True)

# ajustando alguns valores
df_tot['faixa_etaria'].replace('< 9','0 - 9' , inplace = True)

#lista do estados (UF):
lista_estados = list(df_tot.uf.unique())

# separando os dados da covid:
df_covid = df_tot.query("tipo_doenca == 'COVID'")

# Configurando as cores a serem usadas na Dashboard
colors_ = {
    'background': '#2d4053',
    'text': '#ffffff'
}

# criando a tabela a ser mostrada:
fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(["UF", "Tipo da Doença", "Local do Óbito", "Faixa Etária", "Sexo", "Total de Mortos", "Ano"]),
            fill_color='#4682B4',
            align='center',
            font=dict(color='white')
            ),
        cells=dict(
            values=[df_tot.uf, df_tot.tipo_doenca, df_tot.local_obito, df_tot.faixa_etaria, df_tot.sexo, df_tot.total,
                    df_tot.ano],
            fill_color='#87CEFA',
            align='left'))
    ])
fig.update_layout(
        plot_bgcolor=colors_['background'],
        paper_bgcolor=colors_['background'],
        font_color=colors_['text']
    )


# Criando o app da dashboard setando um tema do Bootstrap
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.SUPERHERO],
                                        # Responsivilidade para mobile layout
                                        meta_tags=[ {'name': 'viewport',
                                                    'content': 'width=device-width, initial-scale=1.0'}  ] )

# Criando a Dashboard em si:
app.layout = dbc.Container([
    # linha com o cabeçalho
    dbc.Row([
        dbc.Col([
            # título principal
            html.H1("Dashboard Covid" ,
                    className = "text-center text-primary, display-2 shadow") ,
            # descrição abaixo do título
            html.H2("Dashboard criada com o intúito de analisar os dados da Covid-19 com dados do Portal da transparência" ,
                    className = "text-sm-center text-primary display-3 font-weight-bold" ,
                    style = {"font-size":26})
        ] , width=10) ,

        # cardbox
        dbc.Col([
            dbc.Card([

                # links para páginas externas
                dbc.CardLink([dbc.CardImg(
                    src = "assets/pt_logo.png" , top=True , bottom=False
                )] ,
                    href="https://transparencia.registrocivil.org.br/dados-covid-download" ,
                    target = "_blank" ,
                    className="text-center bg-white") ,

                dbc.CardLink("Onde me encontrar ?" ,
                             href="https://linktr.ee/iNukss" ,
                             target = "_blank" ,
                             className="text-center text-info" ,
                             style={"font-size":14})
            ] , style = {'width':'15rem'})

        ] , width=2)
    ]) ,

    # Linha para Selecionar o Range dos anos:
    dbc.Row([
        dbc.Col([
            html.P("Selecione o período:"),
                dcc.RangeSlider(
                        id='range-slider-anos',
                        min=2019,
                        max=2021,
                        step=1,
                        value=[2019,2021],
                        marks={
                                2019: {'label': '2019', 'style': {'color': '#ffffff'} },
                                2020: {'label': '2020', 'style': {'color': '#ffffff'} },
                                2021: {'label': '2021', 'style': {'color': '#ffffff'} }
                            }),
            html.Br(),
            html.Hr(style={"color":"black"})
        ] , width = 12)
    ]) ,

    # Linha com os 2 primeiros gráficos:
    dbc.Row([
        # Mostrar tabela dos dados:
        dbc.Col([
            html.H3("Dados da Covid19 completo:"),

            dcc.Graph(id="tabela_dos_dados" , figure = fig)
        ] , width = {'size' : 5 , 'order':1}) ,

        # gráfico das colunas com relação ao número de óbitos
        dbc.Col([
            html.H3("Selecione uma variável:" ,
                    style={"font-size":20 , "font-weight":"bold"},
                    className="text-center"),

            dcc.Dropdown(
                id="dropdown-variavel-1",
                options=[
                    {"label": "Tipo de doença", "value":"tipo_doenca"},
                    {"label": "Local do Óbito", "value": "local_obito"},
                    {"label": "Estado", "value": "uf"}
                ],
                value="local_obito",
                style={"color":"#000000" , "width":"70%"}
            ),

            dcc.Graph(id="grafico-1" , figure = {})

        ] , width = {'size' : 7 , 'order':2})
    ]) ,

    html.Br(),

    # Linha com os 2 últimos gráficos:
    dbc.Row([
        # Gráfico de distribuição da Idade
        dbc.Col([
            # selecionar se quer ou não quer mostrar as linhas:
            dcc.RadioItems(
                id = "mostrar_linha",
                options=[
                    {'label': 'Mostrar Linha ', 'value': 1},
                    {'label': 'Não Mostrar Linha', 'value': 0}
                ],
                value=0
            ) ,

            dcc.Graph(id="histograma" , figure = {})
        ] , width = {'size' : 7 , 'order':1}) ,

        # Gráfico de Rosca
        dbc.Col([
            html.H3("Selecione os Estados:",
                    style={"font-size": 20, "font-weight": "bold"},
                    className="text-center"
                    ) ,

            dcc.Dropdown(
                id = "dropdown-estados",
                options=[
                    {"label":x , "value":x} for x in lista_estados
                ],
                style={"color":"#000000" , "width":"90%"},
                multi=True,
                value="AL"
            ) ,

            dcc.Graph(id="grafico_rosca" , figure={})
        ] , width = {'size' : 5 , 'order':2})
    ])




] , fluid = True)



## Região dos CallBack's:

### Gráfico 1:
@app.callback(
    Output("grafico-1", "figure"),
    [Input("range-slider-anos","value") ,
     Input("dropdown-variavel-1","value")]
)

def update_graph_1(anos_selecionado , coluna):
    # criando uma lista com os anos selecionados:
    lista_anos = [ano for ano in range(anos_selecionado[0] , anos_selecionado[1]+1)]

    # filtrando os dados a partir do ano
    df = df_tot.query("ano == @lista_anos")

    # Agrupando os dados a partir do sexo
    df_temp_M = df.query("sexo == 'M'").groupby(coluna).sum().sort_values("total", ascending=False)

    df_temp_F = df.query("sexo == 'F'").groupby(coluna).sum().sort_values("total", ascending=False)

    # gráfico:
    fig = go.Figure()

    # Create layout and specify title, legend and so on
    fig.add_trace(go.Bar(
        x=df_temp_M.index,
        y=df_temp_M.total,
        name="Masculino",
        marker_color='#5882FA'
    ))
    fig.add_trace(go.Bar(
        x=df_temp_F.index,
        y=df_temp_F.total,
        name="Feminino",
        marker_color="#F781BE"
    ))

    fig.update_layout(title_text='Numéro de morte mediante {}'.format(coluna), barmode='group')
    fig.update_yaxes(title='Número de óbitos')
    fig.update_xaxes(title='')

    fig.update_layout(
        plot_bgcolor=colors_['background'],
        paper_bgcolor=colors_['background'],
        font_color=colors_['text']
    )

    return fig

### Histograma das idades:
@app.callback(
    Output("histograma","figure"),
    [Input("range-slider-anos", "value"),
     Input("mostrar_linha", "value")]
)

# plotar histograma
def update_histograma(anos_selecionado , tem_linha):
    # criando uma lista com os anos selecionados:
    lista_anos = [ano for ano in range(anos_selecionado[0], anos_selecionado[1] + 1)]

    # filtrando os dados a partir do ano
    df_covid = df_tot.query("ano == @lista_anos").query("tipo_doenca == 'COVID'")

    # filtrando os dados:
    df_temp_M = df_covid.query("sexo == 'M'").groupby('faixa_etaria').sum().sort_values("faixa_etaria")
    df_temp_F = df_covid.query("sexo == 'F'").groupby('faixa_etaria').sum().sort_values("faixa_etaria")

    fig = go.Figure()

    # Criando os gráficos de barras
    fig.add_trace(go.Bar(
        x=df_temp_M.index,
        y=df_temp_M.total,
        name="Masculino",
        marker_color='#5882FA'
    ))
    fig.add_trace(go.Bar(
        x=df_temp_F.index,
        y=df_temp_F.total,
        name="Feminino",
        marker_color="#F781BE"
    ))

    if tem_linha == 1:
        # adicionando a linha nos gráficos:
        fig.add_trace(go.Scatter(
            x=df_temp_F.index,
            y=df_temp_F.total,
            name="Feminino",
            marker_color="#e377af"
        ))
        fig.add_trace(go.Scatter(
            x=df_temp_M.index,
            y=df_temp_M.total,
            name="Masculino",
            marker_color='#4b6fd5'
        ))
    fig.update_layout(title_text='Distribuição das idades por números de mortos por COVID19', barmode='group')
    fig.update_yaxes(title='Número de óbitos')
    fig.update_xaxes(title='')

    fig.update_layout(
        plot_bgcolor=colors_['background'],
        paper_bgcolor=colors_['background'],
        font_color=colors_['text']
    )

    return fig

@app.callback(
    Output("grafico_rosca","figure"),
    [Input("range-slider-anos", "value"),
     Input("dropdown-estados", "value")]
)
def update_grafico_rosca(anos_selecionado , estados):
    # criando uma lista com os anos selecionados:
    lista_anos = [ano for ano in range(anos_selecionado[0], anos_selecionado[1] + 1)]

    # lista com os estados:
    if estados == []:
        estados = ["AL"]

    # filtrando os dados a partir do ano
    df_covid = df_tot.query("ano == @lista_anos").query("tipo_doenca == 'COVID'")

    df_temp = df_covid.query('uf == @estados')

    fig = px.sunburst(
        df_temp,
        path=["uf", "sexo", "faixa_etaria"],
        values="total",
        hover_name="total",
    )

    fig.update_layout(
        plot_bgcolor=colors_['background'],
        paper_bgcolor=colors_['background'],
        font_color=colors_['text']
    )

    return fig


# Instanciando a aplicação:
if __name__ == '__main__':
    app.run_server(debug=True , port=8000)
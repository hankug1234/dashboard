import dash
import json
import dash_core_components as dcc
import dash_html_components as html
from requests import get
import re
import flask
from dash.dependencies import Input, Output,State
import plotly.graph_objects as go
from collections import deque
from flask_restful import Resource,Api,reqparse
from dash.exceptions import PreventUpdate

cpuX = deque(maxlen=20); cpuY= deque(maxlen=20); gpuX= deque(maxlen=20); gpuY= deque(maxlen=20)

avgX = deque(maxlen=100); avgCpu = deque(maxlen=100); avgGpu = deque(maxlen=100); queue = list()

'''평균 그래프 사이즈 설정값 '''
count = 0; Max = 100; Min = 0

'''현재 변수 값 사태 바 설정 값'''
cdata=['interval','cpu_avg','gpu_avg','value1','value2']; rdata = [1,0,0,0,0]

'''dash 기본 양식 설정'''
es = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

'''graph css 설정'''
colors = {'background': '#111111','text': '#7FDBFF'}


'''cpu gpu에 대한 deque의 size를 초기화 하는 함수'''
def initialDequeSize(maxlen):
    global cpuX,cpuY,gpuX,gpuY
    cpuX = deque(maxlen=maxlen)
    cpuY= deque(maxlen=maxlen)
    gpuX= deque(maxlen=maxlen)
    gpuY= deque(maxlen=maxlen)

'''cpu gpu avg 값을 보여주는 bar를 생성 에대한 figure값을 생성하는 함수'''
def generate_table(cdata,rdata,max_rows=5):
    return html.Table([html.Tr([html.Th(col) for col in cdata]) ,html.Tr([html.Td(data) for data in rdata])],className='table-style')

def initGraph():
    global avgX,avgGpu,avgCpu,gpuY,gpuX,cpuX,cpuY
    avgX.append(0)
    gpuX.append(0)
    cpuX.append(0)
    gpuY.append(0)
    cpuY.append(0)
    avgCpu.append(0)
    avgGpu.append(0)
'''regular expression을 사용하여 데이터 형식이 올바를지를 판다하여 boolean값을 리턴 한다'''
def validation(str):
    exp = re.compile('{ *(\'cpu\'|\'gpu\') *: *(\d+.?\d+) *, *(\'cpu\'|\'gpu\') *: *(\d+.?\d+) *}')
    result = exp.match(str)
    if(result):
        if(result.group(1)==result.group(3)):
         return False
        else:
         return True
    else:
        return False
'''graph에 보여질avg 데이터 사이즈 를 초기화 하는 함수 '''
def initParam(c,max,min):
    global count,Max,Min
    count = c; Max = max; Min = min


initialDequeSize(20)
initGraph()
initParam(0,100,0)

'''html figure '''
app = dash.Dash(__name__, external_stylesheets=es, routes_pathname_prefix='/graph/')

avgGraphConfig= go.Figure(layout = go.Layout(plot_bgcolor= colors['background'], paper_bgcolor=colors['background'], title='AVG'))
avgGraphConfig.add_trace(go.Scatter(name='CPU', line=dict(color='firebrick')))
avgGraphConfig.add_trace(go.Scatter(name='GPU', line=dict(color='green')))

cpuGraphConfig = go.Figure(
        data=[go.Scatter( fill='tonexty',)],
        layout = go.Layout(title='CPU',plot_bgcolor= colors['background'],paper_bgcolor=colors['background'],xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        )

gpuGraphConfig = go.Figure(
        data=[go.Scatter(fill='tonexty',)],
        layout = go.Layout(title='GPU',plot_bgcolor= colors['background'], paper_bgcolor= colors['background'],xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        )

'''html form'''
app.layout = html.Div(
    [html.Div([generate_table(cdata,rdata)],className='bar-style',id='table'),
     html.Div([ dcc.Graph( id = 'graph3',animate=True, figure = avgGraphConfig)], className='avg-style'),
     html.Div([ dcc.Graph(id='graph', animate=True, figure= cpuGraphConfig)],className='cpu-style'),
     html.Div([ dcc.Graph(id='graph2', animate=True,figure= gpuGraphConfig)],className='gpu-style'),
     dcc.Interval(id='interval',interval=1000,n_intervals=0),
    ], className='base-style'
   )



@app.callback([Output('graph','figure'),Output('table','children'),Output('graph2','figure')],[Input('interval','n_intervals')])
def update_graph(n):
    global cpuX, cpuY, gpuX, gpuY, cdata,rdata

    data = get('http://127.0.0.1:5002/data').json()
    if(data['data']=='404'):
        raise PreventUpdate
    else:
     cpuX.append(cpuX[-1] + 1)
     gpuX.append(gpuX[-1] + 1)
     cpuY.append(data['data']['cpu'])
     gpuY.append(data['data']['gpu'])
     rdata[3] = data['data']['cpu']
     rdata[4] = data['data']['gpu']


    figure = go.Figure(
        data=[go.Scatter(y=list(cpuY), x=list(cpuX),)],
        layout=go.Layout(xaxis=dict(range=[min(cpuX), max(cpuX)]), yaxis=dict(range=[min(cpuY), max(cpuY)])))

    figure2 = go.Figure(
        data=[go.Scatter(y=list(gpuY), x=list(gpuX),)],
        layout=go.Layout(xaxis=dict(range=[min(gpuX), max(gpuX)]), yaxis=dict(range=[min(gpuY), max(gpuY)])))


    return figure, generate_table(cdata,rdata),figure2


@app.callback(Output('graph3','figure'),[Input('interval','n_intervals')])
def update_graph3(n):
    global avgX, avgCpu,avgGpu
    global count,Max,Min
    global rdata

    if(n%20==0):
     count+=1
     avgX.append(count)
     avgCpu.append((sum(list(cpuY)) / len(list(cpuY))))
     avgGpu.append((sum(list(gpuY)) / len(list(gpuY))))
     f = go.Figure(layout=go.Layout(xaxis=dict(showgrid=False,range=[Min,Max]),yaxis=dict(range=[0,5])))
     f.add_trace(go.Scatter(x=list(avgX), y=list(avgCpu)))
     f.add_trace(go.Scatter(x=list(avgX), y=list(avgGpu)))
     rdata[1] = avgCpu[-1]
     rdata[2] = avgGpu[-1]
     if (avgX[-1] >= Max):
         Min = Max
         Max = avgX[-1] + 100

     return f
    else:
        raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=False,port=5001)

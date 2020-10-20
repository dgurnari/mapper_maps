# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 16:49:11 2018
@author: jingwenken
"""

import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go

import networkx as nx


# read nodes
nodes_df = pd.read_csv("input/BM_graph_vertices", sep=" ", header=None,
                       names=['id', 'size'], index_col='id')

num_nodes = len(nodes_df)

# read edges
edges_df = pd.read_csv("input/BM_graph_edges", sep=" ", header=None,
                       names=['v1', 'v2'])

#create graph G
G = nx.Graph()
for i, row in edges_df.iterrows():
    G.add_edge(row.v1, row.v2)

#get a x,y position for each node
pos = nx.layout.spring_layout(G, seed=42)

#add a pos and color attribute to each node
for node in G.nodes:
    G.nodes[node]['size'] = nodes_df.loc[node, 'size']
    G.nodes[node]['pos'] = list(pos[node])

##from the docs, create a random geometric graph for test
#G=nx.random_geometric_graph(200,0.125)
pos=nx.get_node_attributes(G,'pos')


dmin=1
ncenter=0
for n in pos:
    x,y=pos[n]
    d=(x-0.5)**2+(y-0.5)**2
    if d<dmin:
        ncenter=n
        dmin=d

p=nx.single_source_shortest_path_length(G,ncenter)

#Create Edges
edge_trace = go.Scatter(
    x=[],
    y=[],
    line=dict(width=0.5,color='#888'),
    hoverinfo='none',
    mode='lines')

for edge in G.edges():
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    edge_trace['x'] += tuple([x0, x1, None])
    edge_trace['y'] += tuple([y0, y1, None])

node_trace = go.Scatter(
    x=[],
    y=[],
    text=[],
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        # colorscale options
        #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='Viridis',
        reversescale=True,
        color=[],
        size=[],
        colorbar=dict(
            thickness=15,
            title='Points in cluster',
            xanchor='left',
            titleside='right'
        ),
        line=dict(width=2)))

for node in G.nodes():
    x, y = G.nodes[node]['pos']
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])

    node_size = G.nodes[node]['size']

    node_trace['marker']['color'] += tuple([node_size])
    # node size depends on the number of points in cluster, min size = 10
    node_trace['marker']['size'] += tuple([ max([node_size, 10]) ])
    node_trace['text']+=tuple(['size: {}'.format(G.nodes[node]['size'])])

# #add color to node points
# for node, adjacencies in enumerate(G.adjacency()):
#     node_trace['marker']['color']+=tuple([len(adjacencies[1])])
#     node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: '+str(len(adjacencies[1]))
#     node_trace['text']+=tuple([node_info])





################### START OF DASH APP ###################

app = dash.Dash()

# to add ability to use columns
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                #title='<br>Network Graph of '+str(num_nodes)+' rules',
                titlefont=dict(size=16),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))


app.layout = html.Div([
                html.Div(dcc.Graph(id='my_graph',figure=fig)),
                html.Div(className='row', children=[
                    html.Div([html.H2('Overall Data'),
                              html.P('Num of nodes: ' + str(len(G.nodes))),
                              html.P('Num of edges: ' + str(len(G.edges)))],
                              className='three columns'),
                    html.Div([
                            html.H2('Selected Data'),
                            html.P('Try to select some nodes using the box or the lasso selection tool'),
                            html.Div(id='selected-data'),
                        ], className='six columns')
                    ])
                ])

@app.callback(
    Output('selected-data', 'children'),
    [Input('my_graph','selectedData')])
def display_selected_data(selectedData):
    try:
        num_of_nodes = len(selectedData['points'])
    except:
        return None
    text = [html.P('Num of nodes selected: '+str(num_of_nodes))]
#     for x in selectedData['points']:
# #        print(x['text'])
#         material = x['text'].split('<br>')[0][7:]
#         text.append(html.P(str(material)))
    return text

if __name__ == '__main__':
    app.run_server(debug=True)

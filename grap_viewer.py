#!/usr/bin/env python
# coding: utf-8


import networkx as nx
import csv
import sys

csv.field_size_limit(sys.maxsize)


from bokeh.io import show
from bokeh.plotting import figure

from bokeh.layouts import layout, column, row, grid
from bokeh.models import (BoxZoomTool, Circle, HoverTool,
                          MultiLine, Plot, Range1d, ResetTool,
                          ColumnDataSource, LabelSet,
                          TapTool, WheelZoomTool, PanTool,
                          ColorBar, LinearColorMapper, BasicTicker,
                          Button, TextInput,
                          CustomJS, MultiChoice)

from bokeh.palettes import linear_palette, Reds256
from bokeh.plotting import from_networkx, figure, curdoc


# ## Read the graphs

# Each graph must be rapresented by an adjecency list (space separated)
# We assume nodes are numbered from 1 to N
#
# The list of points covereb by each node is a file with N lines, each line contains the points id (space separated)

# In[28]:


def read_graph_from_list(GRAPH_ADJ_PATH, GRAPH_POINTS_PATH):
    # read graph adjecency list
    # ASSUME NODES ARE NUMBERED FROM 1 TO N
    G = nx.read_adjlist(GRAPH_ADJ_PATH, nodetype = int)

    # read list of points covered by each node
    # ASSUME NODES ARE NUMBERED FROM 1 TO N
    csv_file = open(GRAPH_POINTS_PATH)
    reader = csv.reader(csv_file)

    points_covered = {}

    for i, line_list in enumerate(reader):
        points_covered[i+1] = [int(node) for node in line_list[0].split(' ')]

    # add the nodes that are not in the edgelist
    G.add_nodes_from( range(1, len(points_covered) + 1) )

    for node in G.nodes:
        G.nodes[node]['points covered'] = points_covered[node]
        G.nodes[node]['size'] = len(G.nodes[node]['points covered'])
        # cap the size for display
        G.nodes[node]['size capped'] = min(5, max(10, G.nodes[node]['size']))

    return G


# In[29]:


# Prepare Data

# adj lists path
# adj lists path
GRAPH1_PATH = sys.argv[1]
GRAPH2_PATH = sys.argv[3]

# point covered by each node path
GRAPH1_POINTS_PATH = sys.argv[2]
GRAPH2_POINTS_PATH = sys.argv[4]

###########
# GRAPH 1 #
###########

# read graph
# ASSUME NODES ARE NUMBERED FROM 1 TO N
G1 = read_graph_from_list(GRAPH1_PATH, GRAPH1_POINTS_PATH)

###########
# GRAPH 2 #
###########

G2 = read_graph_from_list(GRAPH2_PATH, GRAPH2_POINTS_PATH)


# In[30]:


# create a red palette and reverse it (I want 0 to be white and 100 to be red)
my_red_palette = linear_palette(Reds256, 101)[::-1]

SELECTED_NODES = []

# function to color the nodes
# will be triggered each time SELECTED_NODES is updated
def color_nodes(G1, G2, SELECTED_NODES=[], my_palette=my_red_palette):
    # color all non selected G1 nodes white
    for node in G1.nodes:
        if node in SELECTED_NODES:
            G1.nodes[node]['color'] = my_palette[-1]
        else:
            G1.nodes[node]['color'] = my_palette[0]

    # get list of points in SELECTED_NODES
    POINTS_IN_SELECTED_NODES = set()
    for node in SELECTED_NODES:
        POINTS_IN_SELECTED_NODES = POINTS_IN_SELECTED_NODES.union(set(G1.nodes[node]['points covered']))

    # color nodes in G2 according to the percentage of points that are in POINTS_IN_SELECTED_NODES
    for node in G2.nodes:
        points = set(G2.nodes[node]['points covered'])
        coverage = len(points & POINTS_IN_SELECTED_NODES) / len(points)
        G2.nodes[node]['coverage'] = coverage
        # round the coverage value and use it as index for our color palette
        G2.nodes[node]['color'] = my_palette[round(coverage*100)]


# color all nodes to white
color_nodes(G1, G2, SELECTED_NODES)


# ## UI

##########
# PLOT 1 #
##########

plot1 = Plot(plot_width=800, plot_height=800,
            x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1),
            sizing_mode="stretch_both")

node_hover_tool = HoverTool(tooltips=[("index", "@index"), ("size", "@size")])
plot1.add_tools(PanTool(), node_hover_tool, BoxZoomTool(), WheelZoomTool(),
                ResetTool())

graph_renderer_1 = from_networkx(G1, nx.spring_layout,
                                  seed=42, scale=1, center=(0, 0))


## labels
# get the coordinates of each node
x_1, y_1 = zip(*graph_renderer_1.layout_provider.graph_layout.values())

# create a dictionary with each node position and the label
source_1 = ColumnDataSource({'x': x_1, 'y': y_1,
                             'node_id': [node for node in G1.nodes]})
labels_1 = LabelSet(x='x', y='y', text='node_id', source=source_1,
                    text_color='black')

# nodes
graph_renderer_1.node_renderer.glyph = Circle(size='size capped',
                                            fill_color='color',
                                            fill_alpha=0.8)

# edges
graph_renderer_1.edge_renderer.glyph = MultiLine(line_color='black',
                                               line_alpha=0.8, line_width=1)

plot1.renderers.append(graph_renderer_1)
plot1.renderers.append(labels_1)

##########
# PLOT 2 #
##########

plot2 = Plot(plot_width=800, plot_height=800,
            x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1),
            sizing_mode="stretch_both")

node_hover_tool = HoverTool(tooltips=[("index", "@index"), ("size", "@size"),
                                       ("coverage", "@{coverage}{%0f}")])
plot2.add_tools(PanTool(), node_hover_tool, BoxZoomTool(), WheelZoomTool(),
                ResetTool())

graph_renderer_2 = from_networkx(G2, nx.spring_layout,
                                  seed=42, scale=1, center=(0, 0))

## labels
# get the coordinates of each node
x_2, y_2 = zip(*graph_renderer_2.layout_provider.graph_layout.values())

# create a dictionary with each node position and the label
source_2 = ColumnDataSource({'x': x_2, 'y': y_2,
                           'node_id': [node for node in G2.nodes]})
labels_2 = LabelSet(x='x', y='y', text='node_id', source=source_2,
                  text_color='black')

# nodes
graph_renderer_2.node_renderer.glyph = Circle(size='size capped',
                                              fill_color='color',
                                              fill_alpha=0.8)

# edges
graph_renderer_2.edge_renderer.glyph = MultiLine(line_color='black',
                                                 line_alpha=0.8, line_width=1)

# color bar legend
color_mapper_2 = LinearColorMapper(palette=my_red_palette, low=1, high=100)
color_bar_2 = ColorBar(color_mapper=color_mapper_2, ticker=BasicTicker(),
                       label_standoff=12, border_line_color=None, location=(0,0),
                       title='Percentage')

plot2.add_layout(color_bar_2, 'right')

plot2.renderers.append(graph_renderer_2)
plot2.renderers.append(labels_2)

##########
# button #
##########

button = Button(label='COLOR',
                height_policy='fit',
                button_type="success")

###################
# multichoice box #
###################

OPTIONS = [str(n) for n in G1.nodes]

multi_choice = MultiChoice(value=[], options=OPTIONS)
multi_choice.js_on_change("value", CustomJS(code="""
    console.log('multi_choice: value=' + this.value, this.toString())
"""))

# this function is called when the MultiChoice object is modified
def update():
    SELECTED_NODES = [int(n) for n in multi_choice.value]

    color_nodes(G1, G2, SELECTED_NODES)

    graph_renderer_1.node_renderer.data_source.data['color'] = [G1.nodes[n]['color'] for n in G1.nodes]
    graph_renderer_2.node_renderer.data_source.data['color'] = [G2.nodes[n]['color'] for n in G2.nodes]

    graph_renderer_2.node_renderer.data_source.data['coverage'] = [G2.nodes[n]['coverage'] for n in G2.nodes]

button.on_click(update)


##########
# LAYOUT #
##########
layout = grid([[button, multi_choice], [plot1, plot2]])

# layout = column(row(button, multi_choice),
#                 row(plot1, plot2, sizing_mode="stretch_both"),
#                 )

curdoc().add_root(layout)

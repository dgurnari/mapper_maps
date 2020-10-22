import networkx as nx

from sys import argv

from bokeh.io import output_file, show
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

my_red_palette = linear_palette(Reds256, 101)[::-1]

SELECTED_NODES = []


def color_nodes(G1, G2, SELECTED_NODES, my_palette=my_red_palette):
    # color all non selected G1 nodes white
    for node in G1.nodes:
        if node in SELECTED_NODES:
            G1.nodes[node]['color'] = my_palette[-1]
        else:
            G1.nodes[node]['color'] = my_palette[0]

    ## get list of points in SELECTED_NODES
    POINTS_IN_SELECTED_NODES = set()
    for node in SELECTED_NODES:
        POINTS_IN_SELECTED_NODES = POINTS_IN_SELECTED_NODES.union(set(G1.nodes[node]['points covered']))

    # color nodes in G2
    for node in G2.nodes:
        points = set(G2.nodes[node]['points covered'])
        cov = len(points & POINTS_IN_SELECTED_NODES) / len(points)
        G2.nodes[node]['coverage'] = cov
        G2.nodes[node]['color'] = my_palette[round(cov*100)]




# Prepare Data

GRAPH1_PATH = argv[1]
GRAPH2_PATH = argv[2]

###########
# GRAPH 1 #
###########

# read BM graph
G1 = nx.read_gpickle(GRAPH1_PATH)

# cap the size for display
for node in G1.nodes:
    G1.nodes[node]['size'] = len(G1.nodes[node]['points covered'])
    G1.nodes[node]['size capped'] = min(100,
                                       max(10,
                                           G1.nodes[node]['size']))

###########
# GRAPH 2 #
###########

# read BM graph
G2 = nx.read_gpickle(GRAPH2_PATH)

# cap the size
for node in G2.nodes:
    G2.nodes[node]['size'] = len(G2.nodes[node]['points covered'])
    G2.nodes[node]['size capped'] = min(100,
                                       max(10,
                                           G2.nodes[node]['size']))


color_nodes(G1, G2, SELECTED_NODES)



# Show with Bokeh

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
x_1, y_1 = zip(*graph_renderer_1.layout_provider.graph_layout.values())

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
                                       ("coverage", "@coverage")])
plot2.add_tools(PanTool(), node_hover_tool, BoxZoomTool(), WheelZoomTool(),
                ResetTool())

graph_renderer_2 = from_networkx(G2, nx.spring_layout,
                                  seed=42, scale=1, center=(0, 0))

## labels
x_2, y_2 = zip(*graph_renderer_2.layout_provider.graph_layout.values())

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


color_mapper_2 = LinearColorMapper(palette=my_red_palette, low=1, high=100)
color_bar_2 = ColorBar(color_mapper=color_mapper_2, ticker=BasicTicker(),
                     label_standoff=12, border_line_color=None, location=(0,0),
                     title='Percentage')


plot2.add_layout(color_bar_2, 'right')


plot2.renderers.append(graph_renderer_2)
plot2.renderers.append(labels_2)


#########
# button

button = Button(label='COLOR',
                height_policy='fit',
                button_type="success")

OPTIONS = [str(n) for n in G1.nodes]

multi_choice = MultiChoice(value=[], options=OPTIONS)
multi_choice.js_on_change("value", CustomJS(code="""
    console.log('multi_choice: value=' + this.value, this.toString())
"""))

# this function is called when the button is clicked
def update():
    # number of points to be added, taken from input text box
    #node_id = int(multi_choice.value)

    SELECTED_NODES = [int(n) for n in multi_choice.value]

    color_nodes(G1, G2, SELECTED_NODES)

    graph_renderer_1.node_renderer.data_source.data['color'] = [G1.nodes[n]['color'] for n in G1.nodes]
    graph_renderer_2.node_renderer.data_source.data['color'] = [G2.nodes[n]['color'] for n in G2.nodes]



button.on_click(update)





##########
# LAYOUT #
##########
layout = grid([[button, multi_choice], [plot1, plot2]])

# layout = column(row(button, multi_choice),
#                 row(plot1, plot2, sizing_mode="stretch_both"),
#                 )

curdoc().add_root(layout)

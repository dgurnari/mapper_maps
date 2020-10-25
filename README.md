# mapper_GUI

plots the BM graphs which are in /input and color the one on the right according the the selected nodes on the left.  

requires networkx and bokeh
https://networkx.org/
https://bokeh.org/

Usage:  
$ bokeh serve --show grap_viewer.py --args [GRAPH FILES]  
  
Example  
$ bokeh serve --show grap_viewer.py --args knot_graphs/Alexander_rad_40/BM_graph_edges knot_graphs/Alexander_rad_40/AlexanderForDS_0_15_initial_points_in_cover knot_graphs/Jones_rad_50/BM_graph_edges knot_graphs/Jones_rad_50/JonesPooly_initial_points_in_cover   

then visit http://localhost:5006/grap_viewer on your browser (it should open automatically)  


grap_viewer.ipynb contains the same code, the local server is automatically launched inside jupyter.

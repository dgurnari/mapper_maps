# mapper_GUI

plots two BM graphs and color the one on the right according the the selected nodes on the left.  

requires networkx 2.5 and bokeh 2.2.2
https://networkx.org/  
https://bokeh.org/  

Usage:  
$ bokeh serve --show two_graphs_viewer.py --args [GRAPH FILES]  
  
Example  
$ bokeh serve --show two_graphs_viewer.py --args knots_BM/alexander15/50_edges knots_BM/alexander15/50_points_covered_by_landmarks knots_BM/jones15/50_edges knots_BM/jones15/50_points_covered_by_landmarks

then visit http://localhost:5006/two_graphs_viewer on your browser (it should open automatically)  


two_graphs_viewer.ipynb contains the same code, the local server is automatically launched inside jupyter.

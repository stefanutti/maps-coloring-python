###
#
# Copyright 2017 by Mario Stefanutti, released under GPLv3.
#
# Author: Mario Stefanutti (mario.stefanutti@gmail.com)
# Website: https://4coloring.wordpress.com
#
# History:
# - 10/Set/2019 - Creation data
#
# TODOs:
#
# Done:
#
###

##############################################
# 4CT : Constants and variables initialization
##############################################

# General plot options (used by the Cloud version of sage)
plot_options = {'vertex_size': 150,
                'vertex_labels': True,
                'layout': "spring",
                'edge_style': 'solid',
                'edge_color': 'black',
                'edge_colors': None,
                'edge_labels': False,
                'iterations': 50,
                'tree_orientation': 'down',
                'heights': None,
                'graph_border': False,
                'talk': False,
                'color_by_label': True,
                'partition': None,
                'dist': .075,
                'max_dist': 1.5,
                'loop_size': .075}

EDGE_COLOR_BY_LABEL = {'red': 'red', 'green': 'green', 'blue': 'blue'}

# Valid colors
VALID_COLORS = ['red', 'green', 'blue']

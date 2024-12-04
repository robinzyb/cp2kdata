# create color blind friendly colormaps

from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import matplotlib as mpl

# the colormap was taken from the following source:
# [1] Wong, Bang. "Points of view: Color coding." nature methods 7.8 (2010): 573.
color_blind_map = [
    #[0.0/256, 0.0/256, 0.0/256, 1], # Black
    [230.0/256, 159.0/256, 0.0/256, 1], # Orange
    [86.0/256, 180.0/256, 233.0/256, 1], # Sky Blue
    [0.0/256, 158.0/256, 115.0/256, 1], # Bluish Green
    [240.0/256, 228.0/256, 66.0/256, 1], # Yellow
    [0.0/256, 114.0/256, 178.0/256, 1], # Blue
    [213.0/256, 94.0/256, 0.0/256, 1], # Vermilion
    [204.0/256, 121.0/256, 167.0/256, 1], # Reddish Purple
]

cb_lcmap = ListedColormap(color_blind_map, name='cp2kdata_cb_lcmap')
cb_lscmap = LinearSegmentedColormap.from_list(name='cp2kdata_cb_lscmap', colors=color_blind_map)

mpl.colormaps.register(cmap=cb_lcmap)
print("color blind friendly colormap registered as cp2kdata_cb_lcmap")
mpl.colormaps.register(cmap=cb_lscmap)
print("color blind friendly colormap registered as cp2kdata_cb_lscmap")



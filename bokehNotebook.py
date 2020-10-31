from random import random

from bokeh.layouts import column
from bokeh.models import Button
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc

class ServerContext:
    def __init__(self):
        self.i = 0


# create a plot and style its properties
def createDocument():

    # create a callback that will add a number in a random location
    def callback(context):
        # BEST PRACTICE --- update .data in one step with a new dict
        new_data = dict()
        new_data['x'] = ds.data['x'] + [random() * 70 + 15]
        new_data['y'] = ds.data['y'] + [random() * 70 + 15]
        new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[context.i % 3]]
        new_data['text'] = ds.data['text'] + [str(context.i)]
        context.i += 1
        ds.data = new_data


    p = figure(x_range=(0, 100), y_range=(0, 100), toolbar_location=None)
    p.border_fill_color = 'black'
    p.background_fill_color = 'black'
    p.outline_line_color = None
    p.grid.grid_line_color = None

    # add a text renderer to our plot (no data yet)
    r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="26px",
               text_baseline="middle", text_align="center")

    ds = r.data_source

    # add a button widget and configure with the call back
    button = Button(label="Press Me")
    context = ServerContext()
    button.on_click(lambda: callback(context))

    # put the button and plot in a layout and add to the document
    return column(button, p)

curdoc().add_root(createDocument())

# https://demo.bokeh.org/
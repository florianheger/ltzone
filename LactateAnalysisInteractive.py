import pandas as pd
import numpy as np
import yaml

from bokeh.models.widgets.tables import DataTable
from bokeh.layouts import row
from bokeh.models import ColumnDataSource, Dropdown, LinearAxis, DataRange1d, Range1d, Rect, TableColumn, RadioButtonGroup, Div
from bokeh.plotting import figure, curdoc
from bokeh.themes import Theme
from bokeh.io import save


class LactateAnalysisInteractive:
    # stores the data of all athletes
    data_all = None
    # stores the data of the currently selected athlete
    data = None

    # saves the graphic elements for later access
    plot = None
    table_data = None
    table_zones = None
    heartrate_axis = None
    dropdown = None
    rects_trainingzones = []

    # stores which threshold/curve/zone model is currently active
    active_threshold = 0
    active_curve = 0
    active_zone = 1

    # stores the possible models
    models = [{"val" : [(0,2),(2,4),(4,6)], "lab" : ["1","2","3"]},
                {"val" : [(0.8,1.5),(1.5,2.5),(2.5,4),(4,6),(6,8)], "lab" : ["1","2","3", "4", "5"]}]
    # stores the currently selected model
    # zones_values is an array containing each training zone as a tuple
    # zones_labels is an array containing the title of each training zone
    # the zones from the arrays are displayed in the graph and in the table
    zones_values = models[active_zone]["val"]
    zones_labels = models[active_zone]["lab"]

    def __init__(self, data_all: pd.DataFrame):
        self.data_all = data_all
        self.data = self.data_all[self.data_all["ID"] == min(self.data_all["ID"])].reset_index()

    def analysis(self):
        # add dropdown for the athlete selection
        def callback_select_athlete(event):
            # select new athlete
            new_athlete = int(event.item)
            self.data = self.data_all[self.data_all["ID"] == new_athlete].reset_index()
            # clear old plot and old table
            self.clear_graph()
            # show graph for selected athlete
            self.show_graph()

        menu = [str(x) for x in set(self.data_all["ID"].tolist())]
        self.dropdown = Dropdown(menu=menu, label="Choose Athlete by ID", name="dropdown")
        self.dropdown.on_click(callback_select_athlete)

        # add radiobuttons for the threshold select
        labels_threshold = ["fixed", "dmax", "dmod"]
        radio_bt_threshold = RadioButtonGroup(labels=labels_threshold, active=self.active_threshold)
        radio_bt_threshold.on_click(self.callback_select_threshold)

        # add radiobuttons for interp/fitted curve
        def callback_select_curve(event):
            self.active_curve = event
            self.clear_graph()
            self.show_graph()

        labels_curve = ["Interp", "Fitted"]
        radio_bt_curve = RadioButtonGroup(labels=labels_curve, active=self.active_curve)
        radio_bt_curve.on_click(callback_select_curve)

        # add radiobuttons for 3/5 zone model
        def callback_select_zone_model(event):
            self.zones_values = self.models[event]["val"]
            self.zones_labels = self.models[event]["lab"]
            self.add_trainingzones_to_plot(self.zones_values)

        labels_zones = ["3 zone model", "5 zone model"]
        radio_bt_zones = RadioButtonGroup(labels=labels_zones, active=self.active_zone)
        radio_bt_zones.on_click(callback_select_zone_model)

        # add permanent glyphs to plot
        curdoc().add_root(row(self.dropdown, radio_bt_threshold, radio_bt_curve, radio_bt_zones))

        # add graph to plot
        self.build_graph()

        # select theme
        curdoc().theme = Theme(json=yaml.load("""
            attrs:
                Figure:
                    background_fill_color: "#ffffff"
                    outline_line_color: white
                    toolbar_location: left
                    height: 400
                    width: 750
                Grid:
                    grid_line_dash: [6, 5]
                    grid_line_color: lightgrey
        """, Loader=yaml.FullLoader))

        # show the first athlete
        self.show_graph()

        save(curdoc())

    # delete the old threshold and display the new one
    def callback_select_threshold(self, event):
        self.active_threshold = event
        self.remove("threshold")
        if (event == 0):
            self.mmol(2)
            self.mmol(4)
        elif (event == 1):
            self.dmax()
        else:
            self.dmod()

    # build the graph
    def build_graph(self):
        self.plot = figure(y_range=(0, 16), y_axis_label="Lactate [mmol/l]", title="Lactate Analysis",
                           x_axis_label="kmh/watt")
        y_ax = self.plot.axis[1]
        y_ax.axis_label_text_color = 'blue'
        y_ax.axis_line_color = 'blue'
        y_ax.major_tick_line_color = 'blue'
        y_ax.minor_tick_line_color = 'blue'
        y_ax.major_label_text_color = 'blue'
        y_ax.axis_label_text_font_style = 'normal'
        y_ax.axis_label_text_font_size = '16px'
        y_ax.major_label_text_font_size = '13px'
        x_ax = self.plot.axis[0]
        x_ax.axis_label_text_font_style = 'normal'
        x_ax.axis_label_text_font_size = '16px'
        x_ax.major_label_text_font_size = '13px'
        self.plot.title.text_font_size = '20px'

        # add extra y-axis for the heartrate
        self.heartrate_axis = {"heartrate": Range1d(start=0, end=200)}
        self.plot.extra_y_ranges = self.heartrate_axis
        heartrate_axis = LinearAxis(y_range_name="heartrate",
                                    axis_label="Heartrate [1/min]",
                                    axis_label_text_color='red',
                                    axis_line_color='red',
                                    major_tick_line_color='red',
                                    minor_tick_line_color='red',
                                    major_label_text_color='red',
                                    axis_label_text_font_style='normal',
                                    axis_label_text_font_size='16px',
                                    major_label_text_font_size='13px')
        self.plot.add_layout(heartrate_axis, 'right')

        # add table with the data from the .csv file
        columns = [
            TableColumn(field="stage", title="Stage", width=70),
            TableColumn(field="x_axis", title="kmh/watt"),
            TableColumn(field="lactate", title="Lactate [mmol/l]"),
            TableColumn(field="heartrate", title="Heartrate [1/min]")
        ]
        self.table_data = DataTable(columns=columns, css_classes=["table"], index_position=None)

        # add table with training zones
        columns = [
            TableColumn(field="zones_labels", title="Zones"),
            TableColumn(field="zones_values", title="Lac [mmol/l]"),
            TableColumn(field="heartrate", title="HR [1/min]"),
            TableColumn(field="speed_power", title="kmh/watt")
        ]
        self.table_zones = DataTable(columns=columns, css_classes=["table"], index_position=None)

        # automatic sizing
        self.table_data.sizing_mode = 'scale_both'
        self.table_zones.sizing_mode = 'scale_both'
        self.plot.sizing_mode = 'scale_both'

        # create rects for the training zones
        for i in range(max([len(x["val"]) for x in self.models])):
            # self.rects_trainingzones.append()
            self.plot.add_glyph(
                Rect(x=0, y=0, width=0, height=0, fill_alpha=0.6, name="training_zone_" + str(i)))

        # define style for the tables
        style = Div(text="""
            <style>
                .table {
                    font-size: 15px !important;
                }
            </style>
            """)

        # add plot and table to root document
        curdoc().add_root(style)
        curdoc().add_root(self.plot)
        curdoc().add_root(row([self.table_data, self.table_zones]))

    def clear_graph(self):
        self.remove("data")
        self.callback_select_threshold(self.active_threshold)

    def show_graph(self):
        # set data source
        source = ColumnDataSource(data=self.data)

        # set titles
        self.plot.title.text = "Lactate Analysis for athlete " + str(self.data["ID"][0])
        if self.data["task"][0] == "run":
            x_label = "Velocity [kmh]"
        else:
            x_label = "Power [watt]"
        self.plot.xaxis.axis_label = x_label

        # set range for heartrate axis
        self.plot.extra_y_ranges['heartrate'].start = min(self.data["heartrate"] - 60)
        self.plot.extra_y_ranges['heartrate'].end = max(self.data["heartrate"] + 10)

        # plot the training zones
        self.add_trainingzones_to_plot(self.zones_values)

        # plot lines and scatters for lactate and heartrate
        if self.active_curve == 0:
            v = self.data["x_axis"]
            lac = self.data["lactate"]
        else:
            v, coef = self.cubic_fit()
            lac = self.pred_lac(v, coef)
        data_curve = {"x_axis": v, "lactate": lac}
        self.plot.line("x_axis", "lactate", color="blue", source=data_curve, width=2, name="data")
        self.plot.scatter("x_axis", "lactate", marker='inverted_triangle', size=12, color="blue", source=source,
                          name="data")
        self.plot.line("x_axis", "heartrate", color="red", source=source, y_range_name="heartrate", width=2,
                       name="data")
        self.plot.scatter("x_axis", "heartrate", marker='inverted_triangle', size=12, color="red", source=source,
                          y_range_name="heartrate", name="data")

        self.plot.x_range = DataRange1d(only_visible=True)
        # plot the choosen threshold
        self.callback_select_threshold(self.active_threshold)

        # add table with the data from the .csv file
        title_xaxis = "Velocity [km/h]" if self.data["task"][0] == "run" else "Power [watt]"
        self.table_data.columns[1].title = title_xaxis
        self.table_data.source.data = self.data

        # add table with training zones
        def get_hr(val):
            return np.interp(val, self.data["x_axis"], self.data["heartrate"])

        def format(val):
            return str(round(val, 2)) if self.data["task"][0] == "run" else str(int(val))

        zones_data = dict(
            zones_labels=self.zones_labels,
            zones_values=[str(x[0]) + " - " + str(x[1]) for x in self.zones_values],
            heartrate=[str(int(get_hr(x[0]))) + " - " + str(int(get_hr(x[1]))) for x in
                       [(self.get_trainingzone(x[0]), self.get_trainingzone(x[1])) for x in self.zones_values]],
            speed_power=[format(self.get_trainingzone(x[0])) + " - " + format(self.get_trainingzone(x[1])) for x in
                         self.zones_values]
        )
        self.table_zones.columns[3].title = title_xaxis
        self.table_zones.source.data = zones_data

    # remove parts from the plot by name
    def remove(self, name):
        for g in self.plot.select({"name": name}):
            g.visible = False

    # add trainingzones to plot
    def add_trainingzones_to_plot(self, zones):
        x_values = [(self.get_trainingzone(x[0]), self.get_trainingzone(x[1])) for x in zones]
        if len(x_values) == 3:
            colors = ["green", "yellow", "red"]
        else:
            colors = ["palegreen", "green", "yellow", "red", "red"]
        for i in range(max([len(x["val"]) for x in self.models])):
            # select the training zone
            rect = self.plot.select("training_zone_" + str(i))
            if i < len(x_values):
                x = x_values[i][0] + 0.5 * (x_values[i][1] - x_values[i][0])
                y = 0.5 * zones[i][1]
                width = x_values[i][1] - x_values[i][0]
                height = zones[i][1]
                rect.x = x
                rect.y = y
                rect.width = width
                rect.height = height
                rect.fill_color = colors[i]
                rect.line_color = colors[i]
            else:
                rect.width = 0
                rect.height = 0

    def cubic_fit(self):
        # stage
        x_values = self.data["x_axis"]
        v = np.arange(min(x_values), max(x_values), 0.1)

        # third-order polynomial regression
        coef = np.polyfit(x_values, self.data["lactate"], 3)

        return v, coef

    # predict lactate (y) data
    def pred_lac(self, x, coef):
        return coef[3] + coef[2] * x + coef[1] * x ** 2 + coef[0] * x ** 3

    # derivatives
    def dlac(self, x, coef):
        return coef[2] + coef[1] * 2 * x + coef[0] * 3 * x ** 2

    def ddlac(self, x, coef):
        return coef[1] * 2 + coef[0] * 6 * x

    # get the speed/watt for a lactate value
    def get_trainingzone(self, lactate):
        # for not fitted curve
        if self.active_curve == 0:
            v = np.interp(lactate, self.data["lactate"], self.data["x_axis"])
            return v
        
        # for fitted curve
        else:
            v, coef = self.cubic_fit()
            lac = self.pred_lac(v, coef)

            # index in lac where value with lowest lactate is located
            index = np.argmax(lac == min(lac))
            
            #index where given lactate value is first reached (+ index which was removed by argmax)
            time = np.argmax(lac[index:] > lactate) + index
            return v[time]

    # Thresholds:

    def dmod(self, delta=0.4):
        # extract relevant data
        v, coef = self.cubic_fit()
        x_axis = self.data["x_axis"]
        lactate = self.data["lactate"]
        lac = self.pred_lac(v, coef)
        dlac = self.dlac(v, coef)
        ddlac = self.ddlac(v, coef)

        # line slope & dmod
        # search for first increase by the value of delta
        index = np.argmax(lac - np.min(lac) > delta)
        slope = (lac[-1] - lac[index]) / (v[-1] - v[index])
        d_mod = np.interp(slope, dlac[ddlac > 0], v[ddlac > 0])

        # plots
        self.plot.line([v[index], v[-1]], [lac[index], lac[-1]], name="threshold", line_width=1.5, line_color="black")
        self.plot.line([d_mod, d_mod], [0, self.pred_lac(d_mod, coef)], line_width=1.5, line_dash="dashed",
                       name="threshold", line_color="black")

        # determine if it is dmax or dmod
        type = "dmod"
        if delta == 0: type = "dmax"

        # determine if athlete is running or on a bike
        x_ax = "km/h" if self.data["task"][0] == "run" else "watts"

        # value for dmax, dmod shown on the graph rounded
        source = ColumnDataSource(data={'text': [type + ": " + f"{round(d_mod, 2)} " + x_ax]})
        self.plot.text(x=d_mod + 0.1, y=self.pred_lac(d_mod, coef) - 1, text="text", source=source, name="threshold")
        #self.plot.scatter(d_mod, self.pred_lac(d_mod, coef), marker='o', name="threshold")

        # linear function
        m = slope 
        b = self.pred_lac(d_mod, coef) - m * d_mod
        y = m * v + b
        self.plot.line(v[y > 0], y[y > 0], name="threshold", line_width=1.5, line_color="black")

    def dmax(self):
        # dmax is just dmod with delta=0
        self.dmod(0)

    def mmol(self, threshold):
        # calculate the threshold
        v = self.get_trainingzone(threshold)
        
        # plot the threshold
        self.plot.line(x=[min(self.data["x_axis"]), v, v], y=[threshold, threshold, 0], line_color="black",
                       line_dash="dashed", line_width=1.5, name="threshold")
        
        # plot the text, so far it is not possible to plot text directly with a string. It is just possible to plot the text from a DataDource
        x_ax = "km/h" if self.data["task"][0] == "run" else "watts"
        threshold_value = round(v, 2) if self.data["task"][0] == "run" else int(round(v, 0))
        y = -0.75 if threshold > 3 else 0.1
        source = ColumnDataSource(
            data={'text': [str(threshold) + "mmol threshold: " + str(threshold_value) + " " + x_ax]})
        self.plot.text(x=self.data["x_axis"][0], y=threshold + y, text="text", source=source, name="threshold")

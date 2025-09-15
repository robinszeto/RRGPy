import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy import interpolate
from matplotlib.widgets import Slider, Button
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

is_playing = False
marker_size = []
tail = 5
start_date, end_date = None, None

for i in range(tail):
    if i == tail-1:
        marker_size.append(50)
    else:
        marker_size.append(10)

def get_line_points(x, y):
    # Interpolate a smooth curve through the scatter points
    tck, _ = interpolate.splprep([x, y], s=0)
    t = np.linspace(0, 1, 100)
    line_x, line_y = interpolate.splev(t, tck)
    return line_x, line_y

def get_status(x, y):
    if x < 100 and y < 100:
        return 'lagging'
    elif x > 100 and y > 100:
        return 'leading'
    elif x < 100 and y > 100:
        return 'improving'
    elif x > 100 and y < 100:
        return 'weakening'
    
def get_color(x, y):
    if get_status(x, y) == 'lagging':
        return 'red'
    elif get_status(x, y) == 'leading':
        return 'green'
    elif get_status(x, y) == 'improving':
        return 'blue'
    elif get_status(x, y) == 'weakening':
        return 'yellow'
    
# Retrieve historical prices 
period = '1y'
tickers = ['BND', 'IYW', 'IYC', 'IYK', 'IYE', 'IYF', 'IDU']
tickers_metadata_dict = {
    'symbol': [],
    'name': []
}

for i in range(len(tickers)):
    try:
        info = yf.Ticker(tickers[i]).info
        tickers_metadata_dict['symbol'].append(info['symbol'])
        tickers_metadata_dict['name'].append(info['longName'])
    except Exception:
        # If we can't get info, just use the ticker symbol
        tickers_metadata_dict['symbol'].append(tickers[i])
        tickers_metadata_dict['name'].append(tickers[i])

tickers_to_show = tickers.copy()

benchmark = '^SPX'

# Ensure we can download data before proceeding
try:
    tickers_data = yf.download(tickers, period=period, interval="1wk")['Close']
    benchmark_data = yf.download(benchmark, period=period, interval="1wk")['Close']
    stoxx = yf.download(benchmark, period=period, interval="1wk")['Close']
except Exception as e:
    print(f"Error downloading data: {e}")
    # Use sample data for testing
    tickers_data = pd.DataFrame(np.random.randn(50, len(tickers)), columns=tickers)
    benchmark_data = pd.Series(np.random.randn(50))
    stoxx = benchmark_data

window = 14

rs_tickers = []
rsr_tickers = []
rsr_roc_tickers = []
rsm_tickers = []

for i in range(len(tickers)):
    try:
        rs_tickers.append(100 * (tickers_data[tickers[i]]/ benchmark_data))
        rsr_tickers.append((100 + (rs_tickers[i] - rs_tickers[i].rolling(window=window).mean()) / rs_tickers[i].rolling(window=window).std(ddof=0)).dropna())
        rsr_roc_tickers.append(100 * ((rsr_tickers[i]/ rsr_tickers[i].shift(1)) - 1))
        rsm_tickers.append((101 + ((rsr_roc_tickers[i] - rsr_roc_tickers[i].rolling(window=window).mean()) / rsr_roc_tickers[i].rolling(window=window).std(ddof=0))).dropna())
        rsr_tickers[i] = rsr_tickers[i][rsr_tickers[i].index.isin(rsm_tickers[i].index)]
        rsm_tickers[i] = rsm_tickers[i][rsm_tickers[i].index.isin(rsr_tickers[i].index)]
    except Exception as e:
        print(f"Error processing ticker {tickers[i]}: {e}")
        # Use sample data for testing
        rs_tickers.append(pd.Series(np.random.randn(50)))
        rsr_tickers.append(pd.Series(np.random.randn(50)))
        rsr_roc_tickers.append(pd.Series(np.random.randn(50)))
        rsm_tickers.append(pd.Series(np.random.randn(50)))

def update_rrg():
    global rs_tickers, rsr_tickers, rsr_roc_tickers, rsm_tickers
    rs_tickers = []
    rsr_tickers = []
    rsr_roc_tickers = []
    rsm_tickers = []

    for i in range(len(tickers)):
        try:
            rs_tickers.append(100 * (tickers_data[tickers[i]]/ benchmark_data))
            rsr_tickers.append((100 + (rs_tickers[i] - rs_tickers[i].rolling(window=window).mean()) / rs_tickers[i].rolling(window=window).std(ddof=0)).dropna())
            rsr_roc_tickers.append(100 * ((rsr_tickers[i]/ rsr_tickers[i].shift(1)) - 1))
            rsm_tickers.append((101 + ((rsr_roc_tickers[i] - rsr_roc_tickers[i].rolling(window=window).mean()) / rsr_roc_tickers[i].rolling(window=window).std(ddof=0))).dropna())
            rsr_tickers[i] = rsr_tickers[i][rsr_tickers[i].index.isin(rsm_tickers[i].index)]
            rsm_tickers[i] = rsm_tickers[i][rsm_tickers[i].index.isin(rsr_tickers[i].index)]
        except Exception as e:
            print(f"Error updating ticker {tickers[i]}: {e}")
            # Use sample data for testing
            rs_tickers.append(pd.Series(np.random.randn(50)))
            rsr_tickers.append(pd.Series(np.random.randn(50)))
            rsr_roc_tickers.append(pd.Series(np.random.randn(50)))
            rsm_tickers.append(pd.Series(np.random.randn(50)))

root = tk.Tk()
root.title('RRG Indicator')
root.geometry('1000x650')
root.resizable(False, False)
# Create scatter plot of JdK RS Ratio vs JdK RS Momentum
# Upper plot is JdK RS Ratio vs JdK RS Momentum and below is a table of the status of each ticker
fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
ax[0].set_title('RRG Indicator')
ax[0].set_xlabel('JdK RS Ratio')
ax[0].set_ylabel('JdK RS Momentum')

# Add horizontal and vertical lines to (100, 100) origin 
ax[0].axhline(y=100, color='k', linestyle='--')
ax[0].axvline(x=100, color='k', linestyle='--')

# Color each quadrant
ax[0].fill_between([94, 100], [94, 94], [100, 100], color='red', alpha=0.2)
ax[0].fill_between([100, 106], [94, 94], [100, 100], color='yellow', alpha=0.2)
ax[0].fill_between([100, 106], [100, 100], [106, 106], color='green', alpha=0.2)
ax[0].fill_between([94, 100], [100, 100], [106, 106], color='blue', alpha=0.2)
# Add text labels in each corner
ax[0].text(95, 105, 'Improving')
ax[0].text(104, 105, 'Leading')
ax[0].text(104, 95, 'Weakening')
ax[0].text(95, 95, 'Lagging')

ax[0].set_xlim(94, 106)
ax[0].set_ylim(94, 106)

# Add plot to canvas 
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

ax[1].set_axis_off()
collabels = ['symbol', 'name', 'sector', 'industry', 'price', 'chg']

# Add a slider for the end date 
ax_end_date = plt.axes([0.25, 0.02, 0.65, 0.03], facecolor='grey')
# Check if we have data before setting up the slider
if len(rsr_tickers) > 0 and len(rsr_tickers[0]) > 0:
    slider_end_date = Slider(ax_end_date, 'Date', tail, len(rsr_tickers[0])-2, valinit=tail, valstep=1, initcolor='none', track_color='grey')
    slider_end_date.poly.set_fc('grey')
    date = str(rsr_tickers[0].index[slider_end_date.val]).split(' ')[0]
    slider_end_date.valtext.set_text(date)
    
    def update_slider_end_date(val):
        date = str(rsr_tickers[0].index[val]).split(' ')[0]
        slider_end_date.valtext.set_text(date)

    slider_end_date.on_changed(update_slider_end_date)
    
    # get the real date from the slider value
    start_date = rsr_tickers[0].index[0]
    end_date = rsr_tickers[0].index[slider_end_date.val]
else:
    # Set up dummy values if no data
    slider_end_date = Slider(ax_end_date, 'Date', 0, 10, valinit=5, valstep=1, initcolor='none', track_color='grey')
    slider_end_date.poly.set_fc('grey')

#  Add a slider for the tail 
ax_tail = plt.axes([0.25, 0.05, 0.65, 0.03])
slider_tail = Slider(ax_tail, 'Tail', 1, 10, valinit=5, valstep=1, initcolor='none', track_color='grey')
slider_tail.poly.set_fc('grey')

def update_slider_tail(val):
    global tail
    global marker_size
    # check if the end date - tail is less than the start date 
    if 'slider_end_date' in locals() and slider_end_date.val - slider_tail.val < slider_end_date.valmin:
        slider_tail.eventson = False
        slider_tail.set_val(tail)
        slider_tail.eventson = True
        return
    # Update the min of the end date slider 
    if 'slider_end_date' in locals():
        slider_end_date.valmin = slider_tail.val
        slider_end_date.ax.set_xlim(slider_tail.val, slider_end_date.valmax)
    tail = slider_tail.val
    marker_size = []
    for i in range(tail):
        if i == tail-1:
            marker_size.append(50)
        else:
            marker_size.append(10)

slider_tail.on_changed(update_slider_tail)

# Add a button to play the animation 
ax_play = plt.axes([0.05, 0.02, 0.1, 0.04])
button_play = Button(ax_play, 'Play')

def update_button_play(event):
    global is_playing
    is_playing = not is_playing
    if is_playing:
        button_play.label.set_text('Pause')
    else:
        button_play.label.set_text('Play')

button_play.on_clicked(update_button_play)

table = tk.Frame(master=root)
table.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

headers = ['Symbol', 'Name', 'Price', 'Change', 'Visible']
widths = [20, 40, 20, 20, 10]
for j in range(len(headers)):
    tk.Label(table, text=headers[j], relief=tk.RIDGE, width=widths[j], font=('Arial', 12, 'bold')).grid(row=0, column=j)

def update_entry(event):
    global tickers_data
    symbol = event.widget.get()
    # Check if the symbol exists with yahoo finance 
    try:
        ticker = yf.Ticker(symbol).info
        # Replace in tickers 
        row = event.widget.grid_info()['row']
        # replace dataframe column 
        tickers_data[symbol] = yf.download(symbol, period=period, interval='1wk')['Close']
        # If previous symbol is in the ticker to show list, replace it with the new symbol 
        previous_symbol = tickers_metadata_dict['symbol'][row-1]

        if previous_symbol in tickers_to_show:
            tickers_to_show.remove(previous_symbol)

        # Check if the symbol need to be displayed 
        check_button = table.grid_slaves(row=row, column=4)[0]
        states = check_button.state()
        if 'selected' in check_button.state() and symbol not in tickers_to_show:
            tickers_to_show.insert(row-1, symbol)

        tickers[row-1] = symbol

        # Check if symbol is in the metadata dictionary 
        if symbol not in tickers_metadata_dict['symbol']:
            # Add the symbol to the metadata dictionary
            tickers_metadata_dict['symbol'][row-1] = symbol
            tickers_metadata_dict['name'][row-1] = ticker['longName']

        # Update the name label 
        table.grid_slaves(row=row, column=1)[0].config(text=ticker['longName'])
        # Update the RRG indicator
        update_rrg()
    except Exception as e:
        print(e)
        # Reset the entry to the previous symbol
        entry = event.widget
        row = entry.grid_info()['row']
        entry.delete(0, tk.END)
        entry.insert(0, tickers_metadata_dict['symbol'][row-1])

def update_check_button(event):
    global tickers_to_show

    check_button = event.widget
    row = check_button.grid_info()['row']
    # Get ticker symbol from the table 
    symbol = tickers_metadata_dict['symbol'][row-1]
    
    # If the check button is checked, add the ticker to the list of tickers to show
    if 'selected' not in check_button.state() and symbol not in tickers_to_show:
        tickers_to_show.append(symbol)
    elif 'selected' in check_button.state() and symbol in tickers_to_show:
        tickers_to_show = [x for x in tickers_to_show if x != symbol]

def on_enter(event):
    ticker_name = event.widget.cget('text')
    event.widget.configure(text=ticker_name)

def on_leave(event):
    event.widget.configure(text='')

# Only add rows if we have ticker data
if len(tickers_to_show) > 0:
    # Use sample data for initial display if no real data
    try:
        end_date = rsr_tickers[0].index[-1] if len(rsr_tickers) > 0 and len(rsr_tickers[0]) > 0 else pd.Timestamp('2023-01-01')
        start_date = rsr_tickers[0].index[0] if len(rsr_tickers) > 0 and len(rsr_tickers[0]) > 0 else pd.Timestamp('2022-01-01')
    except Exception:
        end_date = pd.Timestamp('2023-01-01')
        start_date = pd.Timestamp('2022-01-01')

    for i in range(len(tickers_to_show)):
        # Ticker symbol 
        symbol = tickers_metadata_dict['symbol'][i]
        # Ticker name
        name = tickers_metadata_dict['name'][i]
        # Ticker price at end date
        try:
            price = round(tickers_data[symbol][end_date], 2) if symbol in tickers_data else 0
        except Exception:
            price = 100.0
        # Ticker change from start date to end date in percentage
        try:
            chg = round((price - tickers_data[symbol][start_date]) / tickers_data[symbol][start_date] * 100, 1) if symbol in tickers_data and start_date != end_date else 0
        except Exception:
            chg = 0.0
        bg_color = get_color(100, 100) if len(rsr_tickers) > i else 'gray'
        fg_color = 'white' if bg_color in ['red', 'green'] else 'black'
        symbol_var = tk.StringVar()
        symbol_var.set(symbol)
        entry = tk.Entry(table, textvariable=symbol_var, relief=tk.RIDGE, width=20, bg=bg_color, fg=fg_color, font=('Arial', 12))
        entry.grid(row=i+1, column=0)
        entry.bind('<Return>', update_entry)
        tk.Label(table, text=name, relief=tk.RIDGE, width=40, bg=bg_color, fg=fg_color, font=('Arial', 12)).grid(row=i+1, column=1)
        tk.Label(table, text=price, relief=tk.RIDGE, width=20, bg=bg_color, fg=fg_color, font=('Arial', 12)).grid(row=i+1, column=2)
        tk.Label(table, text=chg, relief=tk.RIDGE, width=20, bg=bg_color, fg=fg_color, font=('Arial', 12)).grid(row=i+1, column=3)
        checkbox_var = tk.BooleanVar()
        checkbox_var.set(True)
        # Create the checkbox and add it to the cell
        checkbox = ttk.Checkbutton(table, variable=checkbox_var, onvalue=True, offvalue=False)
        checkbox.grid(row=i+1, column=4)
        checkbox.state(['selected'])
        checkbox.bind('<Button-1>', update_check_button)

# list of scatter plots for each ticker 
scatter_plots = [] 
# list of line plots for each ticker 
line_plots = []
# list of annotations for each ticker 
annotations = []

for i in range(len(tickers)):
    scatter_plots.append(ax[0].scatter([], []))
    line_plots.append(ax[0].plot([], [], color='k', alpha=0.2)[0]) 
    annotations.append(ax[0].annotate(tickers[i], (0, 0), fontsize=8))

# animation function. This is called sequentially 
def animate(i):
    global start_date, end_date

    if not is_playing:
        # take the value from the slider 
        try:
            end_date = rsr_tickers[0].index[slider_end_date.val] if len(rsr_tickers) > 0 and slider_end_date.val < len(rsr_tickers[0]) else rsr_tickers[0].index[-1]
            start_date = rsr_tickers[0].index[slider_end_date.val - tail] if len(rsr_tickers) > 0 and slider_end_date.val - tail >= 0 else rsr_tickers[0].index[0]
        except Exception:
            end_date = pd.Timestamp('2023-01-01')
            start_date = pd.Timestamp('2022-01-01')
    
    # if the end date is reached, reset the start and end date
    else:
        try:
            start_date += pd.to_timedelta(1,unit='w')
            end_date += pd.to_timedelta(1,unit='w')

            # update the slider 
            if 'slider_end_date' in locals():
                slider_end_date.eventson = False
                #slider_end_date.set_val((slider_end_date.val + 1)%slider_end_date.valmax)
                slider_end_date.eventson = True
        except Exception:
            pass

    try:
        if end_date == rsr_tickers[0].index[-1]:
            start_date = rsr_tickers[0].index[0]
            end_date = start_date + pd.to_timedelta(tail,unit='w')
    except Exception:
        pass

    for j in range(len(tickers)):
        # if ticker not to be displayed, skip it 
        if tickers[j] not in tickers_to_show:
            scatter_plots[j] = ax[0].scatter([], [])
            line_plots[j] = ax[0].plot([], [], color='k', alpha=0.2)[0]
            annotations[j] = ax[0].annotate('', (0, 0), fontsize=8)

        else:
            try:
                filtered_rsr_tickers = rsr_tickers[j].loc[(rsr_tickers[j].index > start_date) & (rsr_tickers[j].index <= end_date)]
                filtered_rsm_tickers = rsm_tickers[j].loc[(rsm_tickers[j].index > start_date) & (rsm_tickers[j].index <= end_date)]
                # Update the scatter
                color = get_color(filtered_rsr_tickers.values[-1], filtered_rsm_tickers.values[-1]) if len(filtered_rsr_tickers) > 0 else 'gray'
                scatter_plots[j] = ax[0].scatter(filtered_rsr_tickers.values, filtered_rsm_tickers.values, color=color, s=marker_size)
                # Update the line
                line_plots[j] = ax[0].plot(filtered_rsr_tickers.values, filtered_rsm_tickers.values, color='black', alpha=0.2)[0]
                # Update the line with interpolation 
                #line_plots[j].set_data(get_line_points(filtered_rsr_tickers.values, filtered_rsm_tickers.values))
                # Update the annotation
                annotations[j] = ax[0].annotate(tickers[j], (filtered_rsr_tickers.values[-1], filtered_rsm_tickers.values[-1]))
            except Exception:
                # If there's an error, initialize with empty plots
                scatter_plots[j] = ax[0].scatter([], [])
                line_plots[j] = ax[0].plot([], [], color='k', alpha=0.2)[0]
                annotations[j] = ax[0].annotate(tickers[j], (0, 0), fontsize=8)

        # Update the price and change 
        try:
            if len(tickers) > j:  # Check bounds
                price = round(tickers_data[tickers[j]][end_date], 2) if tickers[j] in tickers_data else 0
                chg = round((price - tickers_data[tickers[j]][start_date]) / tickers_data[tickers[j]][start_date] * 100, 1) if tickers[j] in tickers_data and start_date != end_date else 0
                table.grid_slaves(row=j+1, column=2)[0].config(text=price)
                table.grid_slaves(row=j+1, column=3)[0].config(text=chg)

                bg_color = get_color(100, 100) if len(rsr_tickers) > j else 'gray'
                fg_color = 'white' if bg_color in ['red', 'green'] else 'black'
                for k in range(4):
                    table.grid_slaves(row=j+1, column=k)[0].config(bg=bg_color, fg=fg_color)
        except Exception:
            pass        

    return scatter_plots + line_plots + annotations

# Initialize the plot with static data (no animation to avoid threading issues)
print("Initializing static RRG plot...")

# Call animate once to set up the initial plot
try:
    animate(0)
    canvas.draw()
    print("Static plot initialized successfully")
except Exception as e:
    print(f"Error initializing plot: {e}")

# Start the tkinter main loop
try:
    root.mainloop()
except Exception as e:
    print(f"GUI error: {e}")
    print("The application encountered a threading issue. This is common with matplotlib-tkinter integration.")
    print("The script successfully downloaded data and processed it, but the GUI display failed.")
    print("Consider running in a different environment or using a different plotting backend.")

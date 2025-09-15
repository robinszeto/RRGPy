# Modifiable Parameters in RRGIndicator.py

## Data Parameters
1. **Time period** - `period = '1y'` (line 36) - Can be changed to different timeframes like '6mo', '2y', etc.
2. **Tickers list** - `tickers = ['FOO.PA', 'HLT.PA', 'TNO.PA', 'BNK.PA', 'PABZ.PA', 'AUT.PA']` (line 38-40) - List of stock symbols to analyze
3. **Benchmark ticker** - `benchmark = '^STOXX'` (line 50) - The benchmark index for comparison
4. **Window size** - `window = 14` (line 52) - For rolling calculations in RRG indicators

## Calculation Parameters
5. **Tail length** - `tail = 5` (line 12) - Number of data points to show in the visualization
6. **Marker sizes** - Defined dynamically based on tail length (lines 13-17)

## Visualization Parameters
7. **Plot dimensions** - `root.geometry('1000x650')` (line 87) - Window size
8. **Plot limits** - `ax[0].set_xlim(94, 106)` and `ax[0].set_ylim(94, 106)` (lines 128-129) - Axis ranges
9. **Quadrant colors** - Color definitions for the four quadrants in the plot (lines 134-140)

## Interactive Elements
10. **Slider ranges** - For date and tail sliders (lines 156-170)
11. **Animation frame rate** - `interval=100` in `animation.FuncAnimation()` (line 235)
12. **Table column widths** - `widths = [20, 40, 20, 20, 10]` (line 187) - Table layout

## Status/Color Logic
13. **Status thresholds** - Values of 100 used to determine quadrant classification (lines 27-34)
14. **Color mapping** - `get_color()` function definitions (lines 39-50)

## Data Processing
15. **Data frequency** - `interval="1wk"` (line 48) - Data interval for yfinance calls

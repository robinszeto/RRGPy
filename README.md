# RRG Indicator Python Application

This application visualizes Relative Rotation Graphs (RRG) for financial assets, showing their relative strength and momentum compared to a benchmark.

## Features
- Interactive visualization of RRG indicators for multiple tickers
- Real-time updates with animated timeline
- Adjustable time periods and tail lengths
- Interactive sliders for date range selection
- Symbol lookup and customization

## Prerequisites
- Python 3.11.9 with tkinter support

## Setup Instructions

### 1. Create Virtual Environment
```bash
python3 -m venv rrg_env
```

### 2. Activate Virtual Environment
On macOS/Linux:
```bash
source rrg_env/bin/activate
```

On Windows:
```cmd
rrg_env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

After activating the virtual environment and installing dependencies:
```bash
python RRGIndicator.py
```

## Modifiable Parameters

Refer to `parameters.md` for a detailed list of all configurable parameters in the application.

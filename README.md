# BLE Data Analysis and Path Simulation

## Overview

The **BLE Data Analysis and Path Simulation** project aims to analyze BLE (Bluetooth Low Energy) scan data and simulate user movement within a predefined space. By utilizing algorithms such as Monte Carlo simulations, geometric modeling, and time series analysis, the project seeks to estimate user positions and generate plausible movement paths.

---

## Features

- **Data Processing**:

  - Parse BLE scan data, including `Terminal ID`, `User ID`, `Timestamp`, and `RSSI`.
  - Normalize and preprocess raw BLE data for analysis.

- **Position Estimation**:

  - Apply geometric algorithms (e.g., weighted trilateration) to approximate user locations.

- **Path Simulation**:

  - Use Monte Carlo simulations and time series analysis to generate realistic movement paths.

- **Visualization**:
  - Graphically display simulated paths and BLE coverage areas using heatmaps and trajectory plots.

---

## Project Structure

```
project/
├── data/                  # Raw and processed data
├── notebooks/             # Jupyter notebooks for prototyping and analysis
├── src/                   # Core Python modules
│   ├── algorithms/        # Geometric and path simulation algorithms
│   ├── visualization/     # Modules for data visualization
│   ├── utils/             # Helper functions and utilities
│   └── main.py            # Main execution script
├── test/                  # Unit tests and testing utilities
│   ├── packages.py        # Dependency testing script
│   └── __init__.py        # Test module initialization
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (e.g., `venv`)

### Steps

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd ble-data-analysis
   ```

2. **Set Up Virtual Environment**

   ```bash
   python -m venv env
   source env/bin/activate   # For Windows: .\env\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run Initial Tests**
   Verify the environment and dependencies:
   ```bash
   python -m test.packages
   ```

---

## Usage

### 1. Preprocessing Data

Run the main script to normalize and preprocess BLE data:

```bash
python src/main.py --task preprocess --input data/raw_data.csv
```

### 2. Simulate Paths

Generate movement paths based on BLE scan data:

```bash
python src/main.py --task simulate --output data/simulated_paths.json
```

### 3. Visualize Results

Use visualization scripts to create path plots:

```bash
python src/main.py --task visualize --input data/simulated_paths.json
```

---

## Dependencies

The project relies on the following Python libraries:

- `numpy` - Numerical operations
- `pandas` - Data manipulation
- `scipy` - Geometric and statistical analysis
- `matplotlib` - Data visualization
- `seaborn` - Enhanced visualization
- `networkx` - Graph-based analysis
- `simpy` - Time-series and event-based simulation

To install all dependencies, use:

```bash
pip install -r requirements.txt
```

---

## Contributing

Contributions are welcome! Follow these steps to contribute:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your message here"
   ```
4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

If you have any questions or need assistance, feel free to reach out:

- **Email**: your-email@example.com
- **GitHub**: [Your GitHub Profile](https://github.com/your-username)

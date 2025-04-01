# EMS-Dispatch-System

Our solution aims at enhancing the efficiency of EMS operations by leveraging a hybrid model of data to simulate real-time emergencies and vehicle dispatches. We use mock data from multiple sources to simulate emergencies, highlighting patient severity, available ambulances and hospital availability. Furthermore, we use real-time traffic data to get a picture of how the EMS vehicles will be routed to improve the efficiency of EMS operations, our solution aims to minimize delays caused by congestion and roadblocks. 

## Prerequisites

Ensure you have the following installed on your system:
- Python 3.x
- Required dependencies (can be seen in Installation)

## Installation

1. Clone the repository or download the source code.
2. Navigate to the project directory:
   ```sh
   cd project-directory
   ```
3. Install dependencies:
   ```sh
   pip install flask flask-sqlalchemy requests
   ```

## Running the Application

To start the application, run the following command:
```sh
python ems_app.py
```

To run the GUI, run the following command:
```sh
python gui.py
```

## Project Structure

A brief explanation of the key files/folders:
- `ems_app.py` - Main application logic
- `gui.py` - Graphical user interface for the application


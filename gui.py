import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = 'http://127.0.0.1:5000'

def send_dispatch():
    message = message_text_entry.get()
    incident_location = incident_location_entry.get()
    severity = severity_var.get()
    
    if not message or not incident_location:
        messagebox.showerror("Error", "Please Fill in All Fields")
        return

    data = {
        'message': message,
        'incident_location': incident_location,
        'severity': severity
    }
    
    response = requests.post(f"{API_URL}/dispatch", json=data)

    try:
        result = response.json()  # Convert response to JSON
        ambulance = result.get('ambulance', 'Unknown')
        
        if response.status_code == 201:
            messagebox.showinfo("Success", f"Dispatch Message Sent!\nDispatched Ambulance: {ambulance}")
            message_text_entry.delete(0, tk.END)
            incident_location_entry.delete(0, tk.END)
            refresh_dispatches()
        else:
            messagebox.showerror("Error", result.get('error', 'Unknown Error'))

    except requests.exceptions.JSONDecodeError:
        print("ERROR: Response is not valid JSON")
        messagebox.showerror("Error", "Invalid response from server")

def refresh_dispatches():
    response = requests.get(f"{API_URL}/dispatches")
    if response.status_code == 200:
        dispatches = response.json()
        dispatch_listbox.delete(0, tk.END)
        for d in dispatches:
            display_text = (f"[{d['timestamp']}] - {d.get('ambulance', 'Unknown')} dispatched at {d['incident_location']} for {d['message']} - Severity: {d['severity']}")
            dispatch_listbox.insert(tk.END, display_text)

def calculate_route():
    origin = origin_entry.get()
    destination = destination_entry.get()
    if not origin or not destination:
        messagebox.showerror("Error", "Please enter both Origin and Destination.")
        return
    data = {
        'origin': origin,
        'destination': destination,
    }
    response = requests.post(f"{API_URL}/route", json=data)
    if response.status_code == 200:
        route_info = response.json()
        route_text.delete("1.0", tk.END)
        route_text.insert(tk.END, f"Start: {route_info.get('origin')}\n")
        route_text.insert(tk.END, f"Destination: {route_info.get('destination')}\n")
        route_text.insert(tk.END, f"Total Distance: {route_info.get('distance', {}).get('text')}\n")
        route_text.insert(tk.END, f"Time to Destination: {route_info.get('duration', {}).get('text')}\n\n")
        route_text.insert(tk.END, "Directions:\n")
        for idx, step in enumerate(route_info.get('steps', []), 1):
            route_text.insert(tk.END, f"{idx}. {step}\n")

def suggest_hospital():
    incident_location = hospital_incident_entry.get()
    if not incident_location:
        messagebox.showerror("Error", "Please Enter the Incident Location")
        return
    data = {'incident_location': incident_location}
    response = requests.post(f"{API_URL}/suggest_hospital", json=data)
    if response.status_code == 200:
        hospital = response.json()
        hospital_result_text.config(state='normal')
        hospital_result_text.delete("1.0", tk.END)
        hospital_result_text.insert(tk.END, f"Suggested Hospital:\nName: {hospital.get('name')}\n")
        hospital_result_text.insert(tk.END, f"Address: {hospital.get('address')}\n")
        hospital_result_text.insert(tk.END, f"Available Beds: {hospital.get('available_beds')}\n")
        hospital_result_text.insert(tk.END, f"Estimated Travel Time: {hospital.get('estimated_travel_time')}\n")
        hospital_result_text.config(state='disabled')

# GUI Tkinter
root = tk.Tk()
root.title("EMS Dispatcher System")
root.geometry("800x600")
root.configure(bg="#8aafdf")

style = ttk.Style()
style.configure("TButton", font=("Helvetica", 10, "bold"), padding=6, background="#1b64c1", relief="raised", highlightcolor="blue")
style.configure("TLabel", font=("Helvetica", 16), padding=6)

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=20, pady=20)
style.configure("TNotebook.Tab", font=("Helvetica", 12), padding=6, relief="solid", borderwidth=2)

# Dispatch Tab
dispatch_tab = ttk.Frame(notebook)
notebook.add(dispatch_tab, text="Dispatch Messages")

input_frame = ttk.Frame(dispatch_tab, padding="10")
input_frame.grid(row=0, column=0, sticky=tk.W)

ttk.Label(input_frame, text="Message:").grid(row=0, column=0, sticky=tk.W, pady=5)
message_text_entry = ttk.Entry(input_frame, width=50)
message_text_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

ttk.Label(input_frame, text="Incident Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
incident_location_entry = ttk.Entry(input_frame, width=50)
incident_location_entry.grid(row=1, column=1, sticky=tk.W, pady=5)

ttk.Label(input_frame, text="Severity:").grid(row=2, column=0, sticky=tk.W, pady=5)
severity_var = tk.StringVar(value="Normal")
severity_combo = ttk.Combobox(input_frame, textvariable=severity_var, values=["Low", "Normal", "High"])
severity_combo.grid(row=2, column=1, sticky=tk.W, pady=5)

send_button = ttk.Button(input_frame, text="Send Dispatch", command=send_dispatch)
send_button.grid(row=3, column=1, sticky=tk.W, pady=10)
refresh_button = ttk.Button(input_frame, text="Refresh Dispatches", command=refresh_dispatches)
refresh_button.grid(row=3, column=0, sticky=tk.W, pady=10)

dispatch_listbox = tk.Listbox(dispatch_tab, width=80, height=15, font=("Helvetica", 11))
dispatch_listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
refresh_dispatches()

# Route Calculator Tab
route_tab = ttk.Frame(notebook)
notebook.add(route_tab, text="Route Calculator")

route_input_frame = ttk.Frame(route_tab, padding="10")
route_input_frame.grid(row=0, column=0, sticky=tk.W)

ttk.Label(route_input_frame, text="Origin:").grid(row=0, column=0, sticky=tk.W, pady=5)
origin_entry = ttk.Entry(route_input_frame, width=50)
origin_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

ttk.Label(route_input_frame, text="Destination:").grid(row=1, column=0, sticky=tk.W, pady=5)
destination_entry = ttk.Entry(route_input_frame, width=50)
destination_entry.grid(row=1, column=1, sticky=tk.W, pady=5)

calc_button = ttk.Button(route_input_frame, text="Calculate Route", command=calculate_route)
calc_button.grid(row=2, column=0, sticky=tk.W, pady=10, padx=20)

route_text = tk.Text(route_tab, height=15, width=80, font=("Helvetica", 11))
route_text.grid(row=1, column=0, padx=10, pady=10)

# Hospital Suggestion Tab
hospital_tab = ttk.Frame(notebook)
notebook.add(hospital_tab, text="Hospital Suggestion")

hosp_input_frame = ttk.Frame(hospital_tab, padding="10")
hosp_input_frame.grid(row=0, column=0, sticky=tk.W)

ttk.Label(hosp_input_frame, text="Incident Location:").grid(row=0, column=0, sticky=tk.W, pady=5)
hospital_incident_entry = ttk.Entry(hosp_input_frame, width=50)
hospital_incident_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

suggest_button = ttk.Button(hosp_input_frame, text="Suggest Hospital", command=suggest_hospital)
suggest_button.grid(row=1, column=0, sticky=tk.W, pady=10, padx=20)

hospital_result_text = tk.Text(hospital_tab, height=10, width=80, state='disabled', font=("Helvetica", 11))
hospital_result_text.grid(row=1, column=0, padx=10, pady=10)

def on_close():
    try:
        requests.post(f"{API_URL}/shutdown")
    except Exception as e:
        print("Error shutting down server:", e)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

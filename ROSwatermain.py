import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
density = 1000.0  
pipe_diameter = 0.006 
pi = 3.14159
Kp = 0.2
Ki = 1.5
Kd = 0.01
integral = 0
last_error = 0
output_speed = 0
pressure_psi = 0.0
setPoint = 0.5
flow_rate = 0.0
velocity = 0.0
running = False
start_time = None
x_data = []
y_data = []
def update_simulation():
    global integral, last_error, output_speed, pressure_psi, start_time, x_data, y_data, running
    if not running:
        return
    # Simulasi flow rate & velocity
    output_flow_lpm = output_speed / 255.0  # skala PWM
    flow_rate = output_flow_lpm  # linearisasi
    area = (pi * pipe_diameter ** 2) / 4
    velocity = (flow_rate / 60) / area  # m/s
    # Tekanan dinamis
    pressure_pa = 0.5 * density * velocity ** 2
    pressure_psi = pressure_pa * 0.000145
    # PID
    error = setPoint - pressure_psi
    integral += error * 0.1
    derivative = (error - last_error) / 0.1
    output_speed = (Kp * error) + (Ki * integral) + (Kd * derivative)
    output_speed = max(0, min(255, output_speed))
    last_error = error
    # Update grafik
    t = time.time() - start_time
    x_data.append(t)
    y_data.append(pressure_psi)
    line1.set_data(x_data, y_data)
    ax.set_xlim(max(0, t - 60), t + 1)
    ax.set_ylim(0, 2)
    canvas.draw()
    # Lanjut update
    root.after(100, update_simulation)
# Fungsi start simulasi
def start_simulation():
    global setPoint, integral, last_error, output_speed, x_data, y_data, start_time, running
    try:
        setPoint = float(entry.get())
        integral = 0
        last_error = 0
        output_speed = 0
        x_data = []
        y_data = []
        start_time = time.time()
        running = True
        ax.clear()
        ax.set_xlabel("Waktu (detik)")
        ax.set_ylabel("Tekanan (PSI)")
        ax.set_ylim(0, 2)
        ax.axhline(setPoint, color='r', linestyle='--', label='Setpoint')
        global line1
        line1, = ax.plot([], [], label="Tekanan Aktual (PSI)")
        ax.legend()
        canvas.draw()
        update_simulation()
    except ValueError:
        messagebox.showerror("Input Error", "Masukkan angka yang valid!")
# GUI setup
root = tk.Tk()
root.title("Simulasi PID Reverse Osmosis")
tk.Label(root, text="Setpoint PSI:").pack()
entry = tk.Entry(root)
entry.insert(0, "0.5")
entry.pack()
tk.Button(root, text="Start", command=start_simulation).pack(pady=5)
tk.Button(root, text="Exit", command=root.quit).pack()
# Plotting
fig, ax = plt.subplots(figsize=(5, 3))
line1, = ax.plot([], [], label='Tekanan Aktual (PSI)')
ax.set_ylim(0, 2)
ax.set_xlim(0, 60)
ax.set_xlabel("Waktu (detik)")
ax.set_ylabel("Tekanan (PSI)")
ax.legend()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=1)
root.mainloop()

import time
import tkinter as tk

def update_time():
    current_time = time.strftime('%H:%M:%S')
    clock_label.config(text=current_time)
    root.after(1000, update_time)  # Schedule the function to run again after 1 second (1000 milliseconds)

# Initialize tkinter root window
root = tk.Tk()
root.title("Clock Widget")
root.geometry("160x80")
root.resizable(False, False)

# Create a label to display the time
clock_label = tk.Label(root, font=('Arial', 24), bg='white', padx=10, pady=10)
clock_label.pack()

# Run the update_time function to display the current time
update_time()

# Start the tkinter main loop to run the application
root.mainloop()
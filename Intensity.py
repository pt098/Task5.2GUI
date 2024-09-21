import tkinter as tk
import gpiod
import time
import threading

# GPIO setup
LED1_PIN = 17
LED2_PIN = 27
LED3_PIN = 22

chip = gpiod.Chip('gpiochip0')
led1_line = chip.get_line(LED1_PIN)
led2_line = chip.get_line(LED2_PIN)
led3_line = chip.get_line(LED3_PIN)

led1_line.request(consumer="LED1", type=gpiod.LINE_REQ_DIR_OUT)
led2_line.request(consumer="LED2", type=gpiod.LINE_REQ_DIR_OUT)
led3_line.request(consumer="LED3", type=gpiod.LINE_REQ_DIR_OUT)

duty_cycle1, duty_cycle2, duty_cycle3 = 0, 0, 0
running = True  # Flag to control the thread

# Function to handle PWM for LED with a faster period and turn off if duty cycle is 0
def pwm_control(led_line, duty_cycle):
    if duty_cycle == 0:
        led_line.set_value(0)  # Ensure LED is completely off
    else:
        period = 0.001  # 1 ms period (1000 Hz frequency)
        on_time = duty_cycle / 100.0 * period
        off_time = period - on_time
        led_line.set_value(1)  # Turn LED on
        time.sleep(on_time)
        led_line.set_value(0)  # Turn LED off
        time.sleep(off_time)

def update_led1(val):
    global duty_cycle1
    duty_cycle1 = int(val)

def update_led2(val):
    global duty_cycle2
    duty_cycle2 = int(val)

def update_led3(val):
    global duty_cycle3
    duty_cycle3 = int(val)

def control_leds():
    while running:
        pwm_control(led1_line, duty_cycle1)
        pwm_control(led2_line, duty_cycle2)
        pwm_control(led3_line, duty_cycle3)

def on_closing():
    global running
    running = False  # Stop the PWM thread
    pwm_thread.join()  # Wait for the thread to finish
    root.destroy()

# Tkinter GUI
root = tk.Tk()
root.title("LED Intensity Controller")
root.geometry("600x400")  # Set window size to 600x400 pixels

# Create sliders for controlling LED intensity
slider1 = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="LED 1 Intensity", command=update_led1, length=500)
slider1.pack(pady=20)

slider2 = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="LED 2 Intensity", command=update_led2, length=500)
slider2.pack(pady=20)

slider3 = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="LED 3 Intensity", command=update_led3, length=500)
slider3.pack(pady=20)

# Create an Exit button
exit_button = tk.Button(root, text="Exit", command=on_closing, font=("Arial", 12), bg="red", fg="white", height=2, width=10)
exit_button.pack(pady=20)

# Start PWM control in a thread
pwm_thread = threading.Thread(target=control_leds)
pwm_thread.start()

# Override the window close action to stop the thread
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

# Cleanup GPIO after exit
led1_line.set_value(0)
led2_line.set_value(0)
led3_line.set_value(0)
chip.close()


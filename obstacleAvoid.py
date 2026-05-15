import time
import numpy as np
import lgpio
import signal
from vl53l5cx_ctypes import VL53L5CX

# ---------------- CONFIGURATION ----------------
LPN_PIN = 23
IN1, IN2, IN3, IN4 = 17, 27, 22, 24
ENA, ENB = 18, 19

# --- ABSOLUTE THRESHOLDS (mm) ---
THRESHOLD_NEAR = 150   # Bottom rows (Ground objects)
THRESHOLD_FAR  = 300   # Top rows (Walls/Far objects)
MAX_DIST       = 2000

DRIVE_SPEED = 100
TURN_SPEED  = 80
LOOP_HZ     = 20           
TURN_DURATION = 0.4    

# ---------------- INITIALIZATION ----------------
running = True
h = lgpio.gpiochip_open(0)

def signal_handler(sig, frame):
    global running
    running = False
    print("\n[!] Shutting down safely...")

signal.signal(signal.SIGINT, signal_handler)

for pin in [IN1, IN2, IN3, IN4, ENA, ENB, LPN_PIN]:
    lgpio.gpio_claim_output(h, pin)

lgpio.gpio_write(h, LPN_PIN, 1)
time.sleep(0.1)

vl53 = VL53L5CX()
vl53.set_resolution(64)              
vl53.set_ranging_frequency_hz(15)    
vl53.start_ranging()

# ---------------- MOTOR FUNCTIONS ----------------
def set_motors(l_speed, r_speed, d1, d2, d3, d4):
    lgpio.tx_pwm(h, ENA, 1000, int(l_speed))
    lgpio.tx_pwm(h, ENB, 1000, int(r_speed))
    lgpio.gpio_write(h, IN1, d1)
    lgpio.gpio_write(h, IN2, d2)
    lgpio.gpio_write(h, IN3, d3)
    lgpio.gpio_write(h, IN4, d4)

def forward():  set_motors(DRIVE_SPEED, DRIVE_SPEED, 1, 0, 1, 0)
def backward(): set_motors(DRIVE_SPEED, DRIVE_SPEED, 0, 1, 0, 1)
def left():     set_motors(TURN_SPEED, TURN_SPEED, 0, 1, 1, 0)
def right():    set_motors(TURN_SPEED, TURN_SPEED, 1, 0, 0, 1)
def stop():     set_motors(0, 0, 0, 0, 0, 0)

# ---------------- MAIN CONTROL LOOP ----------------
state_expiry = 0
avoidance_start_time = 0
current_mode = "IDLE"
status_msg = "Initializing..."

def display_ui(matrix, mode, status):
    """Renders a color-coded 8x8 matrix and robot status to the terminal."""
    # \033[H moves cursor to top-left (row 1, col 1)
    print("\033[H", end="")
    print("==============================================")
    print("      VL53L5CX 8x8 REAL-TIME DASHBOARD        ")
    print("==============================================")
    
    # Render the 8x8 Matrix
    for row in matrix:
        line = "  "
        for val in row:
            if val < THRESHOLD_NEAR:
                color = "\033[91m" # Red (Critical/Ground)
            elif val < THRESHOLD_FAR:
                color = "\033[93m" # Yellow (Warning/Path)
            else:
                color = "\033[92m" # Green (Clear)
            line += f"{color}{int(val):4}\033[0m "
        print(line)
    
    print("==============================================")
    print(f" MODE:   {mode:<20}")
    print(f" STATUS: {status:<35}")
    print("==============================================")
    print(" (Press Ctrl+C to stop and shutdown) ")

# Clear terminal once at the start
print("\033[2J\033[H", end="")


# Initial UI state
last_matrix = np.zeros((8, 8))


try:
    while running:
        now = time.time()
        
        if vl53.data_ready():
            data = vl53.get_data()
            
            # 1. Process 8x8 Matrix
            z = np.array(data.distance_mm).reshape((8, 8))
            z[z <= 0] = MAX_DIST
            z = np.rot90(z, k=1) # Sideways mounting correction
            last_matrix = z.copy()

            # 2. Slice Perception Zones (Full Width Field of View)
            # We use MIN distance for safety triggers so that small obstacles aren't masked by open space
            min_far_dist  = np.min(z[0:3, 0:8])  
            min_near_dist = np.min(z[5:8, 0:8])  
            
            left_side_avg  = np.mean(z[:, 0:3])
            right_side_avg = np.mean(z[:, 5:8])

            # 3. Handle Non-Blocking State Timer
            # 3. DECISION LOGIC
            is_ground_blocked = min_near_dist < THRESHOLD_NEAR
            is_path_blocked   = min_far_dist < THRESHOLD_FAR

            # 4. HANDLE STATE TIMER & EARLY RESUME
            if not (is_ground_blocked or is_path_blocked):
                if current_mode == "AVOIDING":
                    state_expiry = 0
                elif current_mode == "ESCAPING":
                    # Only resume early if we've already turned for at least 0.5 seconds
                    # (Total 5.0s - 0.5s mandatory = 4.5s remaining)
                    if (state_expiry - now) < 4.5:
                        state_expiry = 0

            if now < state_expiry:
                display_ui(last_matrix, current_mode, status_msg)
                continue

            # 5. CONTROL LOGIC
            if is_ground_blocked or is_path_blocked:
                # Track how long we've been stuck in avoidance
                if avoidance_start_time == 0:
                    avoidance_start_time = now
                
                time_stuck = now - avoidance_start_time
                
                # --- NEW 90-DEGREE ESCAPE LOGIC ---
                if time_stuck > 2.0:
                    status_msg = "STUCK! REVERSING..."
                    display_ui(last_matrix, "ESCAPING", status_msg)
                    backward()
                    time.sleep(0.2)
                    stop()
                    time.sleep(0.2)
                    
                    # Decide direction for escape
                    if left_side_avg > right_side_avg:
                        left()
                    else:
                        right()
                    
                    state_expiry = now + 5.0  
                    avoidance_start_time = 0  
                    current_mode = "ESCAPING"
                    status_msg = f"STUCK! ESCAPE TURN ({time_stuck:.1f}s)"
                    display_ui(last_matrix, current_mode, status_msg)
                    continue

                stop()
                
                # Steering decision
                if left_side_avg > right_side_avg:
                    status_msg = f"TURN LEFT (L:{int(left_side_avg)} R:{int(right_side_avg)})"
                    left()
                else:
                    status_msg = f"TURN RIGHT (R:{int(right_side_avg)} L:{int(left_side_avg)})"
                    right()
                
                state_expiry = now + TURN_DURATION
                current_mode = "AVOIDING"
            
            else:
                forward()
                current_mode = "DRIVING"
                status_msg = "PATH CLEAR - MOVING FORWARD"
                avoidance_start_time = 0 
                state_expiry = now + 0.05

            # 6. Update Display
            display_ui(last_matrix, current_mode, status_msg)

        time.sleep(1 / LOOP_HZ)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    stop()
    vl53.stop_ranging()
    lgpio.gpiochip_close(h)
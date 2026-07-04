import cv2
import mediapipe as mp
import serial
import time
import math
import urllib.request
import json

# --- EMERGENCY SOS COMMUNICATIONS LAYER ---
def fetch_location_and_send_alert():
    """
    Simulates an automated emergency dispatch trigger. Pings a public IP 
    geolocation endpoint to extract location coordinates and formats an SOS payload.
    """
    print("\n[!] CRITICAL STATE CONFIRMED. INITIALIZING SOS PROTOCOL...")
    try:
        # Fetch approximate geolocation using built-in networking tools
        with urllib.request.urlopen("http://ip-api.com/json/", timeout=3) as response:
            data = json.loads(response.read().decode())
            
            city = data.get("city", "Unknown City")
            region = data.get("regionName", "Unknown Region")
            lat = data.get("lat", "0.0")
            lon = data.get("lon", "0.0")
            
            maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    except Exception as e:
        # Fallback tracking parameters if offline or firewalled
        city, region, lat, lon = "Local Node", "Network Timeout", "Unknown", "Unknown"
        maps_link = "Unable to generate live telemetry link."

    # --- MOCK OUTBOUND EMERGENCY API PAYLOAD ---
    print("=" * 60)
    print("🚨 EMERGENCY TELECOMMUNICATIONS OUTBOUND API BROADCAST 🚨")
    print("=" * 60)
    print(f"STATUS   : Priority 1 Dispatch Target")
    print(f"MESSAGE  : Automated Distress Signal Verified via Edge CV.")
    print(f"LOCATION : {city}, {region} (Approx Coordinates: {lat}, {lon})")
    print(f"MAPS LINK: {maps_link}")
    print("=" * 60)
    print("[SYSTEM LOCK] Broadcast complete. Handing control to local hardware.\n")

# --- INITIALIZE SERIAL PORT ---
try:
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(2)
    print("Serial port initialized successfully!")
except Exception as e:
    print(f"Serial port connection failed: {e}")
    ser = None

# --- INITIALIZE MEDIAPIPE ---
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Starting touchless safety interface... Press 'q' to quit, 'r' to reset.")

# --- STATE MACHINE VARIABLES ---
current_state = "UNKNOWN"
signal_counter = 0
last_signal_time = 0
waiting_for_release = False
EMERGENCY_TRIGGERED = False

TIME_WINDOW = 6.0       
REQUIRED_SIGNALS = 3    

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame = cv2.flip(frame, 1)

    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    gesture = "Monitoring..." 

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Distance-based thumb check
            thumb_tip = hand_landmarks.landmark[4]
            index_knuckle = hand_landmarks.landmark[5]
            middle_knuckle = hand_landmarks.landmark[9]
            wrist = hand_landmarks.landmark[0]
            
            palm_scale = math.sqrt((middle_knuckle.x - wrist.x)**2 + (middle_knuckle.y - wrist.y)**2)
            target_x = (index_knuckle.x + middle_knuckle.x) / 2
            target_y = (index_knuckle.y + middle_knuckle.y) / 2
            thumb_palm_dist = math.sqrt((thumb_tip.x - target_x)**2 + (thumb_tip.y - target_y)**2)
            
            is_thumb_tucked = (thumb_palm_dist / palm_scale) < 0.35

            # Fingers folded check
            tip_ids = [8, 12, 16, 20]
            fingers_folded = []
            for tip_id in tip_ids:
                knuckle_id = tip_id - 2
                if hand_landmarks.landmark[tip_id].y > hand_landmarks.landmark[knuckle_id].y:
                    fingers_folded.append(True)
                else:
                    fingers_folded.append(False)

            if is_thumb_tucked and all(fingers_folded):
                gesture = "DISTRESS POSE DETECTED"
            elif not any(fingers_folded) and not is_thumb_tucked:
                gesture = "Normal - Open Palm"
            else:
                gesture = "Monitoring..."

    # --- TEMPORAL COUNTER LOGIC ---
    current_time = time.time()

    if signal_counter > 0 and (current_time - last_signal_time) > TIME_WINDOW and not EMERGENCY_TRIGGERED:
        print("--> Time window expired. Resetting counter.")
        signal_counter = 0

    if gesture == "DISTRESS POSE DETECTED":
        if not waiting_for_release and not EMERGENCY_TRIGGERED:
            signal_counter += 1
            last_signal_time = current_time
            waiting_for_release = True  
            print(f"--> Distress Signal Registered! Count: {signal_counter}/{REQUIRED_SIGNALS}")
            
            if signal_counter >= REQUIRED_SIGNALS:
                EMERGENCY_TRIGGERED = True
                # Run the outbound networking alert block exactly once
                fetch_location_and_send_alert()

    elif gesture == "Normal - Open Palm":
        waiting_for_release = False  

    if EMERGENCY_TRIGGERED:
        gesture = "CRITICAL ALERT SENT!"

    # --- TRANSMIT ONLY ON STATE CHANGE ---
    if ser and gesture != current_state:
        if EMERGENCY_TRIGGERED:
            ser.write(b'S')  
            current_state = "CRITICAL ALERT SENT!"
        elif gesture == "Normal - Open Palm":
            ser.write(b'A')  
            current_state = "Normal - Open Palm"

    # UI Design
    if EMERGENCY_TRIGGERED:
        color = (0, 0, 255)  
        display_text = f"{gesture}"
    elif signal_counter > 0:
        color = (0, 165, 255)  
        display_text = f"FLAGGED (Count: {signal_counter})"
    else:
        color = (0, 255, 0)  
        display_text = "System Secure"

    cv2.putText(frame, display_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
    cv2.imshow("Automated Distress Alert Pipeline", frame)

    # Keyboard interactions
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        print("\n[SYSTEM MANUALLY RESET]")
        EMERGENCY_TRIGGERED = False
        signal_counter = 0
        current_state = "UNKNOWN"

cap.release()
if ser:
    ser.close()
cv2.destroyAllWindows()

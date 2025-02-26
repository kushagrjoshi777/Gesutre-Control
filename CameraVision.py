import cv2
import mediapipe as mp
import os
import subprocess
import time
import math
import webbrowser

# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# Gesture hold timers
gesture_timers = {}

def distance(landmark1, landmark2):
    return math.sqrt((landmark1.x - landmark2.x) ** 2 + (landmark1.y - landmark2.y) ** 2)

def is_i_love_you(landmarks):
    return (
        distance(landmarks[4], landmarks[0]) > distance(landmarks[3], landmarks[0]) and  # Thumb
        distance(landmarks[8], landmarks[0]) > distance(landmarks[6], landmarks[0]) and  # Index
        distance(landmarks[20], landmarks[0]) > distance(landmarks[18], landmarks[0]) and  # Pinky
        distance(landmarks[12], landmarks[0]) < distance(landmarks[9], landmarks[0]) and  # Middle
        distance(landmarks[16], landmarks[0]) < distance(landmarks[13], landmarks[0])    # Ring
    )

def is_victory(landmarks):
    return (
        distance(landmarks[8], landmarks[0]) > distance(landmarks[6], landmarks[0]) and  # Index
        distance(landmarks[12], landmarks[0]) > distance(landmarks[10], landmarks[0]) and  # Middle
        distance(landmarks[16], landmarks[0]) < distance(landmarks[14], landmarks[0]) and  # Ring
        distance(landmarks[20], landmarks[0]) < distance(landmarks[18], landmarks[0])    # Pinky
    )

def is_fist(landmarks):
    return all(
        distance(landmarks[i], landmarks[0]) < distance(landmarks[i - 2], landmarks[0])
        for i in [4, 8, 12, 16, 20]
    )

def is_open_palm(landmarks):
    return all(
        distance(landmarks[i], landmarks[0]) > distance(landmarks[i - 2], landmarks[0])
        for i in [4, 8, 12, 16, 20]
    )

def handle_gesture(gesture_func, hold_time, landmarks, action):
    global gesture_timers
    gesture_name = gesture_func.__name__

    if gesture_func(landmarks):
        if gesture_name not in gesture_timers:
            gesture_timers[gesture_name] = time.time()
        elif time.time() - gesture_timers[gesture_name] >= hold_time:
            action()
            gesture_timers[gesture_name] = None  # Reset timer
    else:
        gesture_timers[gesture_name] = None  # Reset if gesture is not held

def open_chrome():
    print("Opening Google Chrome...")
    try:
        subprocess.Popen(["C:/Program Files/Google/Chrome/Application/chrome.exe"])
    except FileNotFoundError:
        webbrowser.open("https://www.google.com")

def open_library():
    print("Opening File Explorer...")
    os.startfile("explorer")

def toggle_brightness_mode():
    print("Toggling brightness mode (implement functionality here)")

def close_program():
    print("Closing program...")
    cap.release()
    cv2.destroyAllWindows()
    exit(0)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            handle_gesture(is_i_love_you, 3, hand_landmarks.landmark, open_chrome)
            handle_gesture(is_victory, 2, hand_landmarks.landmark, open_library)
            handle_gesture(is_fist, 3, hand_landmarks.landmark, toggle_brightness_mode)
            handle_gesture(is_open_palm, 5, hand_landmarks.landmark, close_program)

    cv2.imshow('Hand Gesture Control', frame)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

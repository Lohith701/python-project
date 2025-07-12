#no venv in this project

import cv2
import time
import pygame
import subprocess
import numpy as np
import os
from gtts import gTTS
from pydub import AudioSegment

# Initialize pygame mixer for playing sound
pygame.mixer.init()

# Load the cascade for face detection
face_cascade = cv2.CascadeClassifier("C:/Users/LOHITH/Downloads/haarcascade_frontalface_default.xml")

# Load the COCO class labels our YOLO model was trained on
LABELS = open("C:/Users/LOHITH/Downloads/Object Detector/Object Detector/coco.names").read().strip().split("\n")
with open("C:/Users/LOHITH/Downloads/Object Detector/Object Detector/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

# Load our YOLO object detector trained on the COCO dataset (80 classes)
print("[INFO] loading YOLO from disk...")
net = cv2.dnn.readNetFromDarknet("C:/Users/LOHITH/Downloads/Object Detector/Object Detector/yolov3.cfg", "C:/Users/LOHITH/Downloads/Object Detector/Object Detector/yolov3.weights")
font = cv2.FONT_HERSHEY_PLAIN

# Determine only the output layer names that we need from YOLO
ln = net.getLayerNames()
unconnected_out_layers = net.getUnconnectedOutLayers()

if isinstance(unconnected_out_layers, np.ndarray) and unconnected_out_layers.ndim == 1:
    ln = [ln[i - 1] for i in unconnected_out_layers]
else:
    ln = [ln[i[0] - 1] for i in unconnected_out_layers]

# Initialize video capture
cap = cv2.VideoCapture(0)

# Initialize variables for tracking time
last_detected_time = time.time()
alert_threshold = 5  # Threshold for alert in seconds

# Function to play buzzer sound
def play_buzzer_sound():
    pygame.mixer.music.load("C:/Users/LOHITH/Desktop/Biometrics/alarm.wav")
    pygame.mixer.music.play()

while True:
    # Read the frame
    ret, frame = cap.read()

    # Convert frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Perform object detection within detected faces
    for (x, y, w, h) in faces:
        face_roi = frame[y:y+h, x:x+w]

        # Prepare blob for YOLO
        blob = cv2.dnn.blobFromImage(face_roi, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        layer_outputs = net.forward(ln)

        # Initialize lists for detected objects
        boxes = []
        confidences = []
        class_ids = []

        # Loop over each of the layer outputs
        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                # Filter out weak predictions by ensuring the detected probability is greater than the minimum probability
                if confidence > 0.5:
                    # Scale the bounding box coordinates back relative to the size of the image
                    center_x = int(detection[0] * w)
                    center_y = int(detection[1] * h)
                    width = int(detection[2] * w)
                    height = int(detection[3] * h)

                    # Get the top-left corner of the bounding box
                    x = int(center_x - (width / 2))
                    y = int(center_y - (height / 2))

                    boxes.append([x, y, width, height])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply non-maxima suppression to suppress weak, overlapping bounding boxes
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)

        # Draw bounding boxes and labels on the frame
        for i in range(len(boxes)):
            if i in indexes:
                x, y, width, height = boxes[i]
                label = str(classes[class_ids[i]])
                confidence = confidences[i]
                color = colors[class_ids[i]]
                cv2.rectangle(face_roi, (x, y), (x + width, y + height), color, 2)
                cv2.putText(face_roi, f"{label}: {confidence:.2f}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Display the frame
    cv2.imshow('Frame', frame)

    # Check if face is detected
    if len(faces) > 0:
        # Update last detected time
        last_detected_time = time.time()
        print("User is looking at the screen:", time.strftime("%H:%M:%S", time.localtime()))

        # Print detected objects
        if len(indexes) > 0:
            detected_objects = [str(classes[class_ids[i]]) for i in indexes.flatten()]
            print("Detected objects:", detected_objects)

    # Check if face is not detected for more than threshold seconds
    if time.time() - last_detected_time > alert_threshold:
        print("User is away from the screen:", time.strftime("%H:%M:%S", time.localtime()))
        alert_text = "Alert: User is away from the screen! Please pay attention."
        cv2.putText(frame, alert_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        play_buzzer_sound()

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close windows
cap.release()
cv2.destroyAllWindows()

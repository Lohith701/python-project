import subprocess
import numpy as np
import time
import cv2
import os
import sys

from gtts import gTTS
from pydub import AudioSegment

AudioSegment.converter = r"C:/Users/LOHITH/Downloads/Object Detector/Object Detector/ffprobe.exe"
AudioSegment.ffprobe   = r"C:/Users/LOHITH/Downloads/Object Detector/Object Detector/ffprobe.exe"


# load the COCO class labels our YOLO model was trained on
LABELS = open("C:/Users/LOHITH/Downloads/Object Detector/Object Detector/coco.names").read().strip().split("\n")
with open("C:/Users/LOHITH/Downloads/Object Detector/Object Detector/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

# load our YOLO object detector trained on COCO dataset (80 classes)
print("[INFO] loading YOLO from disk...")
net = cv2.dnn.readNetFromDarknet("C:/Users/LOHITH/Downloads/Object Detector/Object Detector/yolov3.cfg", "C:/Users/LOHITH/Downloads/Object Detector/Object Detector/yolov3.weights")
font = cv2.FONT_HERSHEY_PLAIN


# determine only the *output* layer names that we need from YOLO
ln = net.getLayerNames()

unconnected_out_layers = net.getUnconnectedOutLayers()

# Check if unconnected_out_layers is a 1-D array
if isinstance(unconnected_out_layers, np.ndarray) and unconnected_out_layers.ndim == 1:
    # If it's a 1-D array, directly iterate over its elements
    ln = [ln[i - 1] for i in unconnected_out_layers]
else:
    # If it's not a 1-D array, handle it as you were doing before
    ln = [ln[i[0] - 1] for i in unconnected_out_layers]


# # Get the unconnected output layers
# unconnected_out_layers = net.getUnconnectedOutLayers()

# # Check if the output is a 2-D array or a 1-D array
# if unconnected_out_layers.shape[1] == 1:
#     # If it's a 1-D array, adjust the indexing
#     ln = [ln[i[0] - 1] for i in unconnected_out_layers]
# else:
#     # If it's a 2-D array, use the original indexing
#     ln = [ln[i[0] - 1] for i in unconnected_out_layers]

# initialize
cap = cv2.VideoCapture(0)

# # determine only the *output* layer names that we need from YOLO
# ln = net.getLayerNames()
# ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# # initialize
# cap = cv2.VideoCapture(0)

frame_count = 0
start = time.time()
first = True
frames = []
flag=1

while True:
	frame_count += 1
    # Capture frame-by-frame
	ret, frame = cap.read()
	cv2.imshow("aj", frame)
	frames.append(frame)


	if cv2.waitKey(25) & 0xFF == ord('q'):
		break
	if ret:
		key = cv2.waitKey(1)
		if frame_count % 60 == 0:
			end = time.time()
			# grab the frame dimensions and convert it to a blob
			(H, W) = frame.shape[:2]
			# construct a blob from the input image and then perform a forward
			# pass of the YOLO object detector, giving us our bounding boxes and
			# associated probabilities
			blob = cv2.dnn.blobFromImage(frame, 1/ 255.0, (416, 416),
				swapRB=True, crop=False)
			net.setInput(blob)
			layerOutputs = net.forward(ln)

			# initialize our lists of detected bounding boxes, confidences, and
			# class IDs, respectively
			boxes = []
			confidences = []
			classIDs = []
			centers = []

			# loop over each of the layer outputs
			for output in layerOutputs:
				# loop over each of the detections
				for detection in output:
					# extract the class ID and confidence (i.e., probability) of
					# the current object detection
					scores = detection[5:]
					classID = np.argmax(scores)
					confidence = scores[classID]

					# filter out weak predictions by ensuring the detected
					# probability is greater than the minimum probability
					if confidence > 0.5:
						# scale the bounding box coordinates back relative to the
						# size of the image, keeping in mind that YOLO actually
						# returns the center (x, y)-coordinates of the bounding
						# box followed by the boxes' width and height
						box = detection[0:4] * np.array([W, H, W, H])
						(centerX, centerY, width, height) = box.astype("int")

						# use the center (x, y)-coordinates to derive the top and
						# and left corner of the bounding box
						x = int(centerX - (width / 2))
						y = int(centerY - (height / 2))

						# update our list of bounding box coordinates, confidences,
						# and class IDs
						boxes.append([x, y, int(width), int(height)])
						confidences.append(float(confidence))
						classIDs.append(classID)
						centers.append((centerX, centerY))

			# apply non-maxima suppression to suppress weak, overlapping bounding
			# boxes
			idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)

			for i in range(len(boxes)):
				if i in idxs:
					x, y, w, h = boxes[i]
					label = str(classes[classIDs[i]])
					confidence = confidences[i]
					color = colors[classIDs[i]]
					cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
					cv2.putText(frame, label + " " + str(round(confidence, 2)), (x, y + 30), font, 3, color, 3)


			texts = ["The environment has following objects"]

			# ensure at least one detection exists
			if len(idxs) > 0:
				# loop over the indexes we are keeping
				for i in idxs.flatten():
					# find positions
					centerX, centerY = centers[i][0], centers[i][1]

					if centerX <= W/3:
						W_pos = "left "
					elif centerX <= (W/3 * 2):
						W_pos = "center "
					else:
						W_pos = "right "

					if centerY <= H/3:
						H_pos = "top "
					elif centerY <= (H/3 * 2):
						H_pos = "mid "
					else:
						H_pos = "bottom "

					texts.append(H_pos + W_pos + LABELS[classIDs[i]])
					flag=0

			print(texts)

			if (flag==0):
				description = ', '.join(texts)
				tts = gTTS(description, lang='en')
				tts.save(r"C:/Users/LOHITH/Downloads/Object Detector/Object Detector/tts.mp3")

from pydub import AudioSegment

                # Specify the path to ffmpeg
AudioSegment.converter = r"C:/Users/LOHITH\Downloads/Object Detector/Object Detector/ffmpeg.exe"
AudioSegment.ffprobe   = r"C:/Users/LOHITH\Downloads/Object Detector/Object Detector/ffprobe.exe"


tts = AudioSegment.from_mp3(r"C:/Users/LOHITH/Downloads/Object Detector/Object Detector/tts.mp3")
subprocess.call(["ffplay", "-nodisp", "-autoexit", "tts.mp3"])


cap.release()
cv2.destroyAllWindows()
os.remove("tts.mp3")

import numpy as np
import imutils
import time
from scipy import spatial
import cv2
from input_retrieval import *
global Masuk,Keluar
list_of_vehicles = ["bicycle","car","motorbike","bus","truck", "train"]
FRAMES_BEFORE_CURRENT = 10  
inputWidth, inputHeight = 416, 416
Masuk=0
Keluar=0
LABELS, weightsPath, configPath, inputVideoPath, outputVideoPath,\
	preDefinedConfidence, preDefinedThreshold, USE_GPU= parseCommandLineArguments()

np.random.seed(42)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
	dtype="uint8")
def displayVehicleCount(frame, vehicle_count):
	global Masuk, Keluar
	cv2.putText(
		frame,
		'Terdeteksi Kendaraan: ' + str(vehicle_count),
		(20, 20),
		cv2.FONT_HERSHEY_SIMPLEX,
		0.8, #Size
		(0, 0xFF, 0), #Color
		2, #Thickness
		cv2.FONT_HERSHEY_COMPLEX_SMALL,
		)
	cv2.putText(
		frame,
		'MASUK: ' ,
		(60, 460),
		cv2.FONT_HERSHEY_SIMPLEX,
		1.3,  # Size
		(0, 255, 0),  # Color
		4,  # Thickness
		cv2.FONT_HERSHEY_COMPLEX_SMALL,
	)
	cv2.putText(
		frame,
		str(Masuk),
		(250, 460),
		cv2.FONT_HERSHEY_SIMPLEX,
		1.3,  # Size
		(0, 255, 0),  # Color
		4,  # Thickness
		cv2.FONT_HERSHEY_COMPLEX_SMALL,
	)
	cv2.putText(
		frame,
		'KELUAR: ',
		(680, 460),
		cv2.FONT_HERSHEY_SIMPLEX,
		1.3,  # Size
		(0, 0, 255),  # Color
		4,  # Thickness
		cv2.FONT_HERSHEY_COMPLEX_SMALL,
	)
	cv2.putText(
		frame,
		str(Keluar),
		(880, 460),
		cv2.FONT_HERSHEY_SIMPLEX,
		1.3,  # Size
		(0, 0, 255),  # Color
		4,  # Thickness
		cv2.FONT_HERSHEY_COMPLEX_SMALL,
	)


def boxAndLineOverlap(x_mid_point, y_mid_point, line_coordinates):
	x1_line, y1_line, x2_line, y2_line = line_coordinates #Unpacking

	if (x_mid_point >= x1_line and x_mid_point <= x2_line+5) and\
		(y_mid_point >= y1_line and y_mid_point <= y2_line+5):
		return True
	return False
def displayFPS(start_time, num_frames):
	current_time = int(time.time())
	if(current_time > start_time):
		os.system('clear')
		print("FPS:", num_frames)
		num_frames = 0
		start_time = current_time
	return start_time, num_frames

def drawDetectionBoxes(idxs, boxes, classIDs, confidences, frame):
	global Masuk,Keluar,label
	if len(idxs) > 0:
		nilai_y_prev=0
		for i in idxs.flatten():
			(x, y) = (boxes[i][0], boxes[i][1])
			(w, h) = (boxes[i][2], boxes[i][3])

			color = [int(c) for c in COLORS[classIDs[i]]]
			cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
			print(LABELS[classIDs[i]])
			if(str(LABELS[classIDs[i]])=="car"):
				label="Mobil"
			elif(str(LABELS[classIDs[i]])=="truck"):
				label="Truk"
			elif (str(LABELS[classIDs[i]]) == "motorbike"):
				label = "Motor"
			elif (str(LABELS[classIDs[i]]) == "bus"):
				label = "Bis"
			elif (str(LABELS[classIDs[i]]) == "train"):
				label = "Kereta"
			elif (str(LABELS[classIDs[i]]) == "bicycle"):
				label = "Sepeda"
			text = "{}: {:.4f}".format(str(label),
				confidences[i])
			nilai_x = x + (w//2)
			nilai_y=y+ (h//2)
			#cv2.putText(frame, text, (x, y - 5),
			#	cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

			cv2.line(frame, (x1_line, 420), (x2_line, 420), (255, 0, 0), 5)
			cv2.line(frame, (630, 420), (630, 800), (255, 0, 0), 5)
			cv2.circle(frame, (x + (w//2), y+ (h//2)), 2, (0, 0xFF, 0), thickness=2)
			cv2.putText(frame, text, (x, y - 5),
						cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
			if(nilai_x<630 and nilai_y>420):
				if(nilai_y>420 and nilai_y<425):
					Masuk=Masuk+1
			elif(nilai_x>630 and nilai_y<420):
				if (nilai_y < 420 and nilai_y > 415):
					Keluar = Keluar + 1
		print("Masuk= "+str(Masuk))
		print("Keluar= " + str(Keluar))




def initializeVideoWriter(video_width, video_height, videoStream):
	sourceVideofps = videoStream.get(cv2.CAP_PROP_FPS)
	fourcc = cv2.VideoWriter_fourcc(*"MJPG")
	return cv2.VideoWriter(outputVideoPath, fourcc, sourceVideofps,
		(video_width, video_height), True)

def boxInPreviousFrames(previous_frame_detections, current_box, current_detections):
	centerX, centerY, width, height = current_box
	dist = np.inf
	for i in range(FRAMES_BEFORE_CURRENT):
		coordinate_list = list(previous_frame_detections[i].keys())
		if len(coordinate_list) == 0:
			continue
		temp_dist, index = spatial.KDTree(coordinate_list).query([(centerX, centerY)])
		if (temp_dist < dist):
			dist = temp_dist
			frame_num = i
			coord = coordinate_list[index[0]]

	if (dist > (max(width, height)/2)):
		return False

	current_detections[(centerX, centerY)] = previous_frame_detections[frame_num][coord]
	return True

def count_vehicles(idxs, boxes, classIDs, vehicle_count, previous_frame_detections, frame):
	current_detections = {}
	if len(idxs) > 0:
		for i in idxs.flatten():
			(x, y) = (boxes[i][0], boxes[i][1])
			(w, h) = (boxes[i][2], boxes[i][3])
			
			centerX = x + (w//2)
			centerY = y+ (h//2)
			if (LABELS[classIDs[i]] in list_of_vehicles):
				current_detections[(centerX, centerY)] = vehicle_count 
				if (not boxInPreviousFrames(previous_frame_detections, (centerX, centerY, w, h), current_detections)):
					vehicle_count += 1
				ID = current_detections.get((centerX, centerY))
				if (list(current_detections.values()).count(ID) > 1):
					current_detections[(centerX, centerY)] = vehicle_count
					vehicle_count += 1
				cv2.putText(frame, str(ID), (centerX, centerY),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0,0,255], 2)

	return vehicle_count, current_detections

net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

if USE_GPU:
	net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
	net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
videoStream = cv2.VideoCapture(inputVideoPath)
video_width = int(videoStream.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(videoStream.get(cv2.CAP_PROP_FRAME_HEIGHT))
x1_line = 0
y1_line = video_height//2
x2_line = video_width
y2_line = video_height//2

previous_frame_detections = [{(0,0):0} for i in range(FRAMES_BEFORE_CURRENT)]
num_frames, vehicle_count = 0, 0
writer = initializeVideoWriter(video_width, video_height, videoStream)
start_time = int(time.time())
while True:
	print("================FRAME BARU================")
	num_frames+= 1
	print("FRAME:\t", num_frames)
	boxes, confidences, classIDs = [], [], [] 
	vehicle_crossed_line_flag = False
	start_time, num_frames = displayFPS(start_time, num_frames)
	(grabbed, frame) = videoStream.read()
	if not grabbed:
		break
	blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (inputWidth, inputHeight),
		swapRB=True, crop=False)
	net.setInput(blob)
	start = time.time()
	layerOutputs = net.forward(ln)
	end = time.time()

	for output in layerOutputs:
		for i, detection in enumerate(output):
			scores = detection[5:]
			classID = np.argmax(scores)
			confidence = scores[classID]
			if confidence > preDefinedConfidence:
				box = detection[0:4] * np.array([video_width, video_height, video_width, video_height])
				(centerX, centerY, width, height) = box.astype("int")
				x = int(centerX - (width / 2))
				y = int(centerY - (height / 2))

				boxes.append([x, y, int(width), int(height)])
				confidences.append(float(confidence))
				classIDs.append(classID)

	idxs = cv2.dnn.NMSBoxes(boxes, confidences, preDefinedConfidence,
		preDefinedThreshold)

	drawDetectionBoxes(idxs, boxes, classIDs, confidences, frame)

	vehicle_count, current_detections = count_vehicles(idxs, boxes, classIDs, vehicle_count, previous_frame_detections, frame)

	displayVehicleCount(frame, vehicle_count)

	writer.write(frame)

	cv2.imshow('Frame', frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	previous_frame_detections.pop(0)
	previous_frame_detections.append(current_detections)

writer.release()
videoStream.release()

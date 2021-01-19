
# real-time object detection program from a live camera feed
# Dec.16, 2020  tst run successfully
# copied code from <Hello AI World NVDIA JETSON>

import jetson.inference
import jetson.utils
from datetime import datetime, date
import time
import smtplib, ssl

def email_alert(t, duration):

	port = 465
	context = ssl.create_default_context()
	sender_email = "emma.lijing0723@gmail.com"
	receiver_email = "regent.rosinski@gmail.com"

	if type(t) == str:
		message = """\
		Subject: Cat-LitterBox Alert


		Hey you! It's {} now.
		Your cat is in the litterbox!""".format(t)
	else:
		cat_left = time.strftime("%H:%M:%S",time.localtime(t))   # convert epoch time(float) to localtime(str)
		message = """\
		Subject: Cat-LitterBox Alert


		Hey again!
		Your cat left the litterbox at {}.
		He used the toilet for {}.""".format(cat_left, duration)

	with smtplib.SMTP_SSL("smtp.gmail.com", port, context = context) as server: # create a secure connection with Gmail's SMTP server
		server.login("emma.lijing0723@gmail.com", "Phantom31")
		server.sendmail(sender_email, receiver_email, message)


def cat_toilet_record():
	count = 0
 # Emma: record first time when cat shows up and set it as the title of the file
	while display.IsStreaming():
		target = ""
		img = camera.Capture()         # caption the nex video frame from the camera; 
                	                       # camera.Capture() will wait until the next frame has been sent from the camera and loaded into GPU memory
	                	               # The returned image will be a jetson.utils.cudaImage object that contains atributes like width, height, and pixel format
		detections = net.Detect(img)   # process the image with net.Detect() function. It returns a list of detections(detecting Objects) 
		display.Render(img)            # visualize the results with OpenGL
		display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))  #  and update the title of the window to display the current performance 

        # Emma modifying here(Dec.17)
		for detection in detections:
			if net.GetClassDesc(detection.ClassID) == "cat":
				print("Yay! It's a cat!")
				target = "cat"
				showup_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
				showup_time_reg = datetime.now().strftime("%H:%M:%S")
				showup_time_epoch = time.time()
		if target == "cat":
			with open(showup_time, "a") as f:
				f.write(showup_time_reg+"\n")
			email_alert(showup_time_reg, 0)
			break

# Emma: Record cat toilet time. If cat is absent for 5 seconds, then call the function itself to open a new log file for when cat shows up again(Dec.22,2020) 
	while display.IsStreaming():
		target = ""
		img = camera.Capture()
		detections = net.Detect(img)
		display.Render(img)
		display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))

		for detection in detections:
			if net.GetClassDesc(detection.ClassID) == "cat":
				target = "cat"
				toilet_time = datetime.now().strftime("%H:%M:%S")
		if target == "cat":
			with open(showup_time, "a") as f:
				f.write(toilet_time+"\n")
			if count != 0:		# set count to 0 if cat shows up again within 10 secs. 
				count = 0
		elif count < 10:
			count += 1
			print("Emma, count is:", count)
		else:
			cat_left_time = time.time()-10   # minus 10 secs because cat left 10 secs ago
			toilet_duration = time.strftime("%H:%M:%S", time.gmtime(cat_left_time - showup_time_epoch))
			email_alert(cat_left_time,toilet_duration)
			cat_toilet_record()
		time.sleep(1)

# create a detectnet object instance that loads the 91-class SSD-Mobilenet-v2 model
net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)   # model string and threshold value can be different

# create an instance of the videoSource object(openning camera stream)
camera = jetson.utils.videoSource("csi://0")

# create a video output interface with the videoOutput object and create a main loop that will run until the user exits(Display loop)
display = jetson.utils.videoOutput("display://0")  # "my_video.mp4" for file

cat_toilet_record()  # call the above function


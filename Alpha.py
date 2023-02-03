# Importing Libraries:
import cv2
import numpy
import math
import pyautogui        # pyautogui is used to press buttons of Media Player automatically.

# Accessing the Webcam:
# 0 to accessing the Primary Webcam
webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

#----------------------------------------------------------------------------------
# Trackbar:
def nothing_function(x):
        pass

# Defining the Window:
cv2.namedWindow("Color Adjustments", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Color Adjustments", (300, 300))
cv2.createTrackbar("Threshold", "Color Adjustments", 0 , 255, nothing_function)

# Color Detection Tracking:
cv2.createTrackbar("Lower H", "Color Adjustments", 0, 255, nothing_function)
cv2.createTrackbar("Lower S", "Color Adjustments", 0, 255, nothing_function)
cv2.createTrackbar("Lower V", "Color Adjustments", 0, 255, nothing_function)
cv2.createTrackbar("Upper H", "Color Adjustments", 255, 255, nothing_function)
cv2.createTrackbar("Upper S", "Color Adjustments", 255, 255, nothing_function)
cv2.createTrackbar("Upper V", "Color Adjustments", 255, 255, nothing_function)


#----------------------------------------------------------------------------------
#  Converting captured frames to hsv:
while True:
        _, frame = webcam.read()
        # Flipping the Camera to avoid Mirroring Effect:
        frame = cv2.flip(frame, 2)
        frame = cv2.resize(frame, (600, 500))

        # Getting hand Data from Rectangular Sub_Window:
        cv2.rectangle(frame, (0, 1), (300, 500), (255, 0, 0), 0)
        crop_image = frame[1:500, 0:300]

        # hsv:
        hsv = cv2.cvtColor(crop_image, cv2.COLOR_BGR2HSV)

        # Detecting Hand:
        # Getting the values of the Trackbars:
        lower_h = cv2.getTrackbarPos("Lower H", "Color Adjustments")
        lower_s = cv2.getTrackbarPos("Lower S", "Color Adjustments")
        lower_v = cv2.getTrackbarPos("Lower V", "Color Adjustments")

        upper_h = cv2.getTrackbarPos("Upper H", "Color Adjustments")
        upper_s = cv2.getTrackbarPos("Upper S", "Color Adjustments")
        upper_v = cv2.getTrackbarPos("Upper V", "Color Adjustments")

        # Passing values of Trackbars, which are RGB values.
        # To detect a hand, we  are passing RGB values of Skin Color here.
        # With the Trackbars, we can change the value of skin color to detect
        # With the trackbars, we can modify our code to work with different complexions of skin color
        lower_bound = numpy.array([lower_h, lower_s, lower_v])
        upper_bound = numpy.array([upper_h, upper_s, upper_v])

        # Creating a Mask:
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        # Filter the mask with an Image:
        mask_filter = cv2.bitwise_and(crop_image, crop_image, mask=mask)

        #----------------------------------------------------------------------------------
        # Inverting Pixel Value (Black to White and Vice Versa)
        # Enhancing the Contours:
        mask1 = cv2.bitwise_not(mask)   # Background becomes Black, object to be detected becomes white
        m_g = cv2.getTrackbarPos("Threshold", "Color Adjustments")      # Getting Track-Bar Values
        ret, threshold = cv2.threshold(mask1, m_g, 255, cv2.THRESH_BINARY)
        noise_dilate = cv2.dilate(threshold, (3, 3), iterations=6)

        #----------------------------------------------------------------------------------
        # Finding the Contours:
        countors, hier = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Exception Handling to avoid errors if Contour Area isn't found:
        try:
                # Finding Contour with Maximum Area:
                contour_maximum = max(countors, key=lambda x: cv2.contourArea(x))
                # Fixing the Contour:
                epsilon = 0.0005 * cv2.arcLength(contour_maximum, True)
                # Enhancing the Contour by :
                data = cv2.approxPolyDP(contour_maximum, epsilon, True)
                # Drawing the Hull over the Contour:
                hull = cv2.convexHull(contour_maximum)

                cv2.drawContours(crop_image, [contour_maximum], -1, (50, 50, 150), 2)
                cv2.drawContours(crop_image, [hull], -1, (0, 255, 0), 2)

                #----------------------------------------------------------------------------------
                # Finding Convexity Defects:
                hull = cv2.convexHull(contour_maximum, returnPoints=False)
                defects = cv2.convexityDefects(contour_maximum, hull)
                defects_count = 0

                for i in range(defects.shape[0]):
                        s, e, f, d = defects[i, 0]

                        start = tuple(contour_maximum[s][0])
                        end = tuple(contour_maximum[e][0])
                        far = tuple(contour_maximum[f][0])

                        # Cosine Rule to find Angle between Fingers:
                        a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                        b= math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                        c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                        angle = (math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180) / 3.14

                        # If angle between fingers is less than 50, draw a white circle there:
                        if angle <= 50:
                                defects_count += 1
                                cv2.circle(crop_image, far, 5, [255, 255, 255], -1)
                
                # Mapping Gestures to Functions:
                print("Count = ", defects_count)

                if defects_count == 0:
                        cv2.putText(frame, " ", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                
                elif defects_count == 1:
                        pyautogui.press("space")
                        cv2.putText(frame, "Play/Pause", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                
                elif defects_count == 2:
                        pyautogui.press("up")
                        cv2.putText(frame, "Volume Up", (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                
                elif defects_count == 3:
                        pyautogui.press("down")
                        cv2.putText(frame, "Volume Down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                
                elif defects_count == 4:
                        pyautogui.press("right")
                        cv2.putText(frame, "Forward", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                
                else:
                        pass

        except:
                pass
        
        # Showing the Windows:
        cv2.imshow("Threshold", threshold)
        cv2.imshow("Filter = ", mask_filter)
        cv2.imshow("Result = ", frame)

        # Exit all Windows by Pressing the ESC Key:
        key = cv2.waitKey(25) &0xFF
        if key == 27:
                break

webcam.release()
cv2.destroyAllWindows()
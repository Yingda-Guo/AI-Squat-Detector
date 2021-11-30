""" usage: run.py [-h] [-v video] 

Process a traning vedio in real-time 

The idea of a valid squat is when both legs angles decrease to a threshold than increase

optional arguments:
  -h, --help            show this help message and exit
  -v VIDEODIR, --videoDir IMAGEDIR
                        Path to the folder where video is stored.
"""
from shutil import copyfile
import argparse
import cv2
import PoseModule as pm
import time
import numpy as np

def main():
    # Initiate argument parser
    parser = argparse.ArgumentParser(description="Process a traning vedio in real-time",
                                     formatter_class=argparse.RawTextHelpFormatter)
    # Add helper arguments
    parser.add_argument(
        '-v', '--videoDir',
        help='Video file path',
        type=str,
        default="squat_resource/squat2.mp4"
    )
    args = parser.parse_args()
    
    # OpenCV video load
    cap = cv2.VideoCapture(args.videoDir)
    # # Get web camera default is 0
    # cap = cv2.VideoCapture(0)
    # # Set web camera size, 3 means width and 4 means height
    # cap.set(3, 1260)
    # cap.set(4, 720)
    
    # FPS initial value
    pTime = 0
    downScaleRatio = 0.6
    draw_scale = 8
    
    # Create object
    detector = pm.poseDetector()
    
    # Using leg angles changes to detect a squat
    count = 0
    
    # 1 is down 0 is up
    dir = 1
    
    # initial threshold
    threshold_max = 170
    threshold_min = 120
    
    # Detect max and min angles when streaming
    max_angle = float('-inf')
    min_angle = float('inf')
    
    # threshold ratio
    threshold_ratio_up = 0.2
    threshold_ratio_down = 0.5
    
    angle_buffer = []
    
    
    while True:
        # success return True or False to indicate whether video ends
        success, img = cap.read()
        # Using waitkey to control the intersection time of sequence images
        if (cv2.waitKey(1) & 0xFF == ord('q')) | success == False:
            break
        height, width, channels = img.shape
        img = cv2.resize(img, (int(width * downScaleRatio),
                         int(height * downScaleRatio)))
        h, w, _ = img.shape
        # Set bounding box size
        box_length = int(h / draw_scale) if h / \
            draw_scale > w / draw_scale else int(w / 6)
            
        detector.findPose(img, draw=False)
        lmList = detector.findPosition(img, draw=False)
        # Get index for certain position
        if lmList is not None and len(lmList) > 0:
            # Get left leg angle
            point1 = (lmList[24][1], lmList[24][2])
            point2 = (lmList[26][1], lmList[26][2])
            point3 = (lmList[28][1], lmList[28][2])
            img = detector.drawAngle(img, point1, point2, point3)
            angle_left = detector.calculateAngle(
                point1, point2, point3, acuteAngle=True)
    
            # Get right leg angle
            point1 = (lmList[23][1], lmList[23][2])
            point2 = (lmList[25][1], lmList[25][2])
            point3 = (lmList[27][1], lmList[27][2])
            img = detector.drawAngle(img, point1, point2, point3)
            angle_right = detector.calculateAngle(
                point1, point2, point3, acuteAngle=True)
    
            # find maximal and minimal angles
            # if angle_left > threshold_max:
            #     if angle_left > max_angle:
            #         max_angle = angle_left
            #         threshold_max = max_angle * (1 - threshold_ratio_up)
            #
            # if angle_right > threshold_max:
            #     if angle_right > max_angle:
            #         max_angle = angle_right
            #         threshold_max = max_angle * (1 - threshold_ratio_up)
            #
            # if angle_left < threshold_min:
            #     if angle_left < min_angle:
            #         min_angle = angle_left
            #         threshold_min = min_angle * (1 + threshold_ratio_down)
            #
            # if angle_right < threshold_min:
            #     if angle_right < min_angle:
            #         min_angle = angle_right
            #         threshold_min = min_angle * (1 + threshold_ratio_down)
    
            # For angles decrease (1), we look for the smaller angle of two sides
            # For angles increase (0), we look for the lager of the two
            if dir == 1:
                angle_optimal = angle_left if angle_left > angle_right else angle_right
            else:
                angle_optimal = angle_left if angle_left < angle_right else angle_right
            
             # When both angles increase to the maximal threshold
            if angle_optimal > threshold_max:
                if len(angle_buffer) == 0:
                    if dir == 0:
                        count += 0.5
                        dir = 1
                        # push the two angles to the buffer
                        angle_buffer.append([angle_left, angle_right])
                else:
                    angle_left_previous, angle_right_previous = angle_buffer.pop()
                    # only when both legs' angle decrese or increase at the same time, a valid squat is deteced
                    if (angle_left >= angle_left_previous and angle_right >= angle_right_previous) or (
                            angle_left <= angle_left_previous and angle_right <= angle_right_previous):
                        if dir == 0:
                            count += 0.5
                            dir = 1
                            angle_buffer.append([angle_left, angle_right])
                            
            # When both angles decreases to a minimal threshold
            if angle_optimal < threshold_min:
                if len(angle_buffer) == 0:
                    if dir == 1:
                        count += 0.5
                        dir = 0
                        # push the two angles to the buffer
                        angle_buffer.append([angle_left, angle_right])
                else:
                    angle_left_previous, angle_right_previous = angle_buffer.pop()
                    # only when both legs' angle decrese or increase at the same time, a valid squat is deteced
                    if (angle_left >= angle_left_previous and angle_right >= angle_right_previous) or (
                            angle_left <= angle_left_previous and angle_right <= angle_right_previous):
                        if dir == 1:
                            count += 0.5
                            dir = 0
                            angle_buffer.append([angle_left, angle_right])
    
            # Left side Bounding box and Text
            cv2.rectangle(img, (0, int(h - 3 * box_length / 4)),
                          (box_length, h), (141, 143, 141), 3)
            cv2.putText(img, f'{int(count)}', (int(box_length / (3 * draw_scale)), h - int(box_length / (draw_scale))),
                        cv2.FONT_HERSHEY_PLAIN, int(box_length / 20), (13, 129, 252), int(box_length / 20))
    
            # Draw a bar
            bar = np.interp(angle_optimal, (threshold_min, threshold_max), (int(h - 3 * box_length / 4 - box_length / (draw_scale) - box_length * 3),
                                                                            int(h - 3 * box_length / 4 - box_length / (draw_scale))))
            cv2.rectangle(img, (0, int(h - 3 * box_length / 4 - box_length / (draw_scale))),
                          (int(box_length / 4), int(h - 3 * box_length /
                           4 - box_length / (draw_scale) - box_length * 3)),
                          (141, 143, 141), int(box_length / 50))
            cv2.rectangle(img, (int(1 / draw_scale), int(bar)),
                          (int(box_length / 4), int(h - 3 * box_length /
                           4 - box_length / (draw_scale))), (13, 129, 252),
                          cv2.FILLED)
            # Draw percentage
            per = np.interp(
                angle_optimal, (threshold_min, threshold_max), (100, 0))
            cv2.putText(img, f'{int(per)}%',
                        (int(1 / draw_scale), int(h - 3 * box_length / 4 -
                         2 * box_length / (draw_scale) - box_length * 3)),
                        cv2.FONT_HERSHEY_PLAIN, int(box_length / 60), (13, 129, 252), int(box_length / 60))
    
        # Add frame rate
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
    
        cv2.putText(img, "FPS:" + str(int(fps)), (20, int(box_length/5)),
                    cv2.FONT_HERSHEY_SIMPLEX, int(box_length / 120), (145, 145, 145), int(box_length / 80))
        # it shows Video as a sequence of images
        cv2.imshow("Video", img)
    
    
if __name__ == '__main__':
    main()

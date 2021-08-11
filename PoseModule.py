import cv2
import mediapipe as mp
import time
import math

# Pose Estimation Class
class poseDetector():
    # init method or constructor
    def __init__(self,
                 mode=False,
                 complexity=1,
                 smooth=True,
                 detection_conf=0.5,
                 tracking_conf=0.5):
        # self相当于一个instance内部通用的variable寄存器
        # Load media pipe pose estimation model
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(mode, complexity, smooth, detection_conf, tracking_conf)
        # Load utilities for drawing
        self.mpDraw = mp.solutions.drawing_utils

    # Run pose detection algorithm
    def findPose(self, img, draw = True):
        # 需要将BGR格式的image转化为RGB格式
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # run pose estimation for the image
        self.result = self.pose.process(imgRGB)
        # 如果没有监测到，则继续下一帧
        if self.result.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.result.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
    # 获得所有坐标以及清晰度
    def findPosition(self, img, draw = True):
        # landmark lists
        self.lmList = []
        # 如果没有监测到，则继续下一帧
        if self.result.pose_landmarks:
            h, w, c = img.shape
            # 返回的x,y,z coordinate都是normalized，如果需要获取到具体坐标需要结合现有image dimension
            for id, lm in enumerate(self.result.pose_landmarks.landmark):
                # Need to convert ratio to real pixel value
                cx, cy = int(lm.x * w), int(lm.y * h)
                z = round(lm.z,5)
                visibility = round(lm.visibility,5)
                # append to list
                self.lmList.append([id, cx, cy, z, visibility])
                # Draw circles to make sure points are correct
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
            return self.lmList

    # 使用index获取angle
    def findAngle(self, img, index_p1, index_p2, index_p3, draw = True, acuteAngle=False):
        x1, y1 = self.lmList[index_p1][1:3]
        x2, y2 = self.lmList[index_p2][1:3]
        x3, y3 = self.lmList[index_p3][1:3]

        # 根据顶角找到顶角的延伸线
        x2_right, y2_right = x2 + 100, y2

        # Draw
        if draw:
            cv2.line(img, (x1,y1), (x2,y2), (209, 209, 209), 3)
            cv2.line(img, (x2,y2), (x3,y3), (209, 209, 209), 3)
            cv2.circle(img, (x1, y1), 10, (13, 129, 252), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (13, 129, 252), 2)
            cv2.circle(img, (x2, y2), 10, (13, 129, 252), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (13, 129, 252), 2)
            cv2.circle(img, (x3, y3), 10, (13, 129, 252), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (13, 129, 252), 2)

        ang = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        ang = ang + 360 if ang < 0 else ang
        if acuteAngle:
            if ang > 180:
                ang = 360 - ang
        return round(ang, 2)

    def calculateAngle(self, point1, point2, point3, acuteAngle = False):
        x1, y1 = point1[0], point1[1]
        x2, y2 = point2[0], point2[1]
        x3, y3 = point3[0], point3[1]
        ang = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        ang = ang + 360 if ang < 0 else ang
        if acuteAngle:
            if ang > 180:
                ang = 360 - ang
        return round(ang, 2)

    def findDistance(self, point1, point2):
        x1, y1 = point1[0], point1[1]
        x2, y2 = point2[0], point2[1]
        return round(((((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5), 2)

    def drawAngle(self, img, point1, point2, point3,
                  font = cv2.FONT_HERSHEY_SIMPLEX,
                  fontScale = 0.8,
                  fontColor = (209, 209, 209),
                  lineType = 2
                  ):
        #三个points，point 2是顶角
        x1, y1 = point1[0], point1[1]
        x2, y2 = point2[0], point2[1]
        x3, y3 = point3[0], point3[1]
        # 根据顶角找到顶角的延伸线
        x2_right, y2_right = x2 + 100, y2

        # Draw points and lines
        cv2.line(img, (x1, y1), (x2, y2), (209, 209, 209), 3)
        cv2.line(img, (x2, y2), (x3, y3), (209, 209, 209), 3)
        cv2.circle(img, (x1, y1), 10, (13, 129, 252), cv2.FILLED)
        cv2.circle(img, (x1, y1), 15, (13, 129, 252), 2)
        cv2.circle(img, (x2, y2), 10, (13, 129, 252), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (13, 129, 252), 2)
        cv2.circle(img, (x3, y3), 10, (13, 129, 252), cv2.FILLED)
        cv2.circle(img, (x3, y3), 15, (13, 129, 252), 2)

        # 找到三角形的小于180度的角
        small_angle = self.calculateAngle((x1, y1), (x2, y2), (x3, y3), acuteAngle=True)

        # 计算三角形边长，并且找到较长边的边长用来角度弧线的半径
        distance1 = self.findDistance((x1, y1), (x2, y2))
        distance2 = self.findDistance((x2, y2), (x3, y3))
        radius = int(distance1 / 3 if distance1 < distance2 else distance2 / 3)

        # 找到生成三角形的两个角的度数
        first_angle = self.calculateAngle((x3, y3), (x2, y2), (x1, y1))
        second_angle = self.calculateAngle((x1, y1), (x2, y2), (x3, y3))
        # 由于eclipse是逆时针画的所以需要找到画圈的起始点，由于总是需要找到锐角，所以起始点有可能是point1或者是point3
        if first_angle < second_angle:
            shift_angle = self.calculateAngle((x2_right, y2_right), (x2, y2), (x3, y3))
        else:
            shift_angle = self.calculateAngle((x2_right, y2_right), (x2, y2), (x1, y1))

        # Draw ellipse
        center_coordinates = (x2, y2)
        axesLength = (radius, radius)
        # 以中心点右侧作为angle 0
        angle = shift_angle
        startAngle = 0
        # 总是找到锐角
        endAngle = first_angle if first_angle < second_angle else second_angle
        # Red color in BGR
        color = (13, 129, 252)
        # Line thickness of 5 px
        thickness = 3

        # Using cv2.ellipse() method
        # Draw a ellipse with red line borders of thickness of 5 px
        cv2.ellipse(img, center_coordinates, axesLength,
                            angle, startAngle, endAngle, color, thickness)

        # 1. Drawing target image sector # 2 of ellipse center longitudinal axis 4. The length of the deflection angle of 3. The arc starting angle end angle 6. 7. 8. Color-padding
        # cv2.ellipse(img,(256,256),(150,100),0,0,145,(255,255,0),-1)

        bottomLeftCornerOfText = (int(x2 - (x1 + x2 - 2 * x2) / 6), int(y2 - (y1 + y2 - 2 * y2) / 6))

        img = cv2.putText(img,
                    str(small_angle),
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)
        return img




def main():
    # OpenCV video load
    cap = cv2.VideoCapture("sample.mp4")
    # FPS initial value
    pTime = 0

    # Create object
    detector = poseDetector()

    while True:
        # success return True or False to indicate whether video ends
        success, img = cap.read()
        # Using waitkey to control the intersection time of consequntive imagesefdsad
        if (cv2.waitKey(1) & 0xFF == ord('q')) | success == False:
            break
        detector.findPose(img, draw=False)
        lmList = detector.findPosition(img, draw=False)
        # Get index for certain position
        if len(lmList) > 0:
            cx, cy = lmList[0][1], lmList[0][2]
            cv2.circle(img, (cx, cy), 8, (0, 0, 255), cv2.FILLED)
        print(lmList)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
        # it shows Video as a sequence of images
        cv2.imshow("Video", img)

if __name__ == '__main__':
    main()
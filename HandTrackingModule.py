import cv2
import numpy as np
import mediapipe as mp
import time                         #to check the frame rate


class HandDetector():
    def __init__(self, mode=False, maxHands=1, modelComplexity=1, detectionConf=0.8, trackConf=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplexity
        self.detectionConf = detectionConf
        self.trackConf = trackConf


        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex, self.detectionConf, self.trackConf)
        self.mpDraw = mp.solutions.drawing_utils


    def findHands(self, img, draw = True):
        imageRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imageRGB)

        if self.results.multi_hand_landmarks:                        #if it detects hand landmarks
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True, eraser=False):

        lmList = []

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h,w,c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                if id == 8 and draw :                           ######## changes made id ==  8 ##########
                    cv2.circle(img, (cx, cy), 10, (255, 255, 255), cv2.FILLED)
                if id ==8 and draw and eraser == True:
                    cv2.circle(img, (cx, cy), 30, (0,0,0), cv2.FILLED)
        
        return lmList

# img1 = np.zeros((320, 480, 3))

def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = HandDetector()

    while True:
        success, img = cap.read()
        image = detector.findHands(img)
        landmarksList = detector.findPosition(img)

        if len(landmarksList) != 0:
            print(landmarksList[8])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_COMPLEX, 3, (193,168,156), 2)

        cv2.imshow('Image', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()
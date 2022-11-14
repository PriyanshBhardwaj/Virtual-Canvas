import cv2
import time

import HandTrackingModule as htm
import numpy as np


class Canvas:

    def __init__(self):
        self.pTime = 0
        self.cTime = 0

        self.cap = cv2.VideoCapture(0)

        self.detector = htm.HandDetector()

        self.painterPoints = []     #x, y of painter
        self.stopperPoints = []    #x, y of stopper(tip of middle finger)

        #coordinates for color strip
        self.xmin, self.xmax, self.ymin = 0, 0, 0
        self.ymax = 100
    

    #drawing function
    def draw(self, points, points1, img, strip_X_coord, colorList):
        # print(2)
        color = 0
        eraser = False
        cacheColor = 0

        y_max=self.ymax+5

        # print(colorList)
        # return

        for point, point1 in zip(points, points1):

            # print(f"point: {point}", f"point1: {point1}", sep='\n')
            if point[1]<self.ymax and point[0]>=20 and point[0]<len(strip_X_coord):
                stripIndex = strip_X_coord.index(point[0])
                # print("stripIndex: ",stripIndex)
                color = colorList[stripIndex]
                # print("color",color)
                # for i in paintColor:
                #     if lenColor*i < point[0] < lenColor*(i+1):
                #         color = paintColor[i] 
            
            elif point[1]>y_max and point[1] <= point1[1] and color != 0:
                # print(f"color now: {color}")
                cv2.circle(img, (point[0], point[1]), 10, color, cv2.FILLED)
            

            ##eraser functionality
            if color != (0,0,0):        #eraser is not selected
                cacheColor = 0
            
            if point[1] < point1[1] and point[0] < 50 and point[1] > 350 and point[1] < 400:
                color = (0,0,0)
                eraser = True
            
            ## for showing eraser
            if point[1] < point1[1] and eraser == True:
                cv2.circle(img, (point[0], point[1]), 30, color, cv2.FILLED)
                # eraser = True
            
            if point[1]>point1[1] and eraser == True:
                eraser=False
                # continue
                color = cacheColor
            
            if point[1]<y_max and point[0]>=20 and point[0]<len(strip_X_coord) and (eraser == True):
                eraser = False

                stripIndex = strip_X_coord.index(point[0])
                # print("stripIndex: ",stripIndex)
                color = colorList[stripIndex]
            
            # print("color: ",color)
            # print("cacheColor: ", cacheColor)


        return color, eraser


    #color strip function
    def colorStrip(self,stX, stY, endY, image):
        x=stX
        y=stY

        r,g,b = 255,0,0
        color_X_Coordinates = []
        colorList = []

        # for i in range(765):
        color = (b,g,r)     #255,0,0
        color_X_Coordinates.append(20)
        while True:
            if g>=0 and g<255 and r == 255 and b == 0:
                colorList.append(color)
                # print(color)
                # b -= 1
                g += 1
                color = (b,g,r)

            elif g==255 and b==0 and r<=255 and r>0:
                colorList.append(color)
                r -= 1
                color = (b,g,r)
            
            elif r==0 and g==255 and b>=0 and b<255:
                colorList.append(color)
                b += 1
                color = (b,g,r)
            
            elif r==0 and b==255 and g<=255 and g>0:
                colorList.append(color)
                g -= 1
                color = (b,g,r)
            
            elif g==0 and b==255 and r>=0 and r<255:
                colorList.append(color)
                r += 1
                color = (b,g,r)
            
            elif r==255 and g==0 and b<=255 and b>1:
                colorList.append(color)
                b -= 1
                color = (b,g,r)
            
            elif r==255 and g==0 and b==1:
                colorList.append(color)
                break    
                
            cv2.line(image, (x, y), (x, endY), color)
            x += 1
            color_X_Coordinates.append(x)

        return color_X_Coordinates, colorList




    # eraser button
    def eraser(self, image):
        cv2.rectangle(image, (0, 350), (50, 400), (0,0,0))
        cv2.circle(image, (25, 375), 25, (255,255,255), cv2.FILLED)
        # cv2.addText()
    
    def erasePattern(self, imgCanvas, image, points, points1, currentColor):
        # color = currentColor
        eraser = False

        for point, point1 in zip(points, points1):
            if point[1] < point1[1] and point[0] < 50 and point[1] > 350 and point[1] < 400:
                eraser = True
            
            # if eraser == True:
                color = (0,0,0)      #black
                # print(color)
                if point[1] < point1[1]:
                    cv2.circle(imgCanvas, (point[0], point[1]), 30, color, cv2.FILLED)

                elif point[1] > point1[1]:
                    eraser = False
                # cv2.circle(image, (point[0], point[1]), 30, color, cv2.FILLED)
        return eraser
        

    ## main canvas function
    def canvas(self):
        scrollerStatus = False
        glider_max_y = 50
        initialColor = 0
        eraser = False

        while True:
            # self.painterPoints.clear()
            # self.stopperPoints.clear()

            # gliderStatus = True

            success, img = self.cap.read()

            #flipping the video frames
            img = cv2.flip(img, 1)

            img = cv2.resize(img, (1600,800))
            imgShape = img.shape
            # print(imgShape)

            imgCanvas = np.zeros(imgShape, np.uint8)
            # imgCanvas = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2RGB)

            # print(img.shape)

            # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            image = self.detector.findHands(img, draw = False)

            landmarksList = self.detector.findPosition(img, eraser = eraser)

            if len(landmarksList) != 0:
                #tip of index finger
                x = landmarksList[8][1]
                y = landmarksList[8][2]
                self.painterPoints.append([x,y])
                # print(f"points: {points}")

                # tip of middle finger
                x1 = landmarksList[12][1]
                y1 = landmarksList[12][2]
                self.stopperPoints.append([x1,y1])
                # print(f"points1: {points1}")
            

            self.cTime = time.time()
            fps = 1 / (self.cTime - self.pTime)
            self.pTime = self.cTime

            color_X_Coordinates, colorList = self.colorStrip(20, self.ymin, self.ymax, image)

            self.eraser(image)


            #####################       Painting        #######################
            if len(self.painterPoints) != 0 and len(self.stopperPoints) != 0:
                # print(1)
                currentColor, eraser = self.draw(self.painterPoints, self.stopperPoints, imgCanvas, color_X_Coordinates, colorList)
                # print(eraser)
                # break
            
                # eraser = self.erasePattern(imgCanvas, image, self.painterPoints, self.stopperPoints, currentColor)
                


            imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
            _, imgInv = cv2.threshold(imgGray, 0, 255, cv2.THRESH_BINARY_INV)
            imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
            # imgInv = cv2.cvtColor(imgInv, cv2.COLOR_BGR2RGB)
            image = cv2.bitwise_and(image, imgInv)
            image = cv2.bitwise_or(image, imgCanvas)

            cv2.imshow('Virtual Canvas', image)
            # cv2.imshow('canvas', imgCanvas)
            # cv2.imshow('inverse', imgInv)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # cv2.imwrite("Hand_Tracking/saved_image.jpg", img)
                break

        
        #releasing resourses
        self.cap.release()
        cv2.destroyAllWindows

if __name__ == "__main__":
    # print("hello world")
    # painter = Canvas()
    Canvas().canvas()
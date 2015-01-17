import cv2
import time

def runStream(process = lambda x: x,
              fps = 30,
              winName = 'camwin',
              filename='whiteboard.jpg',
              printTime = False):
    spf = 1.0/fps
    # cv.NamedWindow(winName)
    capture = lambda: cv2.imread(filename)
    charToCode = { '':-1,'q':1048689 }
    key = charToCode['']

    while key != charToCode['q']:
        loopStart = time.time()
        if key != charToCode['']:
            print "key = '%s'" % key
        img = process(capture())
        cv2.imshow(winName,cv2.resize(img,(640,480)))
        timeSoFar = time.time()-loopStart
        # if spf < timeSoFar:
        #     print "Too Fast! %f < %f" %(spf,timeSoFar)
        if printTime:
            print 'time: ' + str(time.time()-loopStart)
        key = cv2.waitKey(max(1,int(1000*(spf-timeSoFar))))

if __name__ == '__main__':
    runStream()


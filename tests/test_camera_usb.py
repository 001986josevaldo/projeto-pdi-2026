import cv2

for i in range(4):

    cap = cv2.VideoCapture(i, cv2.CAP_V4L2)

    print(i, cap.isOpened())

    if cap.isOpened():

        ret, frame = cap.read()

        print("RET:", ret)

        if ret:
            cv2.imshow(str(i), frame)
            cv2.waitKey(0)

        cap.release()
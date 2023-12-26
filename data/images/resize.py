import cv2

img = cv2.imread("img.jpg")
img = cv2.resize(img, (1024, 720), interpolation=cv2.INTER_AREA)
cv2.imwrite("img.jpg", img)
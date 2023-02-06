import cv2
import numpy as np
import threading
import math

#importamos archivo mqtt_client.py para usar los metodos de la clase que conectan al broker publico, asi podremos enviar la informacion de los codigos aruco
import sys
sys.path.append(".")
from mqtt_client import cliente

#pip opencv-contrib-python: descarga libreria cv2, aruco, y si es necesario, numpy

#modifica imagen, le reduce el brillo
def change_brightness(img, value):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, value)
    v[v > 255] = 255
    v[v < 0] = 0
    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

    return img

#funcion que consigue punto medio del eje x y y
def mid_points(matrix, pt1, pt2):
  matrix[0][0] = (pt1[0] + pt2[0]) / 2
  matrix[0][1] = (pt1[1] + pt2[1]) / 2
  return matrix

#conseguir el angulo de rotacion de los codigos aruco
def get_angle(bottomRight, bottomLeft):
    x = (bottomRight[0] - bottomLeft[0])
    y = (bottomRight[1] - bottomLeft[1])
    angle = math.atan2(y, x)
    angle = math.degrees(angle)
    angle *= -1

    if angle < 0:
      angle += 360
    angle = round(angle, 2)
    angle = abs(angle)
    return angle

#consigue angulo de rotacion de los codigos aruco en radianes
def get_anglerad(bottomRight, bottomLeft):
    x = (bottomRight[0] - bottomLeft[0])
    y = (bottomRight[1] - bottomLeft[1])
    angle = math.atan2(y, x)
    angle = math.degrees(angle)
    angle *= -1

    if angle < 0:
      angle += 360

    angle = abs(angle)
    angle = math.radians(angle)
    angle = round(angle, 2)
    return angle


#funcion que dibuja e imprime informacion en el frame de opencv
def draw_aruco(frame, topLeft, topRight, bottomLeft, bottomRight, MidP, X, Y,angle):
       
  #Se dibuja el cuadrado 
  cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
  cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
  cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
  cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

  #Se dibujan las lineas 
  line_thickness = 3
  cv2.line(frame, X[0], MidP[0], (0, 0, 255), thickness = line_thickness )
  cv2.line(frame, Y[0], MidP[0], (255, 0, 0), thickness = line_thickness )

  #Se imprime la información del texto 
  cv2.putText(frame, str(MidP[0]), (MidP[0][0], MidP[0][1] - 200),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,204,204),2,cv2.LINE_AA )
  cv2.putText(frame, str(f'ID: {markerID}'), (MidP[0][0] - 150, MidP[0][1] - 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 204, 204), 2, cv2.LINE_AA )
  cv2.putText(frame, str(angle) + " grados", (MidP[0][0] - 400, MidP[0][1] - 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 204, 204), 2, cv2.LINE_AA )

#conseguimos las coordenadas del aruco y lo guadamos como pares (x y y) en variables por seccion diferente
def get_coordenates(markerCorner):
  # extract the marker corners (which are always returned in
	# top-left, top-right, bottom-right, and bottom-left order)
  corners = markerCorner.reshape((4, 2))
  (topLeft, topRight, bottomRight, bottomLeft) = corners
  
  # convert each of the (x, y)-coordinate pairs to integers
  topRight = (int(topRight[0]), int(topRight[1]))
  bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
  bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
  topLeft = (int(topLeft[0]), int(topLeft[1]))

  return topLeft, topRight, bottomLeft, bottomRight

#almacenamos info de coordenadas y angulo del aruco, y la almacenamos en un diccionario
def get_ArucoInfo(markerCorner, markerID):

    topLeft, topRight, bottomLeft, bottomRight = get_coordenates(markerCorner)
 
    #Calculamos el angulo de inclinación 
    angle = get_anglerad(bottomRight, bottomLeft)

    info = {"coordenadas": [topLeft, topRight, bottomLeft, bottomRight], "angulo": (angle), "ID": (markerID)}

    return info

def send_public_client():
  info=[]  
  info.append(get_ArucoInfo(markerCorner, markerID))   
  client.connect_client(info)
     
#si es True, se visualizara la camara y su interfaz, si es falsa ejecutará la camara sin mostrar nada
visual=True

if __name__=="__main__":

  capture = cv2.VideoCapture(0)
  qrCodeDetector = cv2.aruco

  window_name = 'Camara detector qr' #Nombre de la ventana

  #resolucion 1080 p
  capture.set(3, 1920)
  capture.set(4, 1080)

  points = np.arange(8).reshape(4,2)
  MidP = np.arange(2).reshape(1,2)
  Y = np.arange(2).reshape(1,2)
  X = np.arange(2).reshape(1,2)

  client = cliente()

  while (True):
    ret, frame = capture.read()
    if ret == False:
      break  #Por si acaso no detecta nada 
    frame = cv2.resize(frame, (2040, 1080)) #Cambiar el tamaño de la ventana que despliega
    frame = change_brightness(frame, 10)

    gray = cv2.cvtColor (frame, cv2.COLOR_BGR2GRAY)

    arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_50)

    arucoParams = cv2.aruco.DetectorParameters_create()

    points, ids, rejected = qrCodeDetector.detectMarkers(gray, arucoDict, parameters = arucoParams)
    
    if len(points) > 0:
      # flatten the ArUco IDs list
      ids = ids.flatten()
      # loop over the detected ArUCo corners
      for (markerCorner, markerID) in zip(points, ids):

          topLeft, topRight, bottomLeft, bottomRight = get_coordenates(markerCorner)

          #Obtenemos coordenadas para punto medio y lineas
          mid_points(MidP, topRight, bottomLeft)
          mid_points(Y, topRight, bottomRight)
          mid_points(X, bottomLeft, bottomRight)
          
          #Calculamos el angulo de inclinación 
          angle = get_angle(bottomRight, bottomLeft)

          if visual==True:
            draw_aruco(frame, topLeft, topRight, bottomLeft, bottomRight, MidP, X, Y, angle)
          h=threading.Thread(target=send_public_client)
          h.start()
  
    if visual ==True:
      cv2.imshow(window_name, frame) #Despliega la ventana 

      if cv2.waitKey(1) & 0xFF == 27: #Presiona esc para salir 
        break
  
  capture.release()
  cv2.destroyAllWindows()
import os
from gpiozero import Button
import cv2
import time
import sched
import timeit
import datetime
import serial
import string
import pynmea2
import json
import paho.mqtt.client as mqtt
import base64

print("initiated")
button=Button(21)
button.wait_for_press()

lat=0
lng=0

def on_connect(client, userdata, flags, rc):
    print("connected with result code"+str(rc))
    client.subscribe("PO")
    Payload = '{"Latitude":"lat", "Longitude":"lng"}'

client = mqtt.Client()
client.on_connect = on_connect
client.connect("155.4.118.2", 1883, 60)

print("initiated")
while True:
    t=time.localtime()
    CurTime=time.strftime("%H : %M : %S",t)
    videoCaptureObject = cv2.VideoCapture(0)
    result = True
    while(result):
     ret,frame = videoCaptureObject.read()
     cv2.imwrite("Image.jpg",frame)
     result = False
    videoCaptureObject.release()
    cv2.destroyAllWindows()
    port="/dev/serial0"
    dataout = pynmea2.NMEAStreamReader()
    try:
        ser=serial.Serial(port)
        newdata=ser.readline()
    except:
        print("Loading values")
    if newdata[0:6] == "$GPRMC":
      newmsg=pynmea2.parse(newdata)
      lat=newmsg.latitude
      lng=newmsg.longitude
      Payload = {"Latitude" : lat, "Longitude" : lng}
      client.publish("PO", json.dumps(Payload))
      gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
      print(gps)
      f=open("/home/pi/Location.html","w")
      f.write(gps+"""<!DOCTYPE html>

<html>

   <head>

      <style>
      body {
   display: block;
   margin: 8px;
}
     #content{
           width:98%;
           margin:auto;
           margin-top:20px;
           margin-left:auto;
           margin-right:auto;
           margin-bottom:auto;
            border-radius: 15px;
            border: 5px solid orange;
            padding-bottom: 55px;
        }
         #Button{
           width:auto;
           margin:auto;
           margin-top:10px;
           margin-left:auto;
           margin-right:auto;
           margin-bottom:10px;
               font-size:200%;
               color:blue;
               border-radius: 13px;
               border: 2px solid orange;
               transition-duration: 0.4s;
               cursor: pointer;
               display: flex;
               text-align: center;
        }

     </style>

      <title></title>
      <meta charset="windows-1252">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <script src="mqttws31.js" type="text/javascript"></script>
      <script type="text/javascript">
      var client;
      var reconnectTimeout;
      var host="155.4.118.2";
      var port=9001;
      var JSONobj;
      var jasonfrom;
      
      
           client = new Paho.MQTT.Client(host, port, "clientId");
           
// set callback handlers
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// connect the client
client.connect({onSuccess:onConnect});


// called when the client connects
function onConnect() {
  // Once a connection has been made, make a subscription and send a message.
  console.log("onConnect");
  
  client.subscribe("G7");
  /*
  message = new Paho.MQTT.Message("Hello ET1544 Students");
  message.destinationName = "G7";
  client.send(message);
  */
  
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
   console.log("onConnectionLost:"+responseObject.errorMessage);
   
  }
}

// called when a message arrives
function onMessageArrived(message) {
  console.log("onMessageArrived:"+message.payloadString);
   
     if(message.payloadString!="ONOFF"){
  try{
     
               jsonobj=JSON.parse(message.payloadString);
               
                    jasonfrom =Object.keys(jsonobj).length;  

  
                                 //onsole.log(evt.data); 
                                 }catch(err){
                                      
                                    console.log(err); 
                                 }
     }
 
  document.getElementById("Button").onclick = function() {SendOnOFF()};
  
  function SendOnOFF(){
     client.subscribe("G8");
      message = new Paho.MQTT.Message("ONOFF");
      message.destinationName = "G8";
      client.send(message);
  }
}
   </script>
   </head>
   <body id="Body"> 
            <div class="mapouter">
               <div class="gmap_canvas">
                  <iframe width="800" height="800" id="gmap_canvas" src="http://maps.google.com/maps?q="""+str(lat)+""","""+str(lng)+"""5&z=12&output=embed" height="450" width="600"></iframe>
                  <a href="https://embedgooglemap.net/maps/40"></a><br>
                  <style>.mapouter{position:relative;text-align:left;height:1000px;width:1000px;}</style>
                  <a href="https://www.embedgooglemap.net">embedgooglemap.net</a>
                  <style>.gmap_canvas {overflow:hidden;background:none!important;height:1000px;width:1000px;}</style>
               </div>
            </div>
   </body>
</html>""")
      f.close()
      os.system("sudo obexftp --nopath --noconn --uuid none --bluetooth E4:C4:83:F4:5F:1A --channel 12 -p Location.html Image.jpg")
      time.sleep(30)
      os.system("sudo rm Image.jpg")
      client.loop()
      print("done")

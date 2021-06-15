import socket
UDP_IP = "0.0.0.0"
UDP_PORT = 3000

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
while True:
  data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
  print("Receive message {0} ".format(data))
  s=data.decode('utf-8').split(',')
  sensor=s[0]
  temp=float(s[1])
  hum=float(s[2])
  print("Sensor id {0}, temp {1}, hum {2} ".format(sensor,temp,hum))

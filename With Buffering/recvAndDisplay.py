import socket
import struct
import cv2
import numpy as np
header_struct = struct.Struct('!I')

def recvall(sock, length):
    blocks = []
    while length:
        block = sock.recv(length)
        if not block:
            raise EOFError('socket closed with {} bytes left'
                           ' in this block'.format(length))
        length -= len(block)
        blocks.append(block)
    return b''.join(blocks)


def display():
    host="127.0.0.1"
    port=1578
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host,port))
    sock.listen(1)
    s,_=sock.accept()
    c=0
    
    try:
        while True:
            print("Asking header")
            data=recvall(s,header_struct.size)
            # print("Got header")
            (frame_size,)=header_struct.unpack(data)
            frame=recvall(s,frame_size)
            # if(frame.decode()=="END"):
            #     break
            nparr = np.fromstring(frame, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # print(len(frame))
            if(frame is None):
                break
            cv2.imshow("Frame",frame)
            # frameBuf.put(frame)
            # print("bump",c)
            c+=1

            if cv2.waitKey(10) and 0xFF == ord('q'):
                break
    finally:
        # endEvent.set()
        s.close()
        sock.close()


display()
import socket
import cv2
import argparse
import struct
import numpy as np
import imutils
from imutils.video import FPS



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






def reciever(host,port):
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # host='localhost'
    sock.bind((host,port))
    # displayEvent=threading.Event()
    # endEvent=threading.Event()
    # thread=threading.Thread(target=display,args=(displayEvent,endEvent))
    # thread.start()
    sock.listen(1)
    s,_=sock.accept()
    c=0
    fps = FPS().start()
    
    try:
        while True:
            # print("Asking header")
            data=recvall(s,header_struct.size)
            # print("Got header")
            (frame_size,)=header_struct.unpack(data)
            frame=recvall(s,frame_size)
            # if(frame.decode()=="END"):
            #     break
            nparr = np.fromstring(frame, np.uint8)
            frameD = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # print(len(frame))
            if(frame is None):
                break
            try:
                cv2.imshow("Frame",frameD)
            except Exception:
                break
            # frameBuf.put(frame)
            # displayEvent.set()
            # print("bump",c)
            c+=1

            cv2.waitKey(10)
            fps.update()

    finally:
        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        # endEvent.set()
        s.close()
        sock.close()



def sender(host,port,src):
    cap=cv2.VideoCapture("./"+src)
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # host='localhost'
    s.connect((host,port))
    c=0
    try:
        while(cap.isOpened()):
            ret,frame=cap.read()
            if(not ret):
                msg=b"END"
                s.sendall(header_struct.pack(len(msg)))
                s.sendall(msg)
                break
            # cv2.imshow("Here",frame)
            encodedData=cv2.imencode(".jpg",frame)[1].tostring()
            s.sendall(header_struct.pack(len(encodedData)))
            s.sendall(encodedData)
            # print("bump",c)
            c+=1

            # if cv2.waitKey(0) & 0xFF == ord('q'):
            #     break
    finally:
        # s.close()
        pass




def main():
    roles = ('reciever', 'sender')
    parser = argparse.ArgumentParser(description='Strea Video over TCP sockets')
    parser.add_argument('role', choices=roles, help='which role to play')
    parser.add_argument('host', help='interface the server listens at;'
                        ' host the client sends to')
    parser.add_argument('bytecount', type=int, nargs='?', default=16,
                        help='number of bytes for client to send (default 16)')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, dest="port",
                        help='port at which sender sends and reviever listens(default 1060)')
    parser.add_argument("-i",dest="src",help="Input video file")
    args=parser.parse_args()

    if args.role=='reciever':
        reciever(args.host,args.port)
    else:
        sender(args.host,args.port,args.src)

    







if __name__ == "__main__":
    main()    
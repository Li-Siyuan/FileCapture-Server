#!/usr/bin/python
# -*- coding: utf-8 -*-

#ok
import socket
import hashlib
import struct
import base64
STORE_DIR='/root/recvData/'

HOST = 'localhost'
PORT = 9527
BUFFER_SIZE = 1024

#这个编码在客户端解不开

HEAD_STRUCT = '128sIq32s'

info_size = struct.calcsize(HEAD_STRUCT)


#md5校验，两处校验必有一次错误

def cal_md5(file):
    with open(file, 'rb') as fr:
        md5 = hashlib.md5()
        md5.update(fr.read())
        md5 = md5.hexdigest()
        return md5


# def unpack_file_info(file_info):
#     file_name, file_name_len, file_size, md5 = struct.unpack(HEAD_STRUCT, file_info[:176])
#     file_name = file_name[:file_name_len]
#     return file_name, file_size, md5


def recv_file():



    #前期没有发现时序不统一的问题，所以加了此处校验，实际没有必要
    # file_name=''
    # #假设信息为空，就一直处于阻塞态
    # while(file_info_package==''):
        # file_info_package = client_socket.recv(info_size)
    print 'waiting info'
    file_name=client_socket.recv(128)
    print file_name
    file_size=client_socket.recv(8)
    print file_size
    md5_recv=client_socket.recv(32)
    print md5_recv
    #信息不为空，解包传递文件
    #file_info_package = client_socket.recv(info_size)
    # print file_info_package
    # file_name, file_size, md5_recv = unpack_file_info(file_info_package)


    #接收文件内容进行二进制写，其实可以直接接收二进制流不进行decode
    recved_size = 0
    file_size=long(file_size)
    with open(STORE_DIR+file_name+'.txt', 'wb') as fw:
        #逻辑上没错，不过要考虑服务器网速
        while recved_size < file_size:
            remained_size = file_size - recved_size
            recv_size = BUFFER_SIZE if remained_size > BUFFER_SIZE else remained_size

            recv_file = client_socket.recv(recv_size)
            recved_size += recv_size
            # print recv_file
            #recv_file=base64.b64decode(recv_file)
	        #missing_padding = 4 - len(recv_file) % 4
            #if missing_padding:
            #    recv_file += b'='* missing_padding
            #recv_file=base64.decodestring(recv_file)

            fw.write(recv_file)
        #检测md5是否正确
        md5 = cal_md5(STORE_DIR+file_name+'.txt')
        if md5 != md5_recv:
            print 'MD5 compared fail!'
        else:
            print 'Received successfully'
    

if __name__ == '__main__':
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (HOST, PORT)
        sock.bind(server_address)
        #开启单个机器接收，多了会丢包
        sock.listen(1)
        #阻塞等待连接
        client_socket, client_address = sock.accept()
        print "Connected %s successfully" % str(client_address)
        while True:
            recv_file()
    except socket.errno, e:
            print "Socket error: %s" % str(e)
    finally:
        sock.close()


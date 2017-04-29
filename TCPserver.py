import socket
import thread
import hashlib
import os.path
import pygtk
pygtk.require('2.0')
import gtk, gtk.glade

serversock = socket.socket()
host = "192.168.0.1"
port = 8888
serversock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1) # Allows user to reuse the ports 
serversock.bind((host,port));
serversock.listen(10);
print "Waiting for a connection....."

clientsocket,addr = serversock.accept()
print("Got a connection from %s" % str(addr))

dialog = gtk.FileChooserDialog("BTV Receiver", # Make sure that glade3 is installed in case of centOS 6 
                               None,
                               gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
dialog.set_default_response(gtk.RESPONSE_OK)

response = dialog.run()
if response == gtk.RESPONSE_OK:
    print dialog.get_filename(), 'selected'
elif response == gtk.RESPONSE_CANCEL:
    print 'Closed, no files selected'
save_path=dialog.get_filename()
dialog.destroy()


while True:
    size = clientsocket.recv(16) # Note that you limit your filename length to 255 bytes.
    if not size:
        break
    fsize = int(size, 2)
    filename = clientsocket.recv(fsize)
    filesize = clientsocket.recv(32)
    filesize = int(filesize, 2)
    completeName=os.path.join(save_path,filename)
    file_to_write = open(completeName, 'wb')
    chunksize = 2097152
    while filesize > 0:
        if filesize < chunksize:
            chunksize = filesize
        data = clientsocket.recv(chunksize)
        file_to_write.write(data)
        filesize -= chunksize
    file_to_write.close()
    print (filename+' received successfully')
serversock.close()

s = socket.socket()
host = "192.168.0.2"
port = 8888
s.connect((host, port))

dialog = gtk.FileChooserDialog("BTV Sender",
                               None,
                               gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
dialog.set_default_response(gtk.RESPONSE_OK)

response = dialog.run()
if response == gtk.RESPONSE_OK:
    print dialog.get_filename(), 'selected'
elif response == gtk.RESPONSE_CANCEL:
    print 'Closed, no files selected'
path=dialog.get_filename()
dialog.destroy()

directory = os.listdir(path)
for files in directory:
    print files
    filename = files
    size = len(filename)
    size = bin(size)[2:].zfill(16) # encode filename size as 16 bit binary
    s.send(size)
    s.send(filename)

    filename = os.path.join(path,filename)
    filesize = os.path.getsize(filename)
    filesize = bin(filesize)[2:].zfill(32) # encode filesize as 32 bit binary
    s.send(filesize)

    file_to_send = open(filename, 'rb')

    l = file_to_send.read()
    s.sendall(l)
    file_to_send.close()
    print('File Sent')
s.close()

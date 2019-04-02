# Building The Best ChatBot with Deep NLP



# Importing the libraries
import seq2seq_wrapper
import importlib
importlib.reload(seq2seq_wrapper)
import data_preprocessing
import data_utils_1
import data_utils_2



########## PART 1 - DATA PREPROCESSING ##########



# Importing the dataset
metadata, idx_q, idx_a = data_preprocessing.load_data(PATH = './')

# Splitting the dataset into the Training set and the Test set
(trainX, trainY), (testX, testY), (validX, validY) = data_utils_1.split_dataset(idx_q, idx_a)

# Embedding
xseq_len = trainX.shape[-1]
yseq_len = trainY.shape[-1]
batch_size = 16
vocab_twit = metadata['idx2w']
xvocab_size = len(metadata['idx2w'])  
yvocab_size = xvocab_size
emb_dim = 1024
idx2w, w2idx, limit = data_utils_2.get_metadata()



########## PART 2 - BUILDING THE SEQ2SEQ MODEL ##########



# Building the seq2seq model
model = seq2seq_wrapper.Seq2Seq(xseq_len = xseq_len,
                                yseq_len = yseq_len,
                                xvocab_size = xvocab_size,
                                yvocab_size = yvocab_size,
                                ckpt_path = './weights',
                                emb_dim = emb_dim,
                                num_layers = 3)



########## PART 3 - TRAINING THE SEQ2SEQ MODEL ##########



# See the Training in seq2seq_wrapper.py



########## PART 4 - TESTING THE SEQ2SEQ MODEL ##########



# Loading the weights and Running the session
session = model.restore_last_session()

# Getting the ChatBot predicted answer
def respond(question):
    encoded_question = data_utils_2.encode(question, w2idx, limit['maxq'])
    answer = model.predict(session, encoded_question)[0]
    return data_utils_2.decode(answer, idx2w) 

# Setting up the chat
#while True :
#  question = input("You: ")
#  answer = respond(question)
#  print ("ChatBot: "+answer)


#!/usr/bin/env python3

import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    #print("8")
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    #print("9")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #print("10")
    sel.register(conn, events, data=data)
    #print("11")


def service_connection(key, mask):
    #print("12")
    sock = key.fileobj
    #print("13")
    data = key.data
    #print("14")
    if mask & selectors.EVENT_READ:
        #print("15")
        recv_data = sock.recv(1024)  # Should be ready to read
        #print("16")
        if recv_data:
            #print("17")
            data.outb += recv_data
            #print("18")
        else:
            print("closing connection to", data.addr)
            sel.unregister(sock)
            #print("19")
            sock.close()
            #print("20")
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            #print("21")
            print("receiving", repr(data.outb), "from", data.addr)
            question = str(data.outb, encoding='utf-8')
            answer = respond(question)
            message = bytes(answer+"\n", encoding='utf-8')
            #print("22")
            print("sending", repr(message), "to", data.addr)
            sent = sock.send(message)  # Should be ready to write
            #print("23") 
            #print(sent)
            data.outb = data.outb[len(data.outb):]
            #print("24")

host, port = "127.0.0.1", 65432
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        #print("1")
        events = sel.select(timeout=None)
        #print("2")
        for key, mask in events:
            #print("3")
            if key.data is None:
                #print("4")
                accept_wrapper(key.fileobj)
                #print("5")
            else:
                #print("6")
                service_connection(key, mask)
                #print("7")
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
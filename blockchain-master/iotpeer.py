from P2PFramework import p2p
import math
import scipy.stats as st
import Consensus.Utilities as ut
import threading
import time
import operator

blockchain_file_name = 'blockchain'

class shared_thread(threading.Thread):


    msglist=[]
    winlock=threading.Lock()

    def __init__(self,msg):
        threading.Thread.__init__(self)
        self.msg=msg
        pass;

    def run(self):
        with shared_thread.winlock:
            shared_thread.msglist.append(self.msg)
            #print shared_thread.msglist
        pass;


class Handles(object):

    window = False

    def __init__(self, operations):
        self.operations = operations
        self.window=False

    # Admin update module
    def admin_update(self,iot,addr,msg):

        print "Incomplete module"

        return

    # UPDATE PRODUCERS
    def update_producers(self,iot,addr,msg):

        producers=msg.split(",")

        if iot.update_producers(producers):
            print "Successfully updated witnesses/producers"

        return

    # UPDATE SHARED KEY
    def update_sharedkey(self,iot,addr,msg):

        sharedkey=msg
        if iot.update_sharedkey(sharedkey):
            print "Successfully updated shared key"

        return


    # send missing block
    # Command - RQMB
    def send_missing_block(self,iot1,addr,msg):

        # I

        required_block=int(msg)
        print "Requested block",required_block

        block_data=self.operations.read_blocks(required_block)
        #print block_data
        if block_data:
            iot1.send_data("RCMB",block_data)
        else:
            print "I do not have the block myself"
            return
        pass

    # RECEIVE MISSING BLOCK
    # Command - RCMB
    def missing_block_update(self,iot1,addr,msg):


        # add data and address to queue if the window is still open

        if Handles.window:
            shared_thread((addr,msg)).start()
        else:
            print "Window closed"

        pass

    # temp functionality - opening window for sometime
    # Command - WIND
    def window_open(self,iot1,addr,msg):


        if Handles.window:
            Handles.window=False
        Handles.window=True
        time.sleep(6)
        Handles.window=False
        self.compare()
        return

    # compare received blocs
    def compare(self):

        '''
        get msgs from unique address
        filter by size
        choose the first biggest one
        '''

        temp = {}
        print ut.get_mymac()



        for ind,msg in enumerate(shared_thread.msglist):
            addr,data=msg

            if addr not in temp:
                # validate data blocks individually and also if the block fits my blockchain
                if self.operations.validate_chain(data):
                    temp[addr]=data

                    #if len(data)>biggest_chain_length:
                      #  biggest_chain_length=len(data)
                       # biggest_chain_address=addr

        biggest_chain=None#temp[biggest_chain_address]

        sorted_chains = sorted(temp.items(), key=operator.itemgetter(1))
        searching_chain=True

        while searching_chain:

            if len(sorted_chains)<1:
                break

            biggest_chain=sorted_chains[0][1]
            if self.operations.fit(biggest_chain):
                searching_chain=False
            else:
                sorted_chains=sorted_chains[1:]


        print "biggest chain",biggest_chain

        if biggest_chain==None:
            return

        start_index=int(biggest_chain[0])

        # Store the latest block
        newcontent = ''
        try:
            with open(blockchain_file_name, 'r') as f:
                content = f.readlines()

                if len(content) >= 1:

                    for ind,line in enumerate(content):
                        if int(line[0])==start_index:
                            newcontent=''.join(content[:ind])+biggest_chain

                            break
                print newcontent

        except Exception as e:
            print e.message

        # clear the message window
        shared_thread.msglist=[]

        try:
            with open(blockchain_file_name,'w') as f:

                f.write(newcontent)
        except Exception as e:
            print e.message

        return

    # update blockchain
    # command - UBLC

    def update_bc(self, iot1, addr, msg):

        bc = self.operations.ojbectfy_block(msg)
        print bc.data
        if bc.validate_block(self.operations.latest_block):
            print "valid block"
            bc.store_block()
            self.operations.latest_block = bc
            return True
        else:
            if ((int(bc.index) - int(self.operations.latest_block.index)) != 1):
                print "missing blocks, broadcast to get the missing block"
                # start timer
                Handles.window=True
                iot1.send_data("RQMB",str(self.operations.latest_block.index))
                time.sleep(6)
                Handles.window=False
                # stop timer

                # compare all collected data and choose the block after validation
                self.compare()
                # DATA FROM QUEUE

            elif bc.pre_hash != self.operations.latest_block.hash_val:
                print "invalid block, dropping"
                return False

        return False



    # new block method
    # command - NBLC

    def new_block(self,iot1,addr,msg):
        """
        If you get the NBLC command call this handler so that is can check if it is it's turn and if it is add it to the blockchain
        :param iot1:
        :param addr:
        :param msg:
        :return: True or False indicating whether success
        """

        #check turn
        print "entered handler"
        if iot1.producers==None:
            print "Error no witness found"
            return False

        mymac=ut.get_mymac()
        if mymac.lower() in iot1.producers:
            ind=ut.whoseturn(len(iot1.producers))
            print "Turn:",iot1.producers[ind]
            if iot1.producers[ind]==mymac.lower():
                print "my turn";
                # add block
                newblock=self.operations.generate_block(msg)
                content = [str(newblock.index), newblock.pre_hash, str(newblock.time_stamp), newblock.data, newblock.hash_val]
                data = ','.join(content)
                # broadcast latest block
                iot1.send_data("UBLC",data)


        return True;

    def hell(self,iot,addr,msg):
        print "Message ffrom hell",msg;
        return


class p2pInstance(object):

    def __init__(self,handlers):

        #host='10.0.0.187';
        self.handlers=handlers;
        self.port = 2433
        self.iot1 = p2p.IOTPeer(self.port,'iot1',None,contype="udp")
        self.iot1.addhandler("HELL",self.handlers.hell)
        self.iot1.addhandler("ADMI",self.handlers.admin_update)
        self.iot1.addhandler("PROD",self.handlers.update_producers)
        self.iot1.addhandler("NBLC",self.handlers.new_block)
        self.iot1.addhandler("UBLC",self.handlers.update_bc)
        self.iot1.addhandler("RQMB", self.handlers.send_missing_block)
        self.iot1.addhandler("RCMB",self.handlers.missing_block_update)
        self.iot1.addhandler("WIND",self.handlers.window_open)

    def run_server(self):
        self.iot1.serverloop()


class p2pThread(threading.Thread):

    def __init__(self,handlers):
        self.threadname="p2p"
        threading.Thread.__init__(self)
        self.handlers=handlers
        self.iot=p2pInstance(self.handlers)

    def run(self):
        print "Starting p2p";
        self.iot.run_server()





# Quite useful when the number of Devices are really high
def get_sample(N,confidence,error,variability=None):
    '''
    Using Central Limit theorem, calculate the sample size required for the given confidence and error

    :param N:
    :param confidence:
    :param error:
    :param variability:
    :return:
    '''

    if confidence>1 or confidence<0:
        return None;

    if not variability:
        variability=0.5;

    z=-st.norm.ppf(variability*(1-confidence));
    n=(math.pow(z,2)*variability*(1-variability))/math.pow(error,2)

    if N<n:
        n=(n*N)/(n+N-1);

    return int(n);



'''
peerid="Iot1"
idlen=len(peerid)
msg = struct.pack("!4sL%ds%ds" % (msglen,idlen), msgtype, msglen, msgdata,peerid)
print msg;
print msg.encode("hex")

msg = struct.pack("!4sL%d"% msglen,msgtype,msglen)
print msg;
print msg.encode("hex")
'''


#print get_sample(10,0.95,0.05,0.5)
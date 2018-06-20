import socket
import struct
import threading
import traceback
import re
from subprocess import Popen, PIPE


class IOTPeer(object):
    def __init__(self, serverport, peerid, serverhost=None, debug=False, contype="tcp", operation=None):
        self.maxpeers = 5
        self.serverport = serverport
        if serverhost:
            self.serverhost = serverhost
        else:
            self.serverhost = self.__initServerhost(contype)

        self.peerid = peerid
        self.protocol = contype
        self.peers = {}
        self.router = None
        self.handlers = {}
        self.debug = debug
        # Dpos Producers/witnesses
        self.producers = []
        self.operation = operation


    def __initServerhost(self, contype):

        if contype == "tcp":
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect(("www.google.com", 80))
            self.serverhost = s.getsockname()[0]
            s.close()
        return

    def update_producers(self, producers):

        try:
            self.producers = producers
        except Exception as e:
            return False

        return True

    def update_sharedkey(self, key):
        try:
            self.key = key
        except Exception as e:
            return False
        return True

    def get_mac(self, addr):
        '''
        Get Mac Address using the Ip address from ARP table
        :param addr:
        :return:
        '''
        try:
            pid = Popen(["arp", "-n", addr[0]], stdout=PIPE)
            s = pid.communicate()[0]
            mac = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", s).groups()[0]
            print mac
        except Exception as e:
            return None

        return mac

    def decode_data(self, data, nbytes, addr):

        try:
            msgtype = data[:4]

            if not msgtype: return (None, None)
            del data[:4]
            lenstr = data[:4]
            del data[:4]
            msglen = int(struct.unpack("!L", lenstr)[0])
            msg = ""

            while len(msg) != msglen:
                minlen = min(1024, msglen - len(msg))
                mydata = data[:minlen]
                del data[:minlen]
                if not len(mydata):
                    break
                msg += mydata

            if len(msg) != msglen:
                return (None, None)

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print e
            if self.debug:
                traceback.print_exc()
            return (None, None)

        return (str(msgtype), str(msg))

        pass;

    def make_data(self, msgtype, data):

        msglen = len(data)
        msg = struct.pack("!4sL%ds" % msglen, msgtype, msglen, data)
        print msg

        return msg

    def mainhandler(self, data, nbytes, addr):
        '''
        Create a new connection, receive command and message and bassed on the command redirect to the appropriate handler
        :param clientsock:
        :return:
        '''

        try:
            command, msg = self.decode_data(data, nbytes, addr)

            if command: command = command.upper();

            if command in self.handlers:
                self.handlers[command](self, addr, msg)
            else:
                print "Invalid command, no handler found"

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print e;
            if self.debug:
                traceback.print_exc()

        pass;

    def addhandler(self, msgtype, handler):
        # --------------------------------------------------------------------------
        """ Registers the handler for the given message type with this peer """
        assert len(msgtype) == 4
        self.handlers[msgtype] = handler
        pass;

    def send_data(self, command, data):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.connect(('255.255.255.255', self.serverport))
            msg = self.make_data(command, data)
            print "sending %s" % msg
            s.send(msg)
            print "send successfully"
            s.close()
        except Exception as e:
            print e.message

    '''
    Main server logic
    '''

    def serverloop(self, backlog=5):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', self.serverport))

        self.shutdown = False

        '''
        Listen to the binded port, whenever you get a message create a new thread to handle the message;
        '''
        while not self.shutdown:
            try:

                # data,addr = s.recvfrom(1024)
                data = bytearray(2000)
                nbytes, addr = s.recvfrom_into(data, 1024)

                t = threading.Thread(target=self.mainhandler,
                                     args=[data, nbytes, addr])
                t.start()
            except KeyboardInterrupt:
                print 'Shutting Down the server'
                self.shutdown = True
                continue
            except Exception as e:
                continue

        s.close()
        return

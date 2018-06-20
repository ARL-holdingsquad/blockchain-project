import time
import socket
import struct
import sys

tb0=1509740483L
timeslot = 3;  # AFTER 3 Seconds change producer
no_of_producers=3;

def gettime_ntp(addr='time.nist.gov'):
    # http://code.activestate.com/recipes/117211-simple-very-sntp-client/

    TIME1970 = 2208988800L      # Thanks to F.Lundh
    client = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    data = '\x1b' + 47 * '\0'
    client.sendto( data, (addr, 123))
    data, address = client.recvfrom( 1024 )
    if data:
        t = struct.unpack( '!12I', data )[10]
        t -= TIME1970
        return time.ctime(t),t


#get current time anc calculate the block that needs to produce at the given time
def whoseturn(no_of_producers):

    currtime=gettime_ntp()[1]
    totalslots= (currtime-tb0)/timeslot;
    print totalslots%no_of_producers,currtime
    return totalslots % no_of_producers

#validate that the timestamp and producer are correct
def validate_timestamp(producer,timestamp):

    ts=(timestamp-tb0)/timeslot
    if ts%no_of_producers==producer:
        return True;
    return False;

#print gettime_ntp()

# Get my mac address
def get_mymac():

    from uuid import getnode as get_mac
    mac=None;

    try:
        mac = get_mac()
        mac = ':'.join(("%012X" % mac)[i:i + 2] for i in range(0, 12, 2))

    except Exception as e:
        return None

    return mac


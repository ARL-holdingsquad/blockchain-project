from block import Block
from hashlib import sha256
import csv
cert_blockchain_file_name = 'cert_blockchain.csv'


class CertBlock(Block):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.cert_id = None
        self.cert_status = True
        self.request_time_stamp = None
        self.producer = None

    def set_cert_block(self,
                       cert_id,
                       cert_status,
                       index,
                       pre_hash,
                       data,
                       time_stamp=None,
                       hash_val=None,
                       producer=None,
                       request_time=None):
        self.set_block(index, pre_hash, data, time_stamp, hash_val)
        self.cert_id = cert_id
        self.cert_status = cert_status
        self.hash_val = self.calculate_hash_for_block()
        self.producer = producer
        self.request_time_stamp = request_time

    def calculate_hash_for_block(self):
        return str(sha256(str(self.index) + self.pre_hash + self.time_stamp + self.data +
                          self.cert_id + self.cert_status).hexdigest())


    def init_first_block(self):
        self.index = 0
        self.pre_hash = "0"
        self.data = "cert"
        self.time_stamp = "1510816805"  # str(time()).split('.')[0]
        self.cert_id = "0"
        self.cert_status = True
        self.producer = "0"
        self.hash_val = self.calculate_hash_for_block()

    def stringify_block(self):
        content = [str(self.index), self.pre_hash, str(self.time_stamp), self.data,
                   self.cert_id, self.cert_status,
                   self.hash_val]
        return ','.join(content) + '\n'

    def store_block(self, mode='a'):
        block_str = self.stringify_block()
        print block_str
        try:
            with open(cert_blockchain_file_name, mode) as f:
                w = csv.writer(f)
                w.writerow(self.stringify_block())
        except Exception as e:
            print e.message

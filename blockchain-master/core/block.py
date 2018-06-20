from time import time
from hashlib import sha256
import csv

blockchain_file_name = 'blockchain'


class Block(object):
    def __init__(self, index=None, pre_hash=None, time_stamp=None, data=None, hash_val=None):
        self.index = index
        self.pre_hash = pre_hash
        self.time_stamp = time_stamp
        self.data = data
        self.hash_val = data

    def set_block(self, index, pre_hash, data, time_stamp=None, hash_val=None):
        self.index = int(index)
        self.pre_hash = str(pre_hash)
        self.data = data
        self.time_stamp = str(time()).split('.')[0] if time_stamp is None else time_stamp
        self.hash_val = self.calculate_hash_for_block() if hash_val is None else str(hash_val)

    def init_first_block(self):
        self.index = 0
        self.pre_hash = "0"
        self.data = "This is the first block"
        self.time_stamp = "1510816805"#str(time()).split('.')[0]
        self.hash_val = self.calculate_hash_for_block()

    def store_block(self, mode='a'):
        block_str = self.stringify_block()
        print block_str
        try:
            with open(blockchain_file_name, mode) as f:
                # w = csv.writer(f)
                # w.writerow(self.stringify_block())
                f.write(block_str)
                f.write('\n')
        except Exception as e:
            print e.message

    def stringify_block(self):
        content = [str(self.index), self.pre_hash, str(self.time_stamp), self.data, self.hash_val]
        print self.pre_hash
        return ','.join(content)

    def calculate_hash_for_block(self):
        return str(sha256(str(self.index) + self.pre_hash + self.time_stamp + self.data).hexdigest())

    def validate_block(self, pre_block):
        return False if pre_block.index + 1 != self.index or pre_block.hash_val != self.pre_hash or \
                 self.calculate_hash_for_block() != self.hash_val else True


class BlockChain(object):
    def __init__(self, blockchain_str=None):
        self.block_chain = [] if blockchain_str is None else self.__objectify_block(blockchain_str)

    def get_latest_block(self):
        return self.block_chain[-1] if len(self.block_chain) != 0 else None

    def load_existing_blockchain(self):
        self.block_chain = self.__get_existing_blockchain()

    def __get_existing_blockchain(self):
        try:
            blockchain = []
            with open(blockchain_file_name, 'r+') as f:
                reader = csv.reader(f)
                print reader
                for line in reader:
                    blockchain += self.__objectify_block(line),
                return blockchain
        except OSError as e:
            print e.message
            return []
        except Exception as e:
            print e.message
            return []

    def __objectify_block(self, block_str):
        block_item = Block()
        block_item.index, block_item.pre_hash, block_item.data, block_item.hash_val, block_item.time_stamp = \
            block_str[:-1].split(',')
        print block_item
        return block_item

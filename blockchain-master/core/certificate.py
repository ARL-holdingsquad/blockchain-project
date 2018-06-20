from subprocess import Popen, PIPE, STDOUT


class Certificate(object):
    def __init__(self):
        # attribution for cert
        pass

    def set_cert(self):
        pass

    def create(self):
        pass

    def revoke(self):
        pass

    @staticmethod
    def get_cert_id_and_status_and_public(cert_encoded_str):
        p = Popen(['java', '-jar', './CertToolKit.jar', '-c', cert_encoded_str], stdout=PIPE, stderr=STDOUT)
        cert_id, is_valid, public_key = p.stdout.readline()
        return cert_id, is_valid, public_key

    @staticmethod
    def get_cert_str_from_file(file_path):
        p = Popen(['java', '-jar', './CertToolKit.jar', '-e', file_path], stdout=PIPE, stderr=STDOUT)
        return p.stdout.readline()

    @staticmethod
    def get_cert_text_from_file(file_path):
        p = Popen(['java', '-jar', './CertToolKit.jar', '-l', file_path], stdout=PIPE, stderr=STDOUT)
        return ''.join(p.stdout.readlines())

    @staticmethod
    def get_cert_text_from_decoded_str(cert_encoded_str):
        p = Popen(['java', '-jar', './CertToolKit.jar', '-d', cert_encoded_str], stdout=PIPE, stderr=STDOUT)
        return ''.join(p.stdout.readlines())


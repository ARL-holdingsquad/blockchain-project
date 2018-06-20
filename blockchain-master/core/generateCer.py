from OpenSSL import crypto, SSL
import uuid
import time

timestr = time.strftime("%Y%m%d-%H%M%S")
CERT_FILE = "selfsigned_"+timestr+".crt"
KEY_FILE = "private.key"

def create_self_signed_cert():
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)
    # create a self-signed cert
    cert = crypto.X509()
    # use mac address as the cert identifier
    cert.get_subject().CN=':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8 * 6, 8)][::-1])
    cert.set_serial_number(12345)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')
    #print cert.get_subject()
    open(CERT_FILE, "wt").write(
        crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    open(KEY_FILE, "wt").write(
        crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

create_self_signed_cert()

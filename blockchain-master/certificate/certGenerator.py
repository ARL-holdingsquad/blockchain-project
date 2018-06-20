from py4j.java_gateway import JavaGateway,GatewayParameters
import json

def generate_cvc():
    gateway = JavaGateway(gateway_parameters=GatewayParameters(port=3335))
    cvc = gateway.entry_point.CvcCert()
    return cvc
    #print cvc

def to_serialize(cvc):
    cvcSerialized=json.dumps(cvc)
    return cvcSerialized
    #print cvcSerialized

def to_deserialize(cvcSerialized):
    cvcDeserialed=json.loads(cvcSerialized)
    return cvcDeserialed
    #print cvcDeserialized

cvc=generate_cvc()
cvcSerialized=to_serialize(cvc)
print cvcSerialized
print to_deserialize(cvcSerialized)
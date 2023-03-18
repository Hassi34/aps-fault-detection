
import os
from dotenv import load_dotenv

load_dotenv()

SECURITY_PROTOCOL=os.getenv("SECURITY_PROTOCOL")
SSL_MACHENISM=os.getenv("SSL_MACHENISM")

CLUSTER_API_KEY=os.getenv("CLUSTER_API_KEY")
CLUSTER_API_SECRET = os.getenv('CLUSTER_API_SECRET')
BOOTSTRAP_SERVER = os.getenv('BOOTSTRAP_SERVER')

#API_SECRET_KEY = os.getenv('API_SECRET_KEY')

ENDPOINT_SCHEMA_URL  = os.getenv('ENDPOINT_SCHEMA_URL')
SCHEMA_REGISTRY_API_KEY = os.getenv('SCHEMA_REGISTRY_API_KEY')
SCHEMA_REGISTRY_API_SECRET = os.getenv('SCHEMA_REGISTRY_API_SECRET')


def sasl_conf():

    sasl_conf = {'sasl.mechanism': SSL_MACHENISM,
                'bootstrap.servers':BOOTSTRAP_SERVER,
                'security.protocol': SECURITY_PROTOCOL,
                'sasl.username': CLUSTER_API_KEY,
                'sasl.password': CLUSTER_API_SECRET
                }
    print(sasl_conf)
    return sasl_conf



def schema_config():
    return {'url':ENDPOINT_SCHEMA_URL,
    
    'basic.auth.user.info':f"{SCHEMA_REGISTRY_API_KEY}:{SCHEMA_REGISTRY_API_SECRET}"

    }

if __name__ == '__main__':
    sasl_conf()


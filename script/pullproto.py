import os.path
import urllib.request

protobuf_url = "https://buf.build/fxnlabs/api-gateway/raw/main/-/apigateway/v1/apigateway.proto"

script_dir = os.path.dirname(os.path.abspath(__file__))

print("Downloading protobuf...")

with urllib.request.urlopen(protobuf_url) as req:
    with open(os.path.join(script_dir, '../protobuf/apigateway.proto'), 'w') as file:
        file.write(req.read().decode('utf-8'))

print("Done")

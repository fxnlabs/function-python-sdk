import os.path

from apigateway import test123

script_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(os.path.join(script_dir, ".."))

os.system(f"protoc -I . --python_betterproto_out=function-sdk protobuf/apigateway.proto")

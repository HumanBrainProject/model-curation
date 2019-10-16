# ! /bin/bash

output=$(python -c '
import json, os

hbp_token_file = os.environ["hbp_token_file"]
if os.path.isfile(hbp_token_file):
   data1=json.load(open(hbp_token_file))
   # print("echo the new HBP token is ["+str(data1["access_token"][:20])+"..."+str(data1["access_token"][-20:])+"]")
else:
   print("echo ** /!\ ", hbp_token_file, "not found **")
hbp_storage_token_file = os.environ["hbp_storage_token_file"]
if os.path.isfile(hbp_storage_token_file):
   data2=json.load(open(hbp_storage_token_file))
   # print("echo the new CSCS token is ["+str(data2["auth"]["token"]["access_token"][:20])+"..."+str(data2["auth"]["token"]["access_token"][-20:])+"]")
else:
   print("echo ** /!\ ", hbp_storage_token_file, "not found **")
magic="source env_variables.sh\n"
magic+="export HBP_token="+str(data1["access_token"])+"\n";
magic+="export HBP_STORAGE_TOKEN="+str(data2["auth"]["token"]["access_token"])+"" ; 
print(magic)')

echo "$output"



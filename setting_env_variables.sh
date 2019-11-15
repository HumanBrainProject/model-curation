# ! /bin/bash

output=$(python -c '
import json, os
from env_variables import SPREADSHEETS_ID, hbp_token_file, hbp_storage_token_file, VALIDATION_FRAMEWORK_INFOS
print("echo -----TOKENS ------------------- ")
if os.path.isfile(hbp_token_file): # defined in env_variables
   data1=json.load(open(hbp_token_file))
   print("echo [ok] the new HBP token is "+str(data1["access_token"][:10])+"..."+str(data1["access_token"][-10:]))
else:
   print("echo ** /!\ ", hbp_token_file, "not found **")
if os.path.isfile(hbp_storage_token_file): # defined in env_variables
   data2=json.load(open(hbp_storage_token_file))
   print("echo [ok] the new CSCS token is "+str(data2["auth"]["token"]["access_token"][:10])+"..."+str(data2["auth"]["token"]["access_token"][-10:]))
else:
   print("echo ** /!\ ", hbp_storage_token_file, "not found **")
magic = ""
for key, val in SPREADSHEETS_ID.items():
    magic+="export %s=%s\n" % (key, val);
for key, val in VALIDATION_FRAMEWORK_INFOS.items():
    magic+="export %s=%s\n" % (key, val);
magic+="export HBP_token="+str(data1["access_token"])+"\n";
magic+="export HBP_STORAGE_TOKEN="+str(data2["auth"]["token"]["access_token"])+"\n" ;
magic+="export curation_url=https://docs.google.com/spreadsheets/d/%s/edit" % SPREADSHEETS_ID["MODEL_CURATION_SPREADSHEET"]	+"" ;
print("echo -----SPREADSHEET ------------------- ")
print("echo The spreadsheet for the model curation is avialble at the URL:")
print("echo https://docs.google.com/spreadsheets/d/%s/edit" % SPREADSHEETS_ID["MODEL_CURATION_SPREADSHEET"])
print("echo -----VALIDATION FRAMEWORK INFOS ------------------- ")

print(magic)')
# echo "$output" # for debugging
eval "$output"



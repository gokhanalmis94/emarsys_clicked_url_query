import base64
import configparser
import datetime
import hashlib
import json
import os
import uuid
from typing import Dict, List
import pandas as pd
import requests


def _getWsseHeader(user, secret):
    # Generate a random 16-byte nonce in the 32-character hexadecimal format.
    # uuid4 uses 'os.urandom(16)' which is a much more unpredictable nonce than anything random.randint() would generate
    nonce = uuid.uuid4().hex

    # Get the current timestamp in ISO8601 format.
    timestamp = datetime.datetime.utcnow()
    # timestamp = timestamp.isoformat(' ', 'seconds')
    timestamp = timestamp.strftime(format='%Y-%m-%dT%H:%M:%SZ')

    # Concatenate the following three values in this order: nonce + timestamp + secret
    concat_bytestring = (nonce + timestamp + secret).encode()

    # Calculate the SHA1 hash value (digest) of the concatenated string in hexadecimal format.
    hash_value = hashlib.sha1(concat_bytestring).hexdigest()

    # Apply BASE64 encoding to the result to get the final PasswordDigest value.
    digest = base64.b64encode(hash_value.encode()).decode("utf-8")

    return f'''UsernameToken Username="{user}", PasswordDigest="{digest}", Nonce="{nonce}", Created="{timestamp}"'''


def _get_emarsys_username_secret():
    config = configparser.ConfigParser()
    config.sections()
    config.read(f"{os.getcwd()}/.emarsys_configs")
    config = config['main']
    username = config['username']
    secret = config['secret']

    return username, secret


def _send_mails(email_id_value, link_id_value):
    username, secret = _get_emarsys_username_secret()
    wsse_header = _getWsseHeader(username, secret)

    headers = {
        'x-wsse': f'"{wsse_header}"',
        'content-type': "application/json"
    }

    payload = {}

    response = requests.get(url=f"https://api.emarsys.net/api/v2/email/{email_id_value}/trackedlinks/{link_id_value}",
                             data=json.dumps(payload),
                             headers=headers)
    response_content = json.loads(response.content)
    return response_content



def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)



sample_data = pd.read_csv("Emarsys_LinkId_Lookup.csv")
#print(sample_data.IND)
#print(sample_data.iloc[0:2, :])
for i in range(len(sample_data)):
    email_id = sample_data.columns.get_loc("email_id")
    email_id_value = sample_data.iat[i, email_id]
    link_id = sample_data.columns.get_loc("link_id")
    link_id_value = sample_data.iat[i, link_id]
    response = _send_mails(email_id_value, link_id_value)
    #print(type(response["data"]))
    if isinstance(response["data"], dict):
      response_url = response["data"]["url"]
      url = sample_data.columns.get_loc("URL")
      sample_data.iat[i, url] = response_url
#print(sample_data)
sample_data.to_csv(r'exported_urls.csv', index = False)
print("Hello World")

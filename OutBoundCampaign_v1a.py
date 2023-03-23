import pandas as pd
import requests
import json
import sys
from datetime import datetime, timezone

webextoken = "YTEwZGI5NjItOGRhNy00YmFlLWEwNDQtMDI4ZGZkYzY1ZWU1MzcwM2NhNzctYWEz_P0A1_f48b1db4-07cb-4868-828d-eba6ea7d9c37"
url = "https://api.wxcc-us1.cisco.com/v1/tasks"
sourcefile = "CSV_campaign.csv"
workingfile = "CSV_campaign_results.csv"

payload = {
    "entryPointId": "",
    "destination": "",
    "attributes": {
        "CallReason": "",
        "CallType": "",
        "Name": "",
        "Email": ""
    },
    "outboundType": "",
    "mediaType": "telephony",
    "callback": {
        "callbackOrigin": "web",
        "callbackType": "immediate"
    }
}
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": ""
}

payload['entryPointId'] = "bdb00760-6c5a-46e4-962b-4de859d5f835"
payload['outboundType'] = "CALLBACK"
headers['Authorization'] = "Bearer " + webextoken

def start():
    menuresponse = input(
        "Welcome to the Outbound loader script, please enter one of the next options \n1.- Load campaign.csv\n2.- Check status of tasks\n9.- Exit \n")
    if menuresponse == '1':
        df = pd.read_csv(sourcefile)
        for index, row in df.iterrows():
            payload['destination'] = str(row[0])
            payload['attributes']['CallReason'] = row[1]
            payload['attributes']['CallType'] = row[2]
            payload['attributes']['Name'] = row[3]
            payload['attributes']['Email'] = row[4]
            response = requests.request("POST", url, json=payload, headers=headers)
            y = json.loads(response.text)
            print(response.text)
            # now_utc = datetime.now(timezone.utc)
            now_utc = datetime.now(timezone.utc).timestamp() * 1000
            df.loc[index, 'TaskID'] = y['data']['id']
            df.loc[index, 'UTCCreated'] = str(int(now_utc))
            print(index, row['tel'])
            print(payload)
        df.to_csv(workingfile, index=False)
    if menuresponse == '2':
        df = pd.read_csv(workingfile)
        for index, row in df.iterrows():
            # print(df.loc[index, 'TaskID'])
            # print(df.loc[index, 'UTCCreated'])
            url2 = url + "?from=" + str(df.loc[index, 'UTCCreated'] - 1000) + "&to=" + str(
                df.loc[index, 'UTCCreated'] + 1000) + "&channelTypes=telephony"
            response2 = requests.request("GET", url2, headers=headers)
            y = json.loads(response2.text)
            for index2 in y['data']:
                if index2['id'] == df.loc[index, 'TaskID']:
                    print("Task: " + str(index2['id']))
                    try:
                        df.loc[index, 'Status'] = index2['attributes']['status']
                        print("Status: " + index2['attributes']['status'])
                    except:
                        print("")
                    try:
                        df.loc[index, 'Owner'] = index2['attributes']['owner']['name']
                        print("Owner: " + index2['attributes']['owner']['name'])
                    except:
                        print("")
                    try:
                        df.loc[index, 'Queue'] = index2['attributes']['queue']['name']
                        print("Queue: " + index2['attributes']['queue']['name'])
                    except:
                        print("")
                    try:
                        df.loc[index, 'Origin'] = index2['attributes']['origin']
                    except:
                        print("")
                    try:
                        UTCTime = int(index2['attributes']['lastUpdatedTime']) / 1000
                        dt = datetime.fromtimestamp(UTCTime)
                        df.loc[index, 'Lastupdate'] = dt.strftime("%d-%m-%Y, %H:%M:%S")
                    except:
                        print("Failed Date")
                    print("\n")
            #
        df.to_csv(workingfile, index=False)
    if menuresponse == '9':
        print("Good bye")
        sys.exit()
    else:
        start()


start()

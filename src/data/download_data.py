# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 23:04:06 2020

@author: Aidan Montare (aam141@case.edu)
"""

import os
import json
import requests
from datetime import datetime, timezone

GROUPME_BASE_URL = "https://api.groupme.com/v3"

def read_secrets():
    """Reads the `secrets.json` file."""
    try:
        # We store our various secrets in an aptly named file
        with open('secrets.json', 'r') as data_file:
            return json.load(data_file)
    except FileNotFoundError:
        raise Exception("You must either provide an access token"
                        " on the commnad line or in the file"
                        " `secrets.json`")

def getAllGroupsOfUser():
    """Get all the groups of the user, and return
    the json"""
        
    page = 1 # page of the groups list we are looking at
    cache = []
    
    while True:      
        request = requests.get(GROUPME_BASE_URL + "/groups",
                               params={'token': groupme_token,
                                       "omit": "memberships",
                                       "page": page})
        
        response = request.json()["response"]
        
        if request.status_code != 200:
            print("API fail with status code", request.status_code)
            break
        
        if not response:
            # we reached the last page
            break
        
        for group in response:
            cache.append(group)
                    
        page += 1
    
    return cache

def identifyGroups(groups):
    """
    Print the names and IDs of all the users groups
    """
    
    for group in groups:
        print(group['name'], group['id'])
        if group['id'] != group['group_id']:
            raise Exception("The id and group_id fields are not"
                            " the same")

def showGroup(group_id):
    """
    Load the information about a given group
    """
    
    request = requests.get(GROUPME_BASE_URL + "/groups/" + target_group_id,
                               params={'token': groupme_token})
        
    response = request.json()["response"]
    
    return response

def postMessage():
    # post a message
    
    with open('message.json', 'r') as data_file:
        message = json.load(data_file)
    
    r = requests.post(GROUPME_BASE_URL + "/groups/" + target_group_id + "/messages",
                      data=json.dumps(message),
                      headers={"Content-Type": "application/json"},
                      params={'token': groupme_token})
    
    return r.json()["response"]

def printMessages():
    # messages are returned newest first
    
    print("created_at", "id", "text")
    for m in messages:
        print(m["created_at"], m["id"], m["text"])

def getMessagesInGroup():
    """
    Get all the messages in a group
    """
    all_messages = [] # the list we will collect messages in
    
    r = requests.get(GROUPME_BASE_URL + "/groups/" + target_group_id + "/messages",
                      params={'token': groupme_token})
    
    response = r.json()["response"]
    
    total_messages = response["count"]
    print("Total messages to be downloaded:", total_messages)
    
    messages = response["messages"]
    
    all_messages.extend(messages)
    
    last_id = messages[len(messages) - 1]["id"]
    
    print("Downloading.", end="")

    while True:
        r = requests.get(GROUPME_BASE_URL + "/groups/" + target_group_id + "/messages",
                      params={'token': groupme_token,
                              "before_id": last_id})
        
        if r.status_code == 304:
            # no more messages
            break
    
        response = r.json()["response"]
        messages = response["messages"]
        
        if not messages:
            break
        
        all_messages.extend(messages)
        
        last_id = messages[len(messages) - 1]["id"]
        print(".", end="")
        
    if len(all_messages) != total_messages:
        raise Exception("Not all messages were successfully"
                        " downloaded.")
        
    print(" Done.")
    
    return all_messages

secrets = read_secrets()

groupme_token = secrets["groupme_token"]
target_group_id = secrets["target_group_id"]

now = datetime.now(timezone.utc)

group_info = showGroup(target_group_id)

with open("./data/raw/group_info.json", 'w') as f:
    json.dump(group_info, f)

messages = getMessagesInGroup()

with open("./data/raw/messages.json", 'w') as f:
    json.dump(messages, f)

metadata = {"downloaded_at": now.isoformat()}

with open("./data/raw/metadata.json", 'w') as f:
    json.dump(metadata, f)

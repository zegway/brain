import urllib.request
import sys
from apistar import App, Route, exceptions, http
import json, time


fields = {"host":"172.31.5.175", "port":80, "fpuser":"/etc/passwd" ,"fpgroup":"/etc/group"}
userf = ("name", "uid", "gid", "comment", "home", "shell")
 
groupf = ("name", "gid", "members")

def user(uid: int) -> list:
    try:
        fopen = open(fields["fpuser"], "r")
    except:
        b = exceptions.NotFound()
        b.default_detail = "Bad user file path"
        raise b
    for line in fopen.read().splitlines():
        f = line.split(":")
        if(int(f[2]) == uid):
            f.pop(1) ##removes password field
            return [dict(zip(userf, f))]        
    raise exceptions.NotFound() ##Returns with HTTP Status 404
    
def group(gid: int) -> list:
    try:
        fopen = open(fields["fpgroup"], "r")
    except:
        b = exceptions.NotFound()
        b.default_detail = "Bad group file path"
        raise b
    for line in fopen.read().splitlines():
        f = line.split(":")
        if(int(f[2]) == gid):
            f[-1] = f[-1].split(",")#Only necessary upon pattern match
            f.pop(1) #removes password field
            return [dict(zip(groupf, f))]        
    raise exceptions.NotFound() ##Returns with HTTP Status 404


def glist(mname: str=None) -> list: ##optional param to check for a member
    try:
        fopen = open(fields["fpgroup"], "r")
    except:
        b = exceptions.NotFound()
        b.default_detail = "Bad group file path"
        raise b
    retlist = []    
    for line in fopen.read().splitlines():
        f = line.split(":")
        f[-1] = f[-1].split(",")
        if(mname and not mname in f[-1]): continue
        f.pop(1)
        retlist.append(dict(zip(groupf, f)))
    return retlist

def ulist() -> list:
    try:
        fopen = open(fields["fpuser"], "r")
    except:
        b = exceptions.NotFound()
        b.default_detail = "Bad user file path"
        raise b
    retlist = []    
    for line in fopen.read().splitlines():
        f = line.split(":")
        f.pop(1) #removes password field
        retlist.append(dict(zip(userf, f)))
    return retlist



def uquery(params: http.QueryParams) -> list:
    try:
        fopen = open(fields["fpuser"], "r")
    except:
        b = exceptions.NotFound()
        b.default_detail = "Bad user file path"
        raise b
    retlist = [] 
    if(not params._list):
        raise exceptions.BadRequest() ##Empty
    for line in fopen.read().splitlines():
        f = line.split(":")
        f.pop(1)
        for i, ufield in enumerate(f):
            if(params.get(userf[i]) and params.get(userf[i]) != ufield): break
            if(i == len(f)- 1):
                retlist.append(dict(zip(userf, f)))
    return retlist
            
def gquery(params: http.QueryParams)-> list:
    try:
        fopen = open(fields["fpgroup"], "r")
    except:
        b = exceptions.NotFound()
        b.default_detail = "Bad group file path"
        raise b
    retlist = []
    if(not params._list):
        raise exceptions.BadRequest() ##Empty
    for line in fopen.read().splitlines():
        f = line.split(":")
        f.pop(1)
        for i, gfield in enumerate(f):
            if(i == len(f) -1): #last element is always member check
                f[-1] = f[-1].split(",")
                if(params._dict.get("member")):
                    qmems = params.get_list("member") #get list of members
                    if(len(qmems) > len(f[-1])): break
                    if(len(set(qmems) & set(f[-1])) != len(qmems)): break
                retlist.append(dict(zip(groupf, f)))
            if(params.get(groupf[i]) and params.get(groupf[i]) != gfield): break
    return retlist



def ugroups(uid: int) -> list:
    return glist(user(uid)[0]["name"]) #all errors propagate from functions 
    


def welcome() -> str:
    return "Welcome to the UNIX User API, consult your manual to get started."
 

routes = [
    Route('/', method='GET', handler=welcome),
    Route('/users/{uid}', method='GET', handler=user),
    Route('/users/{uid}/groups', method='GET', handler=ugroups),
    Route('/groups/{gid}', method='GET', handler=group),
    Route('/groups/query', method='GET', handler=gquery),
    Route('/users/query', method='GET', handler=uquery),
    Route('/users', method='GET', handler=ulist),
    Route('/groups', method='GET', handler=glist),
]

app = App(routes=routes)



if __name__ == '__main__':
    imap = ["host", "port", 'fpuser', 'fpgroup'] ##index map for dict
    if(len(sys.argv) == 1):
        print(f"No arguments supplied, using defaults: {fields}")
    for i, arg in enumerate(sys.argv[1:]):
        try:
            fields[imap[i]] = arg
        except:
            raise Exception(f"{arg} is not a valid {fields[imap[i]]} argument.")

    
    app.serve(fields["host"], fields["port"], debug=True)
    




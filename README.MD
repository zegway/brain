This is passwd as a service, a potentially masochistic (i.e. don't leave this running on the open web, it's an LFD afterall) API which serves realtime information on users and groups. 

The defaults are presented by the program when executed, to run with non-default settings you must include all parameters, e.g.:

python brain.py 127.0.0.1 80 /etc/passwd /etc/group

Remember to use absolute file paths.

With the exception for entering the above line arguments, which gives any argument errors through the stdout, exception messages will be presented through the API, including incorrect file paths or malformed files. 


"""
An `Admin` runs many `Topics` where it provides resources and conducts `Sessions`.
There are some `Users` registered with each topic.
For each `Session` `users` are required to submit required files.
The `Agents` can help to `Evaluate` the sessions by looking at required files.

"""

class Agent: # an Interactive Entity
    def __init__(self, 
            uid,    # a unique identifier - as string usually
            name,   # a friendly user-name - as string usually (may not be unique)
            access, # the access token string
            ):
        self.uid, self.name = uid, name
        self.set_access(access)
    
    def set_access(self, access):
        self.access = set(str(access).split())
        assert self.access.issubset(USER_ACCESS_DEF.keys()), f'[!] Access Token [{self.access}] is Invalid! Must be a subset of {USER_ACCESS_DEF}'

class User(Agent):
    # clients, students ...
    ...

class Helper:
    # Assistants
    ...

class Admin:
    # main admin only one
    ...



class Topic:
    # a course, subject
    # contains many 'sessions'
    ...


class Session:
    # a session, lab, class - duration based
    # 'users' are required to login and submit required files within the fixed time interval
    # has a maximum marks and users are evaluated by assistants
    ...

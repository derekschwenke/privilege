from collections import defaultdict
import sys
import re

"""
This Privilege reporting program scans 3 CSV input files and generates a report. 
Permissions are strings granting users privilege to perform a specific task on a resource, depending on their roles. 
Permissions are additive and positive. 
Future work will define the permission strings and group strings. 

Output

python 2.7  

Usage:
    python Privilege 
    
Input:
Three input files are required in CSV format in the working directory: users.txt, roles.txt and, permissions.txt.

1. users.txt:

100, Mel, Martin
200, Frank, Fisher
300, Sally, Smith

2. roles.txt:

ops, 300
user, 100, 200, 300
admin, 100

3. permissions.txt:

user, read
ops, read, write
admin, read, write, execute

Output:
A report of 6 tables.
"""


class User:
    """ Users"""

    def __init__(self, id, first, last):
        self.id = id
        self.first = first
        self.last = last
        self.roles = set()
        self.role_permissions = set()

    def __str__(self):
        return str(self.id) + " " + self.first + " " + self.last

    def get_key(user):  # for sorting
        return user.id


class Privileges:
    """ Privileges scans input files """

    def readCSV(self, file):
        with open(file, 'r') as f:
            lines = f.read().splitlines()
            return [[ field.strip() for field in line.split(',') ] for line in lines ]

    def writeCSV(self, file, lines):
        with open(file, 'w') as f:
            f.write("\n".join([", ".join(line) for line in lines]))

    def read(self):
        self.users_file = self.readCSV("users.txt")
        self.permissions_file = self.readCSV("permissions.txt")
        self.roles_file = self.readCSV("roles.txt")

    def load(self):
        for v in self.users_file:  # [100, "Mel", "Marvin" ],
            if self.userByID.has_key(v[0]):
                print "Error: users file contains duplicate user id ", v[0]
            self.userByID[v[0]] = User(v[0], v[1], v[2])

        for p in self.permissions_file:  # ["user", "read"]
            role = p.pop(0)
            if self.permissionsForRole.has_key(role):
                print "Error: roles file contains duplicate: ", role
            self.allPermissions.update(p)
            self.permissionsForRole[role].update(p)

        for v in self.roles_file:  # ["ops", 300]
            role = v.pop(0)
            for uid in v:
                if not self.userByID.has_key(uid):
                    print "Error: roles file contains new user ", uid
                    self.userByID[uid] = User(uid, "first_" + uid, "last_" + uid)

                self.usersHaveRole[role].add(uid)  # add user to table of roles
                self.userByID[uid].roles.add(role)  # add role to table of users

        for user in self.userByID.values():
            user.role_permissions = set()
            for role in user.roles:
                if self.permissionsForRole.has_key(role):
                    user.role_permissions.update(self.permissionsForRole[role])
                else:
                    print "Error: role '", role, "' missing from permission.txt file for user ", user

    def report(self):

        print "====== User Permissions"
        for u in sorted(self.userByID.values(), key=User.get_key):
            print "{:28} : {}".format(u, " ".join(sorted(u.role_permissions)))
        print "====== Permission Users"
        for p in sorted(self.allPermissions):
            print "{:16} : {}".format(p, " ".join(sorted(
                [str(u.id) for u in self.userByID.values() if p in (u.role_permissions)])))
        print "====== User Roles"
        for u in sorted(self.userByID.values(), key=User.get_key):
            print "{:28} : {}".format(u, " ".join(sorted(u.roles)))
        print "====== Role Users"
        for r in sorted(self.usersHaveRole.keys()):
            print "{:16} : {}".format(r, " ".join(sorted(self.usersHaveRole[r])))
        print "====== Role Permissions"
        for r in sorted(self.permissionsForRole.keys()):
            print "{:16} : {}".format(r, " ".join(sorted(self.permissionsForRole[r])))
        print "====== Permission Roles"
        for p in sorted(self.allPermissions):
            print "{:16} : {}".format(p, " ".join(sorted(
                [r for r in self.permissionsForRole.keys() if p in self.permissionsForRole[r]])))

        print "\n============== User reports:"
        for u in sorted(self.userByID.values(), key=User.get_key):
            print "{:28} : {}".format(u, " ".join(sorted(u.role_permissions)))
            for p in sorted(u.role_permissions):
                print "    {:16} : {}".format(p, " ".join(sorted(  [r for r in u.roles if p in self.permissionsForRole[r]] )))

    def scan(self):
        line = ""
        while line != "end" or line != "quit":
            line = raw_input('Command: ')
            if not line:
                break
            words = line.split(" ")
            if words[0] == "help":
                print "quit?"

    def __init__(self):
        self.allPermissions = set()
        self.permissionsForRole = defaultdict(set)
        self.usersHaveRole = defaultdict(set)
        self.userByID = dict()

        self.read()
        self.load()
        self.report()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # opts = sys.argv[1]
        access = Privileges()
        # access.scan()
    else:
        print "Usage: Privilege "

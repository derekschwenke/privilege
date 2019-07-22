from collections import defaultdict
import sys
import sqlite3
import json

"""
This Privilege reporting program scans 3 input files and generates a report. It allows the data to be edited and saved.
Permissions are strings granting users privilege to perform a specific task on a resource, depending on their roles. 
Permissions are additive and positive. 
Future work will define the permission strings and group strings. 

python 2.7  

Usage:
    python Privilege [-interactive]
    
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
A report of 6 tables, and user focused tables.
Data error checks (duplicate, missing values).

See readme at 
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
    """ Privileges reporting """
    def clear(self):
        self.allPermissions = set()
        self.permissionsForRole = defaultdict(set)
        self.usersHaveRole = defaultdict(set)
        self.userByID = dict()

    def readCSV(self, file):
        with open(file, 'r') as f:
            lines = f.read().splitlines()
            return [[field.strip() for field in line.split(',')] for line in lines]

    def writeCSV(self, file, lines):
        with open(file, 'w') as f:
            f.write("\n".join([", ".join(line) for line in lines]))

    def read(self):
        self.clear()
        self.users_file = self.readCSV("users.txt")
        self.permissions_file = self.readCSV("permissions.txt")
        self.roles_file = self.readCSV("roles.txt")
        self.load()

    def writejson(self):
        d = {}
        d['users'] = [ { "acct_name" : user.id, "first_name" : user.first, "last_name" : user.last} for user in sorted(self.userByID.values(), key=User.get_key) ]
        d['roles'] = [ { "role_name" : role , "users" : list(users)} for role, users in self.usersHaveRole.iteritems() ]
        d['permissions'] = [ { "role_name" : role , "permissions" : list(permissions)} for role, permissions in self.permissionsForRole.iteritems() ]
        with open('privilege.json', 'w') as f:
            json.dump(d, f, indent=2, sort_keys=True)

    def writeurp(self):
        uix = {}
        pix = {}
        d = []
        j = 0
        for i, user in enumerate(self.userByID.values(), start=1):
            uix[user.id] = i
            m = { "model" : "priv.user", "pk" : i }
            m["fields"] = { "acct_name" : user.id, "first_name" : user.first, "last_name" : user.last }
            d.append(m)
        for i, p in enumerate(self.allPermissions, start=1):
            pix[p] = i
            m = { "model" : "priv.permission", "pk" : i }
            m["fields"] = {"permission_name" : p}
            d.append(m)
        i = 0
        for role, permissions in self.permissionsForRole.iteritems():
            j = j + 1
            ui = [ uix[uid] for uid in self.usersHaveRole[role] ]
            pi = [ pix[permission] for permission in permissions ]
            m = { "model" : "priv.role", "pk" : j }
            m["fields"] = { "role_name" : role, "users" : ui, "permissions" : pi }
            d.append(m)
        with open('urp.json', 'w') as f:
            json.dump(d, f, indent=2 )


    def readjson(self, filename = None):
        if filename == None:
            filename = "privilege.json"
            self.clear()
        with open(filename, "r") as f:
            d = json.load(f)
            self.users_file = [[u["acct_name"],u["first_name"],u["last_name"]] for u in d["users"]]
            self.roles_file = [ [r["role_name"]] + r["users"] for r in d["roles"]]
            self.permissions_file = [ [r["role_name"]] + r["permissions"] for r in d["permissions"]]
        self.load()

    def writesql(self):
        conn = sqlite3.connect('sqlite3.db')
        conn.execute("DROP TABLE IF EXISTS priv_user")
        conn.execute("DROP TABLE IF EXISTS priv_role")
        conn.execute("DROP TABLE IF EXISTS priv_permission")
        conn.execute('''CREATE TABLE IF NOT EXISTS priv_user
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 acct_name        CHAR(24) NOT NULL,
                 first_name       CHAR(24) NOT NULL,
                 last_name        CHAR(24) NOT NULL);''')

        conn.execute('''CREATE TABLE IF NOT EXISTS priv_role
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 role_name        CHAR(80) NOT NULL);''')

        conn.execute('''CREATE TABLE IF NOT EXISTS priv_permission
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 permission_name        CHAR(80) NOT NULL);''')

        conn.execute('''CREATE TABLE IF NOT EXISTS priv_role_users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 role_id       INTEGER NOT NULL,
                 user_id       INTEGER NOT NULL);''')

        conn.execute('''CREATE TABLE IF NOT EXISTS priv_role_permissions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 role_id       INTEGER NOT NULL,
                 permission_id       INTEGER NOT NULL);''')
        #  s_ sorted lists required since SQL uses index and python uses Strings
        s_roles = sorted(self.usersHaveRole.keys())
        s_perms = sorted(self.allPermissions)
        s_uid = sorted(self.userByID.values(), key=User.get_key)
        for user in sorted(self.userByID.values(), key=User.get_key):
            conn.execute("INSERT INTO priv_user (acct_name, first_name, last_name) VALUES ('{}', '{}', '{}')".format(user.id,user.first,user.last))
        for role in sorted(self.usersHaveRole):
            conn.execute("INSERT INTO priv_role (role_name) VALUES ('{}')".format(role))
        for priv in sorted(self.allPermissions):
            conn.execute("INSERT INTO priv_permission (permission_name) VALUES ('{}')".format(priv))

        for rx, role in enumerate(s_roles):
            for ux in self.usersHaveRole[role]:
                conn.execute("INSERT INTO priv_role_users (role_id, user_id) VALUES ('{}', '{}')".format(rx + 1,ux))
        for rx, role in enumerate(s_roles):
            for perm in self.permissionsForRole[role]:
                px = 1 + s_perms.index(perm)
                conn.execute("INSERT INTO priv_role_permissions (role_id, permission_id) VALUES ('{}', '{}')".format(rx + 1,px))

        conn.commit()
        conn.close()

    def readsql(self):
        r_has_u = defaultdict(set)  # Role has Users
        r_has_p = defaultdict(set)  # Role has Permissions
        self.clear()
        conn = sqlite3.connect('sqlite3.db')
        self.users_file = [u for u in conn.execute("SELECT acct_name, first_name, last_name from priv_user") ]
       #user_str = ["None0"] + [u[0] for u in conn.execute("SELECT acct_name from priv_user")]
        role_str = ["None0"] + [r[0] for r in conn.execute("SELECT role_name from priv_role")]
        perm_str = ["None0"] + [p[0] for p in conn.execute("SELECT permission_name from priv_permission")]
        for res in conn.execute("SELECT role_id, user_id from priv_role_users"):
            rx,u = res[:2]
            r = role_str[rx]
            r_has_u[r].add(str(u))
        for res in conn.execute("SELECT role_id, permission_id from priv_role_permissions"):
            r,p = res[:2]
            r_has_p[role_str[r]].add(perm_str[p])
        #self.roles_file = [[u] + list(u_has_r[u]) for u in u_has_r ]
        self.roles_file = [[r] + list(r_has_u[r]) for r in r_has_u ]
        self.permissions_file = [[r] + list(r_has_p[r])  for r in r_has_p ]
        conn.close()
        self.load()

    def write(self):
        self.writeCSV("users.out.txt", [[user.id, user.first, user.last] for user in sorted(self.userByID.values(), key=User.get_key)])
        self.writeCSV("roles.out.txt", [[key] + sorted(self.usersHaveRole[key]) for key in sorted(self.usersHaveRole)])
        self.writeCSV("permissions.out.txt", [[key] + sorted(self.permissionsForRole[key]) for key in sorted(self.permissionsForRole)])

    def delUser(self, uid):
        del self.userByID[uid]
        for role, users in self.usersHaveRole.items():
            users.discard(uid)

    def delRole(self, role):
        del self.permissionsForRole[role]
        del self.usersHaveRole[role]

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
            print "{:28}".format(u)
            for p in sorted(u.role_permissions):
                print "    {:16} : {}".format(p," ".join(sorted([r for r in u.roles if p in self.permissionsForRole[r]])))

    def search(self, query):
        count=0
        for user in sorted(self.userByID.values(), key=User.get_key):
            if query in user.first or query in user.last or query in user.id:
                print "{:28}".format(user)
                count += 1
        if count: print count, "users found."
        else: print "No users found."
        print ""
        for r in sorted(self.permissionsForRole.keys()):
            if query in r:
                print "{:16}".format(r)
        print ""
        for p in sorted(self.allPermissions):
            if query in p:
                print "{:16}".format(p)


    def scan(self):
        while True:
            line = raw_input('Command: ')
            if line == "end" or line == "exit" or line == "quit":
                break
            words = line.split(" ")
            if words[0] == "help":
                print "quit, read, write, report, create, add, delete."
            elif words[0] == "report":
                self.report()
            elif words[0] == "clear":
                 self.clear()
            elif words[0] == "read":
                self.read()
            elif words[0] == "readsql":
                self.readsql()
            elif words[0] == "writesql":
                self.writesql()
            elif words[0] == "mergejson":
                self.readjson(words[1])
            elif words[0] == "readjson":
                self.readjson()
            elif words[0] == "writejson":
                self.writejson()
            elif words[0] == "writeurp":
                 self.writeurp()
            elif words[0] == "write":
                self.write()
            elif line.startswith("create user"):
                User(words[2], words[3], words[4])
            elif line.startswith("delete user"):
                self.delUser(words[2])
            elif line.startswith("create role"):
                self.permissionsForRole[words[2]] = line[3:]
            elif line.startswith("delete role"):
                self.delRole(words[2])
            elif line.startswith("add role"):
                self.usersHaveRole[words[2]] = self.usersHaveRole[words[2]] + set(line[3:])
            elif line.startswith("delete role"):
                self.usersHaveRole[words[2]] = self.usersHaveRole[words[2]].difference(set(line[3:]))
            elif line.startswith("create permission"):
                self.allPermissions.add(set(line[3:]))
            elif line.startswith("delete permission"):
                self.allPermissions.discard((words[2]))
            elif line.startswith("search"):
                self.search(words[1])
            else:
                print "No command:", line

    def __init__(self):
        self.read()
        self.report()
        self.write()


if __name__ == "__main__":
    privileges = Privileges()
    if len(sys.argv) > 1:
        privileges.scan()

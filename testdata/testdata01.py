#! /usr/bin/python
#
# generate testdata01.json, a sample set of data
#
import random
import json

class MockUsers(object):
    "Generate a list of mock users"

    def __init__(self,n=0):
        'create mock users. add n initial users'
        self._init_fname_list()
        self._init_lname_list()
        self.users = []
        self.acctnames = set()

        for i in range(n):
            self.add_user()
        
    def add_user(self):
        'add a user with a random first and last name'

        fname = random.choice(self.fname_list)
        lname = random.choice(self.lname_list)
        acctname = self.mkacct(fname,lname)
        self.users.append(
            {
                'acct_name': acctname,
                'first_name': fname,
                'last_name': lname
            })

    def mkacct(self,fname,lname):
        '''\
        create acctname on template
        'u' + first 5 letters of lname + first letter of fname
        + a digit to uniqify if necessary
        '''
        acctroot = 'u' + lname[0:5].lower() + fname[0].lower()
        acct_candidate = acctroot
        index = 1
        while acct_candidate in self.acctnames:
            index = index + 1
            acct_candidate = "%s%d" % (acctroot,index)

        self.acctnames.add(acct_candidate)
        return acct_candidate
        
        
    def _init_fname_list(self):
        '''\
        initialize fname_list with 50 common boy names
        and 50 common girl names
        '''

        boynames = ','.join([
            'Liam,Noah,William,James,Logan,Benjamin,Mason,Elijah,Oliver,Jacob',
            'Lucas,Michael,Alexander,Ethan,Daniel,Matthew,Aiden,Henry,Joseph',
            'Jackson,Samuel,Sebastian,David,Carter,Wyatt,Jayden,John,Owen',
            'Dylan,Luke,Gabriel,Anthony,Isaac,Grayson,Jack,Julian,Levi',
            'Christopher,Joshua,Andrew,Lincoln,Mateo,Ryan,Jaxon,Nathan',
            'Aaron,Isaiah,Thomas,Charles,Caleb'
            ])
        girlnames = ','.join([
            'Emma,Olivia,Ava,Isabella,Sophia,Mia,Charlotte,Amelia,Evelyn',
            'Abigail,Harper,Emily,Elizabeth,Avery,Sofia,Ella,Madison,Scarlett',
            'Victoria,Aria,Grace,Chloe,Camila,Penelope,Riley,Layla,Lillian',
            'Nora,Zoey,Mila,Aubrey,Hannah,Lily,Addison,Eleanor,Natalie,Luna',
            'Savannah,Brooklyn,Leah,Zoe,Stella,Hazel,Ellie,Paisley,Audrey',
            'Skylar,Violet,Claire,Bella'
            ])

        self.fname_list = boynames.split(',') + girlnames.split(',')

    def _init_lname_list(self):
        '''\
        initialize lname_list with 200 common surnames
        '''
        surnames = ','.join([
            'Smith,Johnson,Williams,Brown,Jones,Garcia,Miller,Davis,Rodriguez',
            'Martinez,Hernandez,Lopez,Gonzalez,Wilson,Anderson,Thomas,Taylor',
            'Moore,Jackson,Martin,Lee,Perez,Thompson,White,Harris,Sanchez',
            'Clark,Ramirez,Lewis,Robinson,Walker,Young,Allen,King,Wright',
            'Scott,Torres,Nguyen,Hill,Flores,Green,Adams,Nelson,Baker,Hall',
            'Rivera,Campbell,Mitchell,Carter,Roberts,Gomez,Phillips,Evans',
            'Turner,Diaz,Parker,Cruz,Edwards,Collins,Reyes,Stewart,Morris',
            'Morales,Murphy,Cook,Rogers,Gutierrez,Ortiz,Morgan,Cooper',
            'Peterson,Bailey,Reed,Kelly,Howard,Ramos,Kim,Cox,Ward,Richardson',
            'Watson,Brooks,Chavez,Wood,James,Bennett,Gray,Mendoza,Ruiz,Hughes',
            'Price,Alvarez,Castillo,Sanders,Patel,Myers,Long,Ross,Foster',
            'Jimenez,Powell,Jenkins,Perry,Russell,Sullivan,Bell,Coleman',
            'Butler,Henderson,Barnes,Gonzales,Fisher,Vasquez,Simmons,Romero',
            'Jordan,Patterson,Alexander,Hamilton,Graham,Reynolds,Griffin',
            'Wallace,Moreno,West,Cole,Hayes,Bryant,Herrera,Gibson,Ellis,Tran',
            'Medina,Aguilar,Stevens,Murray,Ford,Castro,Marshall,Owens',
            'Harrison,Fernandez,Mcdonald,Woods,Washington,Kennedy,Wells',
            'Vargas,Henry,Chen,Freeman,Webb,Tucker,Guzman,Burns,Crawford',
            'Olson,Simpson,Porter,Hunter,Gordon,Mendez,Silva,Shaw,Snyder',
            'Mason,Dixon,Munoz,Hunt,Hicks,Holmes,Palmer,Wagner,Black',
            'Robertson,Boyd,Rose,Stone,Salazar,Fox,Warren,Mills,Meyer,Rice',
            'Schmidt,Garza,Daniels,Ferguson,Nichols,Stephens,Soto,Weaver,Ryan',
            'Gardner,Payne,Grant,Dunn'
            ])
        self.lname_list = surnames.split(',')

class MockRole(object):
    '''superclass for a mock role
    a mock role has role_user list and role_permission list
    '''
    def __init__(self,rolename):
        self.rolename = rolename
        self.users = []
        self.permissions = []

    def get_role_users(self):
        role_users = {
            'role_name': self.rolename,
            'users': self.users
        }
        return role_users

    def get_role_permissions(self):
        role_permissions = {
            'role_name': self.rolename,
            'permissions': self.permissions
        }
        return role_permissions

    def add_permission(self,permission):
        self.permissions.append(permission)

    def add_user(self,user):
        self.users.append( user['acct_name'] )

    def add_acct(self,acct):
        self.users.append( acct )
    
class Ugroup(MockRole):
    'create user specific group'

    def __init__(self, acctname):
        MockRole.__init__(self,"/ugroup/%s" % acctname)
        self.add_acct(acctname)
        self.add_permission("/posix/%s" % acctname)

class Team(MockRole):
    'create a team role'

    def __init__(self,userlist,team_name,subrole=""):
        'create role team_name+subrole with bunch of permissions'
        rolename = team_name + subrole
        MockRole.__init__(self,'/team/%s' % rolename)
        for u in userlist:
            self.add_user( u )
        self.add_permission( '/posix/%s' % team_name )
        self.add_permission( '/win32/%s' % team_name )
        self.add_permission( '/hub/%s' % team_name )
        self.add_permission( '/login/srv_%s' % team_name )
        self.add_permission( '/tkt/read' )
        if rolename != team_name:
            self.add_permission( '/hub/%s' % rolename )


class Inactive(MockRole):
    'create inactive users'

    def __init__(self,userlist):
        MockRole.__init__(self,'INACTIVE')
        for u in userlist:
            self.add_user(u)
        self.add_permission( 'INACTIVE' )

def main():

    NUM_USERS = 250
    INACTIVE_USERS = 20
    NUM_GROUPS = 20
    TEAM_SIZE=(5,15)
    
    mock_users = MockUsers(NUM_USERS)
    users = mock_users.users

    roles = []
    permissions = []

    for u in users:
        user_group = Ugroup(u['acct_name'])
        roles.append(user_group.get_role_users())
        permissions.append(user_group.get_role_permissions())

    for team_idx in range(NUM_GROUPS):
        team_name = 'team%03d' % team_idx
        teamsize = random.randint( TEAM_SIZE[0], TEAM_SIZE[1] )
        new_team = Team(random.sample(users, teamsize),team_name)
        new_team_poc = Team(random.sample(users, 1), team_name, "_poc")
        new_team_adm = Team(random.sample(users, 1), team_name, "_adm")
        roles.append(new_team.get_role_users())
        permissions.append(new_team.get_role_permissions())
        roles.append(new_team_poc.get_role_users())
        permissions.append(new_team_poc.get_role_permissions())
        roles.append(new_team_adm.get_role_users())
        permissions.append(new_team_adm.get_role_permissions())

    inactive_users = Inactive(random.sample(users, INACTIVE_USERS))
    roles.append(inactive_users.get_role_users())
    permissions.append(inactive_users.get_role_permissions())
    
    json_data = {
        'users': users,
        'roles': roles,
        'permissions': permissions
    }

    json_str = json.dumps(json_data,indent=4)
    with open("testdata01.json",'w') as f:
        f.write(json_str)
        

if __name__ == '__main__':
    main()

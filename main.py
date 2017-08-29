from win32print import EnumPrinters, GetPrinter, OpenPrinter
from ldapconmanager import LdapConManager
from registry import Root
import re
import sys

class UserManager():
    def __init__(self, domain=None, server=None):
        self.regRoot = Root()
        self.ldap_connection = None
        if domain and server:
            try:
                self.ldap_connection = LdapConManager(domain, server)
            except Exception as e:
                print(e)


    def getUsersFromReg(self):
        for sid in self.regRoot.users().keys:
            if sid != '.DEFAULT' and not re.match('^[s|S].*_Classes$', sid):
                user = self.getUserFromLdap(sid)
                yield {sid: {'default_printer': self.getDefaultPrinter(sid),
                             'uid': user['uid'] if user else None,
                             'registry': True }}

    def getUsersFromRegDict(self):
        result = {}
        for user in self.getUsersFromReg():
            result.update(user)
        return result


    def getUserFromLdap(self, sid):
        try:
            return self.ldap_connection.getUserSidDict(sid=sid)[sid]
        except:
            return None

    
    def getDefaultPrinter(self, sid):
        try:
            return self.regRoot.users(sid + r'/Software/Microsoft/Windows NT/CurrentVersion/Windows').valsDict['Device'].split(',')[0]
        except KeyError:
            return None
            

    def setDefaultPrinter(self, sid, printer):
        try:
            self.regRoot.users(sid + r'/Software/Microsoft/Windows NT/CurrentVersion/Windows').setVal('Device', printer)
            self.regRoot.users(sid + r'/Software/Microsoft/Windows NT/CurrentVersion/Windows').setVal('UserSelectedDefault', 1, 'dw')            
        except:
            return None
        else:
            return self.getDefaultPrinter(sid)


    def getPrinterSpool(self, sid, printer):
        try:
            return self.regRoot.users(sid + r'/Software/Microsoft/Windows NT/CurrentVersion/Devices').valsDict[printer]
        except KeyError:
            return None


if __name__ == '__main__':
    domain = 'ou=Users,dc=domain,dc=net'
    server = '192.168.0.1'
    um = UserManager(domain, server)

    for i in um.getUsersFromReg():
        print(i)
        

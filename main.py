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
                pass


    def getUsersFromReg(self):
        for sid in self.regRoot.users().keys:
            if sid != '.default' and not re.match('^[s|S].*_Classes$', sid):
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
        except KeyError:
            return None
    
    
    def getDefaultPrinter(self, sid):
        try:
            tmp_vals = {}
            for item in self.regRoot.users(sid + r'/Software/Microsoft/Windows NT/CurrentVersion/Windows').vals:
                tmp_vals.update({item.name: item.val})
            return tmp_vals['Device'].split(',')[0]
        except KeyError:
            return None

    
    # def get_printer_spool(sid, printer):
    #     try:
    #         vals =self.regRoot.users(sid + r'/software/microsoft/windows nt/currentversion/devices').vals
    #         return vals[vals.index(printer)]
    #     except KeyError:
    #         return None


if __name__ == '__main__':
    domain = 'ou=Users,dc=megateks,dc=net'
    server = '10.10.0.1'
    um = UserManager(domain, server)
    for i in um.getUsersFromReg():
        print(i)


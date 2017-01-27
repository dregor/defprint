'''
    Win Registry module
    (_winreg wrapper)
'''
import _winreg as reg

# convenience dicts
vTyp={
    reg.REG_BINARY : 'BIN',
    reg.REG_DWORD : 'DW',
    reg.REG_DWORD_BIG_ENDIAN : 'DWB',
    reg.REG_DWORD_LITTLE_ENDIAN : 'DWL',
    reg.REG_EXPAND_SZ : 'XSZ',
    reg.REG_LINK : 'LNK',
    reg.REG_MULTI_SZ : 'MSZ',
    reg.REG_RESOURCE_LIST : 'RES',
    reg.REG_SZ : 'STR',
    reg.REG_NONE : 'NUL',
    }
rTyp=dict((v, k) for k, v in vTyp.items())

indent='\t'     # the string used for indented output

class Val(object):
    # Registry Value
    def __init__(self, key, name, val, typ):
        self.key, self.name, self.val, self.typ = key, name, val, typ
    @property
    def indented(self):
        return '%s%s' % (indent*(self.key.level+1), self.__str__())
    def __str__(self):
        val=' - bin -' if self.typ==rTyp['BIN']  else self.val
        return '%s : %s' % (self.name, val)

class Key(object):
    # Registry Key
    def __init__(self, parent, name):
        self.parent, self.name = parent, name
        self.level=parent.level+1
        # ! ! ! opens keys in read/write mode ! ! !
        self.wrk=reg.OpenKey(parent.wrk, self.name, 0, reg.KEY_ALL_ACCESS)
        self._keys = self._vals = None
    @property
    def keys(self):
        # returns a dict of subkeys
        if not self._keys:
            self._keys={}
            for i in range(reg.QueryInfoKey(self.wrk)[0]):
                name=reg.EnumKey(self.wrk, i)
                try:
                    self._keys[name]=Key(self, name)
                except WindowsError: pass
        return self._keys
    @property
    def vals(self):
        # returns the list of values
        if not self._vals:
            self._vals=[]
            for i in range(reg.QueryInfoKey(self.wrk)[1]):
                try:
                    self._vals.append(Val(self, *reg.EnumValue(self.wrk, i)))
                except WindowsError: pass
        return self._vals
    @property
    def valsDict(self):
        tmp_vals = {}
        for item in self.vals:
            tmp_vals.update({item.name: item.val})
        return tmp_vals
    def __call__(self, path=None):
        # access to a key        
        key=self
        if path:
            path=path
            for p in path.split('/'):
                key=key.keys[p]
        return key
    def __str__(self):
        return '%s%s/' % (self.parent.__str__(), self.name)
    @property
    def indented(self):
        return '%s%s' % (indent*self.level, self.name)
    def walk(self):
        # walk thru the subkeys tree
        for key in self.keys.values():
            yield key
            for k in key.walk():
                yield k
    def grep(self, text, kv='both', typ=(rTyp['STR'],)):
        # searching keys and/or values for some text
        for k in self.walk():
            if kv in ('keys', 'both') and text in k.name:
                yield k, None
            if kv in ('vals', 'both'):
                for v in k.vals:
                    if (v.typ in typ) and (text in v.val):
                        yield k, v
    def grep2(self, text, kv='both', typ=(rTyp['STR'],)):
        # a grep variant, might be more convinient in some cases
        kb=None
        for k in self.walk():
            if kv in ('keys', 'both') and text in k.name:
                if kv=='both':
                    yield k, False
                    kb=k
                else:
                    yield k
            if kv in ('vals', 'both'):
                for v in k.vals:
                    if (v.typ in typ) and (text in v.val):
                        if kv=='both':
                            if k!=kb:
                                yield k, False
                                kb=k
                            yield v, True
                        else:
                            yield v
    def create(self, path):
        # create a subkey, and the path to it if necessary
        k=self
        for p in path.split('/'):
            if p in k.keys:
                k=k.keys[p]
            else:
                reg.CreateKey(k.wrk, p)
                k=Key(k, p)
        return k
    def setVal(self, name, val, typ='str'):
        # set value
        typ=typ.upper()
        if typ=='DW': typ='DWL'
        typ=rTyp[typ]
        reg.SetValueEx(self.wrk, name, 0, typ, val)

class Hkey(Key):
    # Registry HKey
    def __init__(self, name):
        self.parent=None
        self.level=0
        self.name=name
        self.wrk=reg.ConnectRegistry(None, getattr(reg, name))
        self._keys=None
        self._vals=None
    def __str__(self):
        return '/%s/' % self.name

class Root(Key):
    # Registry Root
    def __init__(self):
        self.hkey={}
        for key in (k for k in dir(reg) if k.startswith('HKEY_')):
            try:
                chk = reg.ConnectRegistry(None, getattr(reg, key))
                inf = reg.QueryInfoKey(chk)
                reg.CloseKey(chk)
            except WindowsError: pass           # some keys may appear in _winreg but can't be reached
            else:
                hk = Hkey(key)
                try:
                    chk=hk.keys
                except WindowsError: pass       # some keys can be accessed but not enumerated
                else:                           # some keys work fine ...
                    name=key[5:].lower()
                    self.hkey[name]=hk          # for iterating
                    setattr(self, name, hk)     # for easy access
    @property
    def keys(self):
        return self.hkey

#example
if __name__=='__main__':
    root=Root()
    try:
        print('\n---- Keys -----\n')
        for k in root.current_user(r'console').keys.values(): print(k)
        print('\n---- Vals -----\n')
        for k in root.current_user(r'console').vals: print(k)
        print('\n---- HERE -----\n')
        try:
            root.current_user('python')
        except KeyError as e:
            root.current_user.create('python')
        finally:
            print(root.current_user('python'))

        print('\n---- NOT HERE -----\n')
        try:
            print(root.current_user('nopython'))
        except KeyError as e:
            print('KEY ERROR ' + str(e))

        print('\n---- Set Vals -----\n')
        root.current_user('python').setVal('TEST', 'TEST')
        root.current_user('python').setVal('TEST2', 3000, 'dw')
        for item in root.current_user('python').vals:
            print(item)

    except UnicodeError: pass

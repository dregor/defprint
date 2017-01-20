import ldap
from getpass import getpass


class LdapConManager():
	PAGE_SIZE = 100

	def __init__(self, domain, server, user='', password=''):
		self.domain = domain
		self.lc = ldap.controls.SimplePagedResultsControl(True, size=self.PAGE_SIZE, cookie='')
		try:
			self.connection = ldap.initialize('ldap://'+server)
			self.connection.bind(user, password)
		except ldap.LDAPError as e:
			if type(e.message) == dict and e.message.has_key('desc'):
				return e.message['desc']
			elif type(e.message) == dict and e.message.has_key('info'):
				return e.message['info']
			else:
				return e

	def get_user_list(self):
		filter=('(&(objectclass=person)(uid=*))')
		attrs=(['uid'])
		for a in self.connection.search_s(self.domain,ldap.SCOPE_SUBTREE, filter, attrs):
			yield(a[1]['uid'][0])

	def get_user_sid(self, uid=None):
		filter_list= ['(objectclass=sambaSamAccount)','(sambaSID=*)']
		if uid is not None:
			filter_list.append('(uid=%s)' % (uid))
		filter = '(&' + ''.join(filter_list) + ')'
		attrs=(['uid','sambaSID'])

		first_pass = True
		while first_pass or self.lc.cookie:
			first_pass = False
			try:
				result = self.connection.search_ext(self.domain,
													ldap.SCOPE_SUBTREE,
													filter,
													attrs,
													serverctrls=[self.lc])
			except Exeption as e:
				print(e)			    

			rtype, rdata, rmsgid, serverctrls = self.connection.result3(result)
			#for item in rdata:
			#	print(item[1])
			# pctrls =  [c for c in serverctrls if c.controlType == ldap.controls.SimplePagedResultsControl.controlType]
			# if not pctrls:
			# 	print >> sys.stderr, 'Warning: Server ignores RFC 2696 control.'
			# 	break
			self.lc.cookie = serverctrls[0].cookie
			print(serverctrls[0].cookie)			
			yield rdata

if __name__=='__main__':
	domain = 'dc=megateks,dc=net'
	server = '172.16.0.111'	
	#user = raw_input("Enter user: ")
	#password = getpass("Enter password: ")
	user = 'ldapadmin'
	password = '35207'
	test = LdapConManager(domain, server, user, password)
	if not isinstance( test, str ):
		for item in test.get_user_sid():
			print('+++++++++++++++++++ PAGE +++++++++++++++++++')
			for item2 in item:
				print(item2[1])
	else:
		print(test)
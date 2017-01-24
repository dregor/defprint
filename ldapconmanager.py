from ldap_paged_search import LdapPagedSearch
from getpass import getpass


class LdapConManager():


	def __init__(self, domain, server, user='', password=''):
		self.domain = domain
		# self.lc = ldap.controls.SimplePagedResultsControl(True, size=self.PAGE_SIZE, cookie='')
		try:
			self.connection = LdapPagedSearch('ldap://' + server, user, password, maxPages=1000, pageSize=500)
		except Exception as e:
			print(e)


	def get_user_list(self):
		filter=('(&(objectclass=person)(uid=*))')
		attrs=(['uid'])
		for user in self.connection.search(self.domain, filter, attrs):
			yield(user)


	def get_user_sid(self, uid=None):
		filter_list= ['(objectclass=sambaSamAccount)','(sambaSID=*)']
		if uid is not None:
			filter_list.append('(uid=%s)' % (uid))
		filter = '(&' + ''.join(filter_list) + ')'
		attrs=(['uid','sambaSID'])
		result = {}
		for dn, sid in self.connection.search(self.domain, filter, attrs):
			result.update( {sid['uid'][0]: {'sid':sid['sambaSID'][0]}} )
		return result


if __name__=='__main__':
	domain = 'ou=Users,dc=megateks,dc=net'
	server = '172.16.0.111'	
	ldap_connection = LdapConManager(domain, server)
	if not isinstance( ldap_connection, str ):
		users = ldap_connection.get_user_sid()
		for item in users:
			print(item)
			print(users[item])
	else:
		print(ldap_connection)
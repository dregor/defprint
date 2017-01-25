from ldap_paged_search import LdapPagedSearch
from getpass import getpass


class LdapConManager():
	def __init__(self, domain, server, user='', password=''):
		self.domain = domain
		self.connection = LdapPagedSearch('ldap://' + server, user, password, maxPages=1000, pageSize=500)


	def getAllUsers(self):
		filter=('(&(objectclass=person)(uid=*))')
		attrs=(['uid'])
		for user in self.connection.search(self.domain, filter, attrs):
			yield(user)


	def getUserSid(self, uid=None, sid=None):
		filter_list= ['(objectclass=sambaSamAccount)']
		if uid:
			filter_list.append('(uid=%s)' % (uid))
		if sid:
			filter_list.append('(sambaSID=%s)' % (sid))
		filter = '(&' + ''.join(filter_list) + ')'
		attrs=(['uid','sambaSID'])
		for dn, data in self.connection.search(self.domain, filter, attrs):
			if sid:
				yield {data['sambaSID'][0]: {'uid':data['uid'][0]}}
			else:
				yield {data['uid'][0]: {'sid':data['sambaSID'][0]}} 

	def getUserSidList(self, uid=None, sid=None):
		result = {}
		for user in self.getUserSid(uid, sid):
			result.update(user)
		return result


if __name__=='__main__':
	domain = 'ou=Users,dc=megateks,dc=net'
	server = '172.16.0.111'	
	ldap_connection = LdapConManager(domain, server)
	if not isinstance( ldap_connection, str ):
		users = ldap_connection.getUserSidList()
		for user in users:
			print(user)
			for item in users[user]:
				print(item + ': ' + users[user][item])
	else:
		print(ldap_connection)
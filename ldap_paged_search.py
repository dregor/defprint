#!/usr/bin/env python
#
# (C) Copyright 2014 Michael Henry aka neoCrimeLabs ( http://neocri.me/ )
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Lesser General Public License
# (LGPL) version 2.1 which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/lgpl-2.1.html
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# Contributors:
#     Michael Henry aka neoCrimeLabs ( http://neocri.me/ )


# Note:  This work is strongly based on the works of others found on various forums
# I took what worked, fixed what didn't, then rewrote as an installable module

import ldap
from   ldap.controls import SimplePagedResultsControl


class LdapPagedSearch( object ):


    def __init__( self, url , username, password, pageSize = 1000, maxPages = 0 ):
        ldap.set_option( ldap.OPT_REFERRALS, 0 )

        self.username               = username
        self.password               = password
        self.pageSize               = pageSize
        self.maxPages               = maxPages
        self.ldap                   = ldap.initialize( url )
        self.ldap.protocol_version  = ldap.VERSION3
        self.pageType               = SimplePagedResultsControl.controlType
        self.responseCodes          = { self.pageType: SimplePagedResultsControl, }
        self.connected              = False
        self.directSearch           = False


    def __enter__( self ):
        if self.connected is False:
            self.ldap.bind_s( self.username, self.password )
            self.connected = True
        return self


    def __exit__( self, type, value, traceback ):
        if self.connected is True:
            self.connected = False
            self.ldap.unbind_s()


    def _getPageCookie( self, serverControls ):
        cookie = None

        for control in serverControls:
            if control.controlType == self.pageType:
                cookie = control.cookie
                break
        return cookie


    def _setPageControl( self, cookie = '' ):
        return SimplePagedResultsControl( True, self.pageSize, cookie = cookie )


    def _handleResults(self, data, callback):
        results = []

        for dn,record in data:
            if dn is not None:
                if callback is not None:
                    callback( dn, record )
                else:
                    results.append( ( dn, record ) )

        return results


    def _doSearch(self, baseDN, searchFilter, attributes, pageControl):

            # Qurey LDAP
            msgID = self.ldap.search_ext(
                    baseDN,
                    ldap.SCOPE_SUBTREE,
                    searchFilter,
                    attrlist = attributes,
                    serverctrls = [pageControl] )

            # Parse the reply
            rType, rData, rMsgID, serverControls = self.ldap.result3(
                    msgID,
                    resp_ctrl_classes = self.responseCodes )

            #Take only what we need
            return rData, serverControls


    def search( self, baseDN, searchFilter, attributes = ['*'], callback = None ):
        page        = 0
        results     = []
        pageControl = self._setPageControl()

        if self.connected is False:
            self.__enter__()
            self.directSearch = True

        while True:
            page += 1

            data, serverControls = self._doSearch(baseDN, searchFilter, attributes, pageControl )

            results += self._handleResults( data, callback )

            if serverControls:
                cookie = self._getPageCookie( serverControls )
                if cookie:
                    pageControl = self._setPageControl( cookie = cookie )
                else:
                    break
            else:
                print "Warning:  Server ignores RFC 2696 control."
                break

            if page == self.maxPages:
                break

        if self.directSearch is True:
            self.__exit__(1,2,3)  # 1,2,3 doesn't do anything, but is required to fill the options
            self.directSearch = False

        return results

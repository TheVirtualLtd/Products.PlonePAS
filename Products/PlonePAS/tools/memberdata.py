"""
$Id: memberdata.py,v 1.4 2005/05/05 00:15:03 jccooper Exp $
"""
from Globals import InitializeClass
from Acquisition import aq_base

from Products.CMFPlone.MemberDataTool import MemberDataTool as BaseMemberDataTool
from Products.CMFPlone.MemberDataTool import MemberData as BaseMemberData   # this actually isn't used in Plone

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.MemberDataTool import CleanupTemp

from Products.PluggableAuthService.interfaces.authservice import IPluggableAuthService
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from Products.PlonePAS.interfaces.propertysheets import IMutablePropertySheet


class MemberDataTool(BaseMemberDataTool):
    """PAS-specific implementation of memberdata tool. Uses Plone MemberDataTool as a base."""

    #### an exact copy from the base, so that we pick up the new MemberData.
    #### wrapUser should have a MemberData factory method to over-ride (or even
    #### set at run-time!) so that we don't have to do this.
    def wrapUser(self, u):
        '''
        If possible, returns the Member object that corresponds
        to the given User object.
        We override this to ensure OUR MemberData class is used
        '''
        id = u.getId()
        members = self._members
        if not members.has_key(id):
            # Get a temporary member that might be
            # registered later via registerMemberData().
            temps = self._v_temps
            if temps is not None and temps.has_key(id):
                m = temps[id]
            else:
                base = aq_base(self)
                m = MemberData(base, id)
                if temps is None:
                    self._v_temps = {id:m}
                    if hasattr(self, 'REQUEST'):
                        # No REQUEST during tests.
                        self.REQUEST._hold(CleanupTemp(self))
                else:
                    temps[id] = m
        else:
            m = members[id]
        # Return a wrapper with self as containment and
        # the user as context.
        return m.__of__(self).__of__(u)

    def searchFulltextForMembers(self, s):
        """PAS-specific search for members by id, email, full name.
        """
        acl_users = getToolByName( self, 'acl_users')
        return acl_users.searchUsers( name=s, exact_match=False)
        # I don't think this is right: we need to return Members

InitializeClass(MemberDataTool)


class MemberData(BaseMemberData):

    ## setProperties uses setMemberProperties. no need to override.

    def setMemberProperties(self, mapping, force_local = 0):
        # Sets the properties given in the MemberDataTool.
        tool = self.getTool()
        print "setMemberProperties"
        # we could pay attention to force_local here...
        if IPluggableAuthService.isImplementedBy(self.acl_users):
            user = self.getUser()
            sheets = getattr(user, 'getOrderedPropertySheets', lambda: None)()
            print " PAS present. user is:", user.__class__
            # we won't always have PlonePAS users, due to acquisition, nor are guaranteed property sheets
            if sheets:
                print "  sheets present" # --
                # xxx track values set to defer to default impl
                # property routing
                for k,v in mapping.items():
                    for sheet in sheets:
                        print "    looking at", k, "=", v, "on", sheet
                        #import pdb; pdb.set_trace()
                        if sheet.hasProperty(k):
                            print '     hasProperty', k, 'sheet', sheet
                            if IMutablePropertySheet.isImplementedBy(sheet):
                                sheet.setProperty( k, v )
                                print "     Set", k, v, sheet
                            else:
                                raise RuntimeError("mutable property provider shadowed by read only provider")
                self.notifyModified()
                return
        print " PAS fails, using MemberData"
        # defer to base impl in absence of PAS, a PAS user, or property sheets
        return BaseMemberData.setMemberProperties(self, mapping, force_local)

    def getProperty(self, id, default=None):
        if IPluggableAuthService.isImplementedBy(self.acl_users):
            user = self.getUser()
            sheets = getattr(user, 'getOrderedPropertySheets', lambda: None)()

            # we won't always have PlonePAS users, due to acquisition, nor are guaranteed property sheets
            if sheets:
                for sheet in user.getOrderedPropertySheets():
                    if sheet.hasProperty(id):
                        return sheet.getProperty(id)
        return BaseMemberData.getProperty(self, id)

InitializeClass(MemberData)

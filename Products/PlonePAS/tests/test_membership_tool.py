"""
$Id: test_membership_tool.py,v 1.2 2005/05/30 21:30:04 dreamcatcher Exp $
"""

import os, sys
import unittest

if __name__ == '__main__':
    execfile(os.path.join(os.path.dirname(sys.argv[0]), 'framework.py'))

from Testing import ZopeTestCase
from Products.PlonePAS.tests import PloneTestCase

from cStringIO import StringIO
from zExceptions import BadRequest
from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.tools.memberdata import MemberData
from Products.PlonePAS.plugins.ufactory import PloneUser

class MembershipToolTest(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.mt = mt = getToolByName(self.portal, 'portal_membership')
        self.md = md = getToolByName(self.portal, 'portal_memberdata')

        self.member_id = 'member1'
        # Create a new Member
        mt.addMember(self.member_id, 'pw', ['Member'], [],
                     {'email': 'member1@host.com',
                      'title': 'Member #1'})

    def test_get_member(self):
        member = self.portal.acl_users.getUserById(self.member_id)
        self.failIf(member is None)

        # Should be wrapped into the PAS.
        got = aq_base(aq_parent(member))
        expected = aq_base(self.portal.acl_users)
        self.assertEquals(got, expected)

        self.failUnless(isinstance(member, PloneUser))

    def test_get_member_by_id(self):
        # Use tool way of getting member by id. This returns a
        # MemberData object wrapped by the member
        member = self.mt.getMemberById(self.member_id)
        self.failIf(member is None)
        self.failUnless(isinstance(member, MemberData))
        self.failUnless(isinstance(aq_parent(member), PloneUser))

class MemberAreaTest(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.mt = mt = getToolByName(self.portal, 'portal_membership')
        self.md = md = getToolByName(self.portal, 'portal_memberdata')
        # Enable member-area creation
        self.mt.memberareaCreationFlag = 1
        # Those are all valid chars in Zope.
        self.mid = "Member #1 - Houston, TX. ($100)"
        self.loginPortalOwner()

    def test_funky_member_ids_1(self):
        mid = self.mid
        minfo = (mid, 'pw', ['Member'], [])

        # Create a new User
        self.portal.acl_users._doAddUser(*minfo)
        self.failIfRaises(BadRequest, self.mt.createMemberArea, mid)

    def test_funky_member_ids_2(self):
        # Forward-slash is not allowed
        mid = self.mid + '/'
        minfo = (mid, 'pw', ['Member'], [])

        # Create a new User
        self.portal.acl_users._doAddUser(*minfo)
        self.failUnlessRaises(BadRequest, self.mt.createMemberArea, mid)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MembershipToolTest))
    suite.addTest(unittest.makeSuite(MemberAreaTest))
    return suite

if __name__ == '__main__':
    framework()
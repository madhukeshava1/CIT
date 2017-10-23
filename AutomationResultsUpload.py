import os.path

import pdb
import time
import os
import re
import filecmp
import sys
import platform
import httplib
import socket
from time import gmtime, strftime
import subprocess
import random
import xml.etree.ElementTree as ET

import xml.dom.minidom
import pprint
import pdb
import json
import urllib
import urllib2
import telnetlib
import types
import commands
import string
import traceback
import copy

import unittest
from  testLinkLibrary import *

class RestTestCase(unittest.TestCase):
    #     #self.testLinkTCName1 = {'TC-3': 'Inc_Man_36', 'TC-4': 'Inc_Man_37'}

    def testCaseSequence(self):
        '''
                This function defines the sequence under which a
                particular test case will go.
        '''
        # setting the result to be true initially
        result = "PASS"
        self.testLinkTCName = ['ivtree_1','ivtree_2']
        tls = getTestLinkObject(
            result_dict['testLinkURL'], result_dict['testLinkDEVKEY'])

        addBuildToTestPlan(tls, result_dict['testLinkTestProjectName'], result_dict['testLinkTestPlanName'],  result_dict['testLinkBuildName'], "fROM AUT")
        for name in self.testLinkTCName:
        # if user wants to upload result in TestLink
            if result_dict['uploadResultInTestLink'] == 'True' and name != '':
                try:
                # establish connection with TestLink


                    # testCaseStatus is 'p' for PASS and 'f' for FAIL
                    testCaseStatus = ''
                    if result == "PASS":
                        testCaseStatus = 'p'
                    else:
                        testCaseStatus = 'f'

                    updateResultInTestLink(tls, result_dict['testLinkTestProjectName'], result_dict['testLinkTestPlanName'], result_dict[
                                       'testLinkBuildName'],name, testCaseStatus, result_dict['testLinkPlatform'])
                except Exception as e:
                    print(
                     'Error "%s" while updating result in TestLink' % e)
if __name__ == '__main__':
    # read the configuration XML file
    tree = ET.parse(os.path.dirname(os.path.abspath(__file__)) + os.sep + 'ConfigInput.xml')
    #root = tree.getroot()

    for node in tree.iter():
        if node.tag == "Parameters":
            result_dict=node.attrib
            print result_dict
    unittest.main()
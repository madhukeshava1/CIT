import testlink
import pdb

def getTestLinkObject(testLinkURL, testLinkDEVKEY):
    """establishes connection with TestLink and returns thye object that interacts with TestLink"""
    testLinkObject = testlink.TestlinkAPIClient(testLinkURL, testLinkDEVKEY)
    return testLinkObject
    
def getTestLinkIDs(testLinkObj, testLinkProjectName, testLinkPlanName = '', testLinkTestSuiteName = '', childTestSuiteName = ''):
    """ given the Test Project, Test Plan, parent Test Suite and Child Test Suite names as in TestLink, returns their IDs (For test suite, if child Test Suite
    name is passed as argument, then its ID is returned, else the parent Test Suite ID id returned"""
    projID = ''
    planID = ''
    testSuiteID = ''
    
    # specify the Test Project name and get the details of the Test Project
    projDict = testLinkObj.getTestProjectByName(testLinkProjectName)
    #assign Test Project ID
    projID = projDict['id']

    #if user has specified the name of the Test Plan, find its ID
    if testLinkPlanName <> '':
        #specify the Test Project ID name and get the details of the Test Plans
        planList = testLinkObj.getProjectTestPlans(projID)
        #go through all the Test Plans and search for the required Test Plan
        for planDict in planList:
            if planDict['name'] == testLinkPlanName:
                planID = planDict['id']
    
    #if user has specified the name of the Parent Test Suite, find its ID
    if testLinkTestSuiteName <> '':
        #specify the Test Project ID and get the details of the Parent Test Suites
        testSuiteList = testLinkObj.getFirstLevelTestSuitesForTestProject(projID)
        
        #go through all the Test Plans and search for the required Test Plan
        for testSuiteDict in testSuiteList:
            if testSuiteDict['name'] == testLinkTestSuiteName:
                testSuiteID = testSuiteDict['id']
        
        #if user has specified the name of the Child Test Suite, find its ID
        if childTestSuiteName <> '':
            #specify the Parent Test Suite ID and get the details of the Child Test Suites
            childTestSuites = testLinkObj.getTestSuitesForTestSuite(testSuiteID)

            # childTestSuites is a dictionary with key as child Test Suite ID and value as a dictionary	of child Test suite details - if there are multiple child Test Suites
            # else it is a single dictionary with child Test Suite details

            #check if the child Test Suite exists under the parent Test Suite
            # scan the dictionary and check if any of the values is a dictionary. If yes then there are multiple children Test Suites
            multiple = 0
            testSuiteID = ''
            for key, value in childTestSuites.items():
                if isinstance(value, dict):
                    multiple = 1
                    break
            
            if multiple:
                for key, value in childTestSuites.items():
                    if value['name'].strip() == childTestSuiteName.strip():
                        testSuiteID = value['id']
                        break
            else:
                if childTestSuites['name'].strip() == childTestSuiteName.strip():
                    testSuiteID = childTestSuites['id']

    return projID, planID, testSuiteID
        
def addTestCaseToTestLink(testLinkObject, testLinkProjectName, testLinkPlanName, testLinkTestSuiteName, testCaseName, executionType, TCpreconditions = '', testCaseDesc = '', testLinkUserName = 'admin', platform =''):
    try:
        # to check if the test case has already been added in TestLink
        result =  testLinkObject.getTestCaseIDByName(testCaseName, testprojectname=testLinkProjectName)
    except:
        # if the test case has not been added in testLink, add it
        
        # get the Test Project ID, Test Plan ID and Test Suite ID
        testLinkProjID, testLinkPlanID, testLinkTestSuiteID = getTestLinkIDs(testLinkObject, testLinkProjectName, testLinkPlanName, testLinkTestSuiteName)
        # create the test case
        newTC = testLinkObject.createTestCase(testCaseName, testLinkTestSuiteID, testLinkProjID, testLinkUserName, testCaseDesc, steps='', preconditions=TCpreconditions, execution=executionType)
        
        #find the version number of the test case
        newTestCaseVersion = newTC[0]['additionalInfo']['version_number']
        
        # find the full external ID of the test case
        # find the prefix of the project
        projDetails = testLinkObject.getTestProjectByName(testLinkProjectName)
        prefix = projDetails['prefix']
        newTestCaseExternalID = prefix + '-' + str(newTC[0]['additionalInfo']['external_id'])
        
        #add the test case
        if platform == '':
            testLinkObject.addTestCaseToTestPlan(testLinkProjID, testLinkPlanID, newTestCaseExternalID, newTestCaseVersion)
        else:
            #find the platform ID:
            platformID  = ''
            platformList = testLinkObject.getTestPlanPlatforms(testLinkPlanID)
            for platformDict in platformList:
                if platform == platformDict['name']:
                    platformID = platformDict['id']
            testLinkObject.addTestCaseToTestPlan(testLinkProjID, testLinkPlanID, newTestCaseExternalID, newTestCaseVersion, platformid=platformID)

def addTestCaseToChildSuite(testLinkObject, testLinkProjectName, testLinkPlanName, testLinkTestSuiteName, testLinkParentTestSuiteName, testCaseName, executionType, TCpreconditions = '', testCaseDesc = '', testLinkUserName = 'admin', platform =''):
    try:
        # to check if the test case has already been added in TestLink. If the test case is not present, control of
        # the program will go to the except
        result =  testLinkObject.getTestCaseIDByName(testCaseName, testprojectname=testLinkProjectName)

        # if control of the program comes here, then the test case is present in TestLink, but may not be added to the test plan
        # add to the test plan
        # add the test case to the specified test plan on the platform
        try:
            # get the Test Project ID, Test Plan ID and Test Suite ID
            testLinkProjID, testLinkPlanID, testLinkTestSuiteID = getTestLinkIDs(testLinkObject, testLinkProjectName, testLinkPlanName, testLinkParentTestSuiteName, testLinkTestSuiteName)

            # find the full external ID of the test case
            # find the prefix of the project
            projDetails = testLinkObject.getTestProjectByName(testLinkProjectName)
            prefix = projDetails['prefix']

            newTestCaseExternalID = prefix + '-' + str(result[0]['tc_external_id'])

            if platform == '':
                testLinkObject.addTestCaseToTestPlan(testLinkProjID, testLinkPlanID, newTestCaseExternalID, 1)
            else:
                #find the platform ID:
                platformID  = ''
                platformList = testLinkObject.getTestPlanPlatforms(testLinkPlanID)
                for platformDict in platformList:
                    if platform == platformDict['name']:
                        platformID = platformDict['id']
                # add the test case to the test plan on the platform
                testLinkObject.addTestCaseToTestPlan(testLinkProjID, testLinkPlanID, newTestCaseExternalID, 1, platformid=platformID)
        except Exception as e:
            # in case the test case is already added to the test plan (on the platform if present,
            # otherwise added on the test plan without platform)
            pass
    except Exception as e:
        # if the test case has not been added in testLink, add it
        
        # get the Test Project ID, Test Plan ID and Test Suite ID
        testLinkProjID, testLinkPlanID, testLinkTestSuiteID = getTestLinkIDs(testLinkObject, testLinkProjectName, testLinkPlanName, testLinkParentTestSuiteName, testLinkTestSuiteName)
        
        # create the test case
        newTC = testLinkObject.createTestCase(testCaseName, testLinkTestSuiteID, testLinkProjID, testLinkUserName, testCaseDesc, steps='', preconditions=TCpreconditions, execution=executionType)
        
        # find the version number of the test case
        newTestCaseVersion = newTC[0]['additionalInfo']['version_number']
        
        # find the full external ID of the test case
        # find the prefix of the project
        projDetails = testLinkObject.getTestProjectByName(testLinkProjectName)
        prefix = projDetails['prefix']
        newTestCaseExternalID = prefix + '-' + str(newTC[0]['additionalInfo']['external_id'])
        
        # add the test case to the specified test plan on the platform
        if platform == '':
            testLinkObject.addTestCaseToTestPlan(testLinkProjID, testLinkPlanID, newTestCaseExternalID, newTestCaseVersion)
        else:
            #find the platform ID:
            platformID  = ''
            platformList = testLinkObject.getTestPlanPlatforms(testLinkPlanID)
            for platformDict in platformList:
                if platform == platformDict['name']:
                    platformID = platformDict['id']
            testLinkObject.addTestCaseToTestPlan(testLinkProjID, testLinkPlanID, newTestCaseExternalID, newTestCaseVersion, platformid=platformID)			

def updateResultInTestLink(testLinkObject, testLinkProjectName, testLinkPlanName, testLinkBuildName, testCaseName, testCaseStatus, platform='', bugID='', customFieldDict={}):
    
    # obatin the test plan ID
    projID, planID, testSuiteID = getTestLinkIDs(testLinkObject, testLinkProjectName, testLinkPlanName)
    
    # get the test case ID
    testCaseDetails = testLinkObject.getTestCaseIDByName(testCaseName, testprojectname=testLinkProjectName)
    testCaseID = testCaseDetails[0]['id']
    
    #assign user for execution
    # get the test case external ID
    # get the project prefix
    projDetails = testLinkObject.getTestProjectByName(testLinkProjectName)
    prefix = projDetails['prefix']
    # form the full test case external ID
    newTC = testLinkObject.getTestCaseIDByName(testCaseName, testprojectname=testLinkProjectName)
    testCaseExternalID = prefix + '-' + str(newTC[0]['tc_external_id'])
    
    # report the result in TestLink
    if bugID == '':
        if platform:
            if customFieldDict:
                testLinkTestCaseResult = testLinkObject.reportTCResult(testCaseID, planID, testLinkBuildName, testCaseStatus, '', platformname=platform, customfields=customFieldDict)
            else:
                testLinkTestCaseResult = testLinkObject.reportTCResult(testCaseID, planID, testLinkBuildName, testCaseStatus, '', platformname=platform)
        else:
            if customFieldDict:
                testLinkTestCaseResult = testLinkObject.reportTCResult(testCaseID, planID, testLinkBuildName, testCaseStatus, '', customfields=customFieldDict)
            else:
                testLinkTestCaseResult = testLinkObject.reportTCResult(testCaseID, planID, testLinkBuildName, testCaseStatus, '')
    else:
        if platform:
            if customFieldDict:
                testLinkTestCaseResult = testLinkObject.reportTCResult(testCaseID, planID, testLinkBuildName, testCaseStatus, '', platformname=platform, bugid=bugID, customfields=customFieldDict)
            else:
                testLinkTestCaseResult = testLinkObject.reportTCResult(testCaseID, planID, testLinkBuildName, testCaseStatus, '', platformname=platform, bugid=bugID)
        else:
            if customFieldDict:
                testLinkTestCaseResult = testLinkObject.reportTCResult(testCaseID, planID, testLinkBuildName, testCaseStatus, '', bugid=bugID, customfields=customFieldDict)
            else:
                testLinkTestCaseResult = testLinkObject.reportTCResult(testCaseID, planID, testLinkBuildName, testCaseStatus, '', bugid=bugID)

    
def createTestProject(testLinkObject, testLinkProjectInfoDict):
    """ Create a Test Project in TestLink if it does not exist """

    """ testLinkProjectInfoDict conatins the following keys:
    testLinkProjectName, testLinkProjectPrefix, testLinkProjInfo, isActive, isPublic, requirementsEnabled, priorityEnabled, 
    automationEnabled, inventoryEnabled
    """
    testLinkProjectName = testLinkProjectInfoDict['testLinkProjectName']
    testLinkProjectPrefix = testLinkProjectInfoDict['testLinkProjectPrefix']
    testLinkProjInfo = testLinkProjectInfoDict['testLinkProjInfo']
    isActive = testLinkProjectInfoDict['isActive']
    isPublic = testLinkProjectInfoDict['isPublic']
    requirementsEnabled = testLinkProjectInfoDict['requirementsEnabled']
    priorityEnabled = testLinkProjectInfoDict['priorityEnabled']
    automationEnabled = testLinkProjectInfoDict['automationEnabled']
    inventoryEnabled = testLinkProjectInfoDict['inventoryEnabled']
    
    #check if the project already exists in TestLink
    try:
        project = testLinkObject.getTestProjectByName(testLinkProjectName)
    except:
        # if the project has not been added in Test Link, create it
        newProject = testLinkObject.createTestProject(testLinkProjectName, testLinkProjectPrefix, notes=testLinkProjInfo, active=isActive, \
        public=isPublic, options={'requirementsEnabled': requirementsEnabled, 'testPriorityEnabled': priorityEnabled, 'automationEnabled': automationEnabled, \
        'inventoryEnabled': inventoryEnabled})

def createTestPlanForProject(testLinkObject, testLinkPlanDict):
    """ Create a Test plan under a Test project in Test Link if it does not exist """
    
    """ testLinkPlanDict contains the following keys:
    testLinkPlanName, testLinkProjectName, testPlanInfo, isActive, isPublic
    """
    testLinkProjectName = testLinkPlanDict['testLinkProjectName']
    testLinkPlanName = testLinkPlanDict['testLinkPlanName']
    testPlanInfo = testLinkPlanDict['testPlanInfo']
    isActive = testLinkPlanDict['isActive']
    isPublic = testLinkPlanDict['isPublic']
    
    try:
        #get the project ID
        
        projectID, planID, suiteID = getTestLinkIDs(testLinkObject, testLinkProjectName)
        
        # check if the Test Plan exists under the Test Project
        planExists = 0
        plans = testLinkObject.getProjectTestPlans(projectID)
        
        for plan in plans:
            if plan['name'] == testLinkPlanName:
                planExists = 1
                break
        if not planExists:
            
            newTestPlan = testLinkObject.createTestPlan(testLinkPlanName, testLinkProjectName, notes=testPlanInfo, active=isActive, public=isPublic)
    except:	
        # If the test Plan has not been created, create and add it
        newTestPlan = testLinkObject.createTestPlan(testLinkPlanName, testLinkProjectName, notes=testPlanInfo, active=isActive, public=isPublic)

def createTestSuiteForTestPlan(testLinkObject, testLinkTestSuiteDict):
    """ Create a Test Suite under a Test Plan in Test Link if it does not exist """
    
    """ testLinkTestSuiteDict contains the following keys:
    testLinkPlanName, testLinkProjectName, testSuiteDetails, testLinkTestSuiteName
    """
    testLinkProjectName = testLinkTestSuiteDict['testLinkProjectName']
    testLinkPlanName = testLinkTestSuiteDict['testLinkPlanName']
    testLinkTestSuiteName = testLinkTestSuiteDict['testLinkTestSuiteName']
    testSuiteDetails = testLinkTestSuiteDict['testSuiteDetails']
    
    try:
        #get the project ID
        projectID, planID, suiteID = getTestLinkIDs(testLinkObject, testLinkProjectName, testLinkPlanName)
        # check if the Test Plan exists under the Test Project
        testSuites = testLinkObject.getTestSuitesForTestPlan(planID)
        testSuiteExists = 0
        for testSuite in testSuites:
            if testSuite['name'] == testLinkTestSuiteName:
                testSuiteExists = 1
                break
        if not testSuiteExists:
            newTestSuite = testLinkObject.createTestSuite(projectID, testLinkTestSuiteName, testSuiteDetails)
    except:	
        # If the test Plan has not been created, create and add it
        newTestSuite = testLinkObject.createTestSuite(projectID, testLinkTestSuiteName, testSuiteDetails)
        
def createChildTestSuiteForTestPlan(testLinkObject, testLinkTestSuiteDict, parentTestSuiteName):
    """ Create a Test Suite under a Test Plan in Test Link if it does not exist """
    
    """ testLinkTestSuiteDict contains the following keys:
    testLinkPlanName, testLinkProjectName, testSuiteDetails, testLinkTestSuiteName
    """
    testLinkProjectName = testLinkTestSuiteDict['testLinkProjectName']
    testLinkPlanName = testLinkTestSuiteDict['testLinkPlanName']
    testLinkTestSuiteName = testLinkTestSuiteDict['testLinkTestSuiteName']
    testSuiteDetails = testLinkTestSuiteDict['testSuiteDetails']
    
    try:
    
        #get the parent Test Suite ID
        projectID, planID, suiteID = getTestLinkIDs(testLinkObject, testLinkProjectName, testLinkPlanName, parentTestSuiteName)
        
        childTestSuites = testLinkObject.getTestSuitesForTestSuite(suiteID) 
        
        # childTestSuites is a dictionary with key as child Test Suite ID and value as a dictionary	of child Test suite details - if there are multiple child Test Suites
        # else it is a single dictionary with child Test Suite details
        
        if not childTestSuites:
            newTestSuite = testLinkObject.createTestSuite(projectID, testLinkTestSuiteName, testSuiteDetails, parentid=suiteID)
        else:
            #check if the child Test Suite exists under the parent Test Suite
            testSuiteExists = 0
            # scan the dictionary and check if any of the values is a dictionary. If yes then there are multiple children Test Suites
            multiple = 0
            for key, value in childTestSuites.items():
                if isinstance(value, dict):
                    multiple = 1
                    break
            if multiple:
                for key, value in childTestSuites.items():
                    if value['name'] == testLinkTestSuiteName:
                        testSuiteExists = 1
                        break
            else:
                if childTestSuites['name'] == testLinkTestSuiteName:
                    testSuiteExists = 1
            
            if not testSuiteExists:
                newTestSuite = testLinkObject.createTestSuite(projectID, testLinkTestSuiteName, testSuiteDetails, parentid=suiteID)
                
    except:
        newTestSuite = testLinkObject.createTestSuite(projectID, testLinkTestSuiteName, testSuiteDetails, parentid=suiteID)
        
def addStepsToTestCase(testLinkObject, testLinkProjectName, testCaseName, stepList):
    """ Add steps to a test case. The step details are step number, action, expected results and execution type """
    """ stepList is a list of step dictionaries, each dictionary having fields step_number, actions and expected_results"""
    
    #get the external ID of the test case
    #get the prefix to form the full external test case ID
    projDetails = testLinkObject.getTestProjectByName(testLinkProjectName)
    prefix = projDetails['prefix']
    newTC = testLinkObject.getTestCaseIDByName(testCaseName, testprojectname=testLinkProjectName)
    testCaseExternalID = prefix + '-' + str(newTC[0]['tc_external_id'])
    
    #find the version of the test case
    testCaseDetails = testLinkObject.getTestCase(None, testcaseexternalid=testCaseExternalID)
    testCaseVersion = testCaseDetails[0]['version']
    
    #add the steps to the test case
    createSteps = testLinkObject.createTestCaseSteps('update', stepList, testcaseexternalid=testCaseExternalID, version=testCaseVersion)
    
def addBuildToTestPlan(testLinkObject, testLinkProjectName, testLinkPlanName, buildName, buildNotes):
    #newBuild = myTestLink.createBuild(newTestPlanID_A, NEWBUILD_A, 'Notes for the Build')
    # check if the build already exists in the Test Plan
    try:
        projectID, planID, suiteID = getTestLinkIDs(testLinkObject, testLinkProjectName, testLinkPlanName)
        builds = testLinkObject.getBuildsForTestPlan(planID)
        buildExists = 0
        for build in builds:
            if build['name'] == buildName:
                buildExists = 1
                break
        if not buildExists:
            newBuild = testLinkObject.createBuild(planID, buildName, buildNotes)
    except:
        newBuild = testLinkObject.createBuild(planID, buildName, buildNotes)
        
def addPlatform(testLinkObject, testLinkProjectName, testLinkPlanName, osList, add=1):
    
    # check if the platform exists
    for os in osList:
        try:
            # OS will be NULL if no platforms are specified in teh XML configuration files
            if os:
                projectID, planID, suiteID = getTestLinkIDs(testLinkObject, testLinkProjectName, testLinkPlanName)
                platformList = testLinkObject.getTestPlanPlatforms(planID)
                
                platformExists = 0
                for platformDict in platformList:
                    if platformDict['name'] == os:
                        platformExists = 1
                        break
                
                if not platformExists:
                    
                    # if the platform does not exist in the Test Plan, create and add it
                    newPlatform = testLinkObject.createPlatform(testLinkProjectName, os, notes=os)
                
                # if the platform has to be added to the test plan after creation
                if add:
                    testLinkObject.addPlatformToTestPlan(planID, os)
            else:
                pass
        except:
            # if the platform has to be added to the test plan after creation
            if add:
                testLinkObject.addPlatformToTestPlan(planID, os)
            
def updatePlatformForTestCase(testLinkObject, testLinkProjectName, testLinkPlanName, testCaseName, newPlatform):

    try:
        #get the ID's of the Test Project and Test Plan
        projectID, planID, suiteID = getTestLinkIDs(testLinkObject, testLinkProjectName, testLinkPlanName)
        
        # get the platform ID of newPlatform
        platformID  = ''
        platformList = testLinkObject.getTestPlanPlatforms(planID)
        for platformDict in platformList:
            if newPlatform == platformDict['name']:
                platformID = platformDict['id']
                
        # get the test case external ID
        # get the project prefix
        projDetails = testLinkObject.getTestProjectByName(testLinkProjectName)
        prefix = projDetails['prefix']
        # form the full test case external ID
        newTC = testLinkObject.getTestCaseIDByName(testCaseName, testprojectname=testLinkProjectName)
        testCaseExternalID = prefix + '-' + str(newTC[0]['tc_external_id'])
        
        # get the test case version
        newTC = testLinkObject.getTestCase(None, testcaseexternalid=testCaseExternalID)
        testCaseVersion = int(newTC[0]['version'])
        
        # add the test case to the Test Plan with newPlatform
        testLinkObject.addTestCaseToTestPlan(projectID, planID, testCaseExternalID, testCaseVersion, platformid=platformID)
    except:
        pass

def addTestCaseToSubPlan(testLinkObject, testLinkProjectName, testLinkPlanName, testLinkTestSuiteName, testCaseName, executionType, TCpreconditions = '', testCaseDesc = '', testLinkUserName = 'admin', platform ='', executionPriority = ''):
    try:
        # get the Test Project ID, Test Plan ID and Test Suite ID
        testLinkProjID, testLinkPlanID, testLinkTestSuiteID = getTestLinkIDs(testLinkObject, testLinkProjectName, testLinkPlanName, testLinkTestSuiteName)
        # create the test case
        # newTC = testLinkObject.createTestCase(testCaseName, testLinkTestSuiteID, testLinkProjID, testLinkUserName, testCaseDesc, steps='', preconditions=TCpreconditions, execution=executionType)
        
        # form the full test case external ID
        projDetails = testLinkObject.getTestProjectByName(testLinkProjectName)
        prefix = projDetails['prefix']
        newTC = testLinkObject.getTestCaseIDByName(testCaseName, testprojectname=testLinkProjectName)
        testCaseExternalID = prefix + '-' + str(newTC[0]['tc_external_id'])
        
        # get the test case version
        newTC = testLinkObject.getTestCase(None, testcaseexternalid=testCaseExternalID)
        testCaseVersion = int(newTC[0]['version'])
        
        #add the test case
        if platform == '':
            testLinkObject.addTestCaseToTestPlan(testLinkProjID, testLinkPlanID, testCaseExternalID, testCaseVersion)
        else:
            #find the platform ID:
            platformID  = ''
            platformList = testLinkObject.getTestPlanPlatforms(testLinkPlanID)
            for platformDict in platformList:
                if platform.lower() == platformDict['name'].lower():
                    platformID = platformDict['id']
            testLinkObject.addTestCaseToTestPlan(testLinkProjID, testLinkPlanID, testCaseExternalID, testCaseVersion, platformid=platformID)
    except Exception as e:
        # print "Note: %s " % e
        pass


def updateTestCaseExecutionAutomated(testLinkObject, testLinkProjectName, testCaseName, testCaseExecutionType=2):
    """ Update the execution type for a test case and its steps as 'automated' """
    try:
        # pdb.set_trace()

        # get the test case external ID
        # get the project prefix
        projDetails = testLinkObject.getTestProjectByName(testLinkProjectName)
        prefix = projDetails['prefix']
        # form the full test case external ID
        newTC = testLinkObject.getTestCaseIDByName(testCaseName, testprojectname=testLinkProjectName)
        testCaseExternalID = prefix + '-' + str(newTC[0]['tc_external_id'])
        
        #get the steps of the test case from its specification in TestLink
        testCaseDetails = testLinkObject.getTestCase(None, testcaseexternalid=testCaseExternalID)
        
        stepList = testCaseDetails[0]['steps']
        for stepDict in stepList:
            stepDict['execution_type'] = testCaseExecutionType	# 2 - Automated, 1 - Manual, 3 - Automatable
        
        # update the test case execution type
        testLinkObject.updateTestCase(testCaseExternalID, executiontype=testCaseExecutionType)
        
        # update the execution type for the steps
        addStepsToTestCase(testLinkObject, testLinkProjectName, testCaseName, stepList)
    
    except Exception as e:
        print "Error: ", e

def getKeywordsInTestProject(testLinkObject, testProjectName):
    """
        Return a list of keywords defined in the specified test project
    """
    projDetails = testLinkObject.getTestProjectByName(testProjectName)
    
    # get the keywords defined for the test project
    keywords = testLinkObject.getProjectKeywords(projDetails['id'])
    
    return keywords

def addKeywordToTestCase(testLinkObject, testLinkProjectName, testCaseName, keyword):
    """
        Assign the specified keyword to the specified test case, if not assigned already
    """
    # get the test case external ID
    # get the project prefix
    projDetails = testLinkObject.getTestProjectByName(testLinkProjectName)
    prefix = projDetails['prefix']
    # form the full test case external ID
    newTC = testLinkObject.getTestCaseIDByName(testCaseName, testprojectname=testLinkProjectName)
    testCaseExternalID = prefix + '-' + str(newTC[0]['tc_external_id'])

    # check if the keyword is assigned to the test case
    keywords = testLinkObject.getTestCaseKeywords(testcaseexternalid=testCaseExternalID)

    if not (keyword in keywords.values()):
        # assign the keyword to the test case
        testLinkObject.addTestCaseKeywords(testCaseExternalID, [keyword])

def assignTesterToTestCase(testLinkObject, testLinkProjectName, testLinkPlanName, testCaseName, buildName, testerLogin, platformName=''):
    """
        Check if the tester login specified is valid. If yes, assign this Tester to
        the specified test case on the specified build and platform (if applicable)
    """
    # check if the tester login provided is valid
    try:
        testerDetails = testLinkObject.getUserByLogin(testerLogin)

        # get the testb plan ID
        projectID, testPlanId, testSuiteID = getTestLinkIDs(testLinkObject, testLinkProjectName, testLinkPlanName)

        # get the test case external ID
        # get the project prefix
        projDetails = testLinkObject.getTestProjectByName(testLinkProjectName)
        prefix = projDetails['prefix']
        # form the full test case external ID
        newTC = testLinkObject.getTestCaseIDByName(testCaseName, testprojectname=testLinkProjectName)
        testCaseExternalID = prefix + '-' + str(newTC[0]['tc_external_id'])

        # assign the test case to the tester
        # if a platform is added to the Test Plan, assign on that platform
        if platformName:
            testLinkObject.assignTestCaseExecutionTask(testerLogin, testPlanId, testCaseExternalID, buildname=buildName, platformname=platformName)
        else:
            testLinkObject.assignTestCaseExecutionTask(testerLogin, testPlanId, testCaseExternalID, buildname=buildName)

    except Exception as e:
        print "Error: %s" % e

def updateDesignCustomField(testLinkObject, testCaseName, testLinkProjectName, customFieldDict):
    """
        Update the value of custom field(s) that are set in the test specification of
        the test case
    """
    # get the Test Project ID
    testLinkProjID, testLinkPlanID, testLinkTestSuiteID = getTestLinkIDs(testLinkObject, testLinkProjectName, '', '')
    
    # get the external ID of the test case
    tc = testLinkObject.getTestCaseIDByName(testCaseName, testprojectname=testLinkProjectName)

    # get the project prefix
    projDetails = testLinkObject.getTestProjectByName(testLinkProjectName)
    prefix = projDetails['prefix']

    testCaseExternalID = prefix + '-' + str(tc[0]['tc_external_id'])

    # get the test case vrsion number
    tc = testLinkObject.getTestCase(None, testcaseexternalid=testCaseExternalID)

    testCaseVersion = tc[0]['version']

    # update the custom field values
    try:
        testLinkObject.updateTestCaseCustomFieldDesignValue(testCaseExternalID, testCaseVersion, testLinkProjID, customFieldDict)
    except Exception as e:
        print "Error while updating custom field value: %s" % e


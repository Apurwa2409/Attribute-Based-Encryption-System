from flask import Flask, request, render_template, jsonify, redirect, url_for
import xml.etree.ElementTree as ET 
import pypyodbc 
import os
import hashlib
import json
import time
from datetime import datetime, timedelta
import ftplib
import smtplib 
from email.mime.text import MIMEText

from CloudProviderDataModel import CloudProviderDataModel
from RoleModel import RoleModel
from AttributeIPControlModel import AttributeIPControlModel
from AttributeTimeControlModel import AttributeTimeControlModel
from UserModel import UserModel
from VideoDataModel import VideoDataModel
from Constants import connString

app = Flask(__name__)
emailid = " "
roleObject = None
ipControlObject = AttributeIPControlModel()
timeControlObject = AttributeTimeControlModel()

errorResult = ""
errType = ""

def initialize():
    errorResult = ""
    errType=""
    
@app.route("/")
def home():
    initialize()
    return render_template('Login.html')

@app.route("/processLogin", methods=['POST'])
def authenticateLogin():
    global emailid, roleObject
    initialize()
    emailid = request.form['emailid']
    password = request.form['password']
    
    
    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM Users WHERE emailid = '"+emailid+"' AND password = '"+password+"'"; 
    print(sqlcmd1)
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    cur1.commit()
    if not row:
        return render_template('Login.html', processResult="Invalid Userid / Password")
    
    cur2 = conn1.cursor()
    sqlcmd2 = "SELECT * FROM Role WHERE roleID = '"+str(row[4])+"'"; 
    cur2.execute(sqlcmd2)
    row2 = cur2.fetchone()
   
    if not row2:
        return render_template('Login.html', processResult="Invalid Role")
    
    roleObject = RoleModel(row2[0], row2[1],row2[2],row2[3],row2[4],row2[5],row2[6],row2[7])
    print("Role Name", row2[1], "canCloudProvider",row2[2], "canVideoData",row2[3], "canBlockchainGeneration",row2[4], "canBlockchainReport",row2[5], "canRole",row2[6], "canUser",row2[7])
    cur2.commit()
    conn1.close();
    
    tree = ET.parse('static/AttributeControl.xml') 
  
    # get root element 
    root = tree.getroot() 
    print("root111", root.tag)
    # create empty list for news items 
    newsitems = [] 
  
    # iterate news items 
    for item in root.findall('./Attribute'): 
        attributeName = ""
        for child in item:
            if child.tag == 'AttributeName':
                attributeName = child.text
            if attributeName == "IPControl":
                if child.tag == "UserID":
                    if child.text.strip() != emailid :
                        break
                    else: 
                        ipControlObject.userID = emailid
                if child.tag == "IPAddress":
                    ipControlObject.IPAddress = child.text.strip()
            if attributeName == "TimeControl": 
                if child.tag == "UserID":
                    if child.text.strip() != emailid :
                        break
                    else: 
                        timeControlObject.userID = emailid
                if child.tag == "canCloudProviderA":
                    timeControlObject.canCloudProviderA = child.tag.strip()
                    for child2 in child:
                        if child2.tag == "AttributeFromTime":
                            timeControlObject.canCloudProviderATime["FromTime"] = child2.text.strip()
                        if child2.tag == "AttributeToTime":
                            timeControlObject.canCloudProviderATime["ToTime"] = child2.text.strip()
                if child.tag == "canVideoDataA":
                    timeControlObject.canVideoDataA = child.tag.strip()
                    for child2 in child:
                        if child2.tag == "AttributeFromTime":
                            timeControlObject.canVideoDataATime["FromTime"] = child2.text.strip()
                        if child2.tag == "AttributeToTime":
                            timeControlObject.canVideoDataATime["ToTime"] = child2.text.strip()
                if child.tag == "canBlockchainGenerationA":
                    timeControlObject.canBlockchainGenerationA = child.tag.strip()
                    for child2 in child:
                        if child2.tag == "AttributeFromTime":
                            timeControlObject.canBlockchainGenerationATime["FromTime"] = child2.text.strip()
                        if child2.tag == "AttributeToTime":
                            timeControlObject.canBlockchainGenerationATime["ToTime"] = child2.text.strip()
                if child.tag == "canBlockchainReportA":
                    timeControlObject.canBlockchainReportA = child.tag.strip()
                    for child2 in child:
                        if child2.tag == "AttributeFromTime":
                            timeControlObject.canBlockchainReportATime["FromTime"] = child2.text.strip()
                        if child2.tag == "AttributeToTime":
                            timeControlObject.canBlockchainReportATime["ToTime"] = child2.text.strip()
                if child.tag == "canRoleA":
                    timeControlObject.canRoleA = child.tag.strip()
                    for child2 in child:
                        if child2.tag == "AttributeFromTime":
                            timeControlObject.canRoleATime["FromTime"] = child2.text.strip()
                        if child2.tag == "AttributeToTime":
                            timeControlObject.canRoleATime["ToTime"] = child2.text.strip()
                if child.tag == "canUserA":
                    timeControlObject.canUserA = child.tag.strip()
                    for child2 in child:
                        if child2.tag == "AttributeFromTime":
                            timeControlObject.canUserATime["FromTime"] = child2.text.strip()
                        if child2.tag == "AttributeToTime":
                            timeControlObject.canUserATime["ToTime"] = child2.text.strip()       
    '''print("ipControlObject.IPAddress", ipControlObject.IPAddress)
    print("timeControlObject.canCloudProviderA", timeControlObject.canCloudProviderA)
    print("timeControlObject.canCloudProviderATime", timeControlObject.canCloudProviderATime)
    print("timeControlObject.canVideoDataA", timeControlObject.canVideoDataA)
    print("timeControlObject.canVideoDataATime", timeControlObject.canVideoDataATime)
    print("timeControlObject.canBlockchainGenerationA", timeControlObject.canBlockchainGenerationA)
    print("timeControlObject.canBlockchainGenerationATime", timeControlObject.canBlockchainGenerationATime)
    print("timeControlObject.canBlockchainReportA", timeControlObject.canBlockchainReportA)
    print("timeControlObject.canBlockchainReportATime", timeControlObject.canBlockchainReportATime)
    print("timeControlObject.canRoleA", timeControlObject.canRoleA)
    print("timeControlObject.canRoleATime", timeControlObject.canRoleATime)
    print("timeControlObject.canUserA", timeControlObject.canUserA)
    print("timeControlObject.canUserATime", timeControlObject.canUserATime)
    
    '''
    print("request.remote_addr..............", request.remote_addr)
    if request.remote_addr == ipControlObject.IPAddress:
        return render_template('Login.html', processResult="You Can't Access From this IP Address "+ipControlObject.IPAddress)
    return render_template('Dashboard.html')
@app.route("/ChangePassword")
def changePassword():
    initialize()
    return render_template('ChangePassword.html')

@app.route("/ProcessChangePassword", methods=['POST'])
def processChangePassword():
    initialize()
    oldPassword= request.form['oldPassword']
    newPassword= request.form['newPassword']
    confirmPassword= request.form['confirmPassword']
    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM Users WHERE  emailid = '"+emailid+"' AND password = '"+oldPassword+"'"; 
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    cur1.commit()
    if not row:
        return render_template('ChangePassword.html', msg="Invalid Old Password")
    
    if newPassword.strip() != confirmPassword.strip() :
       return render_template('ChangePassword.html', msg="New Password and Confirm Password are NOT same")
    
    
    sqlcmd1 = "UPDATE Users SET password = '"+newPassword+"' WHERE emailid = '"+emailid+"'"; 
    cur1.execute(sqlcmd1)
    cur1.commit()
    return render_template('ChangePassword.html', msg="Password Changed Successfully")


@app.route("/ForgotPassword")
def ForgotPassword():
    initialize()
    return render_template('ForgotPassword.html')

@app.route("/processRequestPassword", methods=['POST'])
def processRequestPassword():
    initialize()
    emailid = request.form['emailid']
    
    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM Users WHERE emailid = '"+emailid+"'"; 
    print(sqlcmd1)
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    cur1.commit()
    if not row:
        conn1.close()
        return render_template('ForgotPassword.html', processResult="Invalid Userid ")
    
    msg = MIMEText("Hi Admin, Kindly send the password for emailID "+emailid)
    msg['Subject'] = "Request For Password"
            
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.ehlo()
    s.starttls()
    s.login("mary.ka.brown@gmail.com", "JAMMail123@") 
    s.sendmail("mary.ka.brown@gmail.com", "kannan@wisensoft.com", msg.as_string()) 
    s.quit() 
    return render_template('Login.html', processResult="Request Sent ")

@app.route("/Dashboard")
def dashboard():
    initialize()
    return render_template('Dashboard.html')




'''
    Cloud Provider Data Operation Start
'''

def processRole(optionID):
    if optionID == 2 :
        if roleObject.canCloudProvider == False :
            return False
    if optionID == 3 :
        if roleObject.canVideoData == False :
            return False
    if optionID == 4 :
        if roleObject.canBlockchainGeneration == False :
            return False
    if optionID == 5 :
        if roleObject.canBlockchainReport == False :
            return False
    if optionID == 6 :
        if roleObject.canRole == False :
            return False
    if optionID == 7 :
        if roleObject.canUser == False :
            return False
    return True


@app.route("/CloudProviderDataListing")
def CloudProviderDataListing():
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(2)

    if canRole == False:
        errorResult = "You Don't Have Permission to Access Cloud Provider"
        errType="Error"
        return redirect(url_for('Error'))

    if timeControlObject.canCloudProviderA != "":
        todayA = datetime.today()
        
        
        ftime = time.strptime(timeControlObject.canCloudProviderATime["FromTime"], '%H:%M')
        ttime = time.strptime(timeControlObject.canCloudProviderATime["ToTime"], '%H:%M')
        
        todate = datetime(todayA.year, todayA.month, todayA.day, ttime.tm_hour, ttime.tm_min, 0)
        if ftime.tm_hour > ttime.tm_hour :
            todate +=  timedelta(days = 1)
            todate = todate.replace(hour=ttime.tm_hour)
            #todate = datetime.datetime(todate.year, todate.month, todate.day+1, ttime.tm_hour, ttime.tm_minute, 0)
        
        fromdate = datetime(todate.year, todate.month, todayA.day, ftime.tm_hour, ftime.tm_min, 0)
        if fromdate < todayA and todate > todayA:
            errorResult = "You Can't Access Between "+str(fromdate)+" and "+str(todate)
            errType="Error"
            return redirect(url_for('Error'))
       

    
    initialize()
    searchData = request.args.get('searchData')
    print(searchData)
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM CloudProviderData WHERE cloudProviderName LIKE '"+searchData+"%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = CloudProviderDataModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3])
        
        records.append(row)
    
    return render_template('CloudProviderDataListing.html', records=records, searchData=searchData)

@app.route("/CloudProviderDataOperation")
def cloudProviderDataOperation():
    
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(2)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access Cloud Provider"
        errType="Error"
        return redirect(url_for('Error'))
    
    
    initialize()
    operation = request.args.get('operation')
    unqid = ""
    cloudProvider = CloudProviderDataModel(0, "", 0, 0)
    row = None
    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM CloudProviderData WHERE cloudProviderID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row = CloudProviderDataModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3])
    
    
    return render_template('CloudProviderDataOperation.html', row = row, operation=operation )


@app.route("/ProcessCloudProviderDataOperation", methods=['POST'])
def ProcessCloudProviderDataOperation():
    
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(2)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access Cloud Provider"
        errType="Error"
        return redirect(url_for('Error'))
    
    
    initialize()
    print("ProcessCloudProviderData")
    cloudProviderName = request.form['cloudProviderName']
    storageSpace = request.form['storageSpace']
    usageCostPerGB = request.form['usageCostPerGB']
    
    operation = request.form['operation']
    unqid = request.form['unqid'].strip()
    print(operation)
    conn3 = pypyodbc.connect(connString, autocommit=True)
    cur3 = conn3.cursor()
    
    
    sqlcmd = ""
    if operation == "Create" :
        sqlcmd = "INSERT INTO CloudProviderData (cloudProviderName,  storageSpace, usageCostPerGB) VALUES ('"+cloudProviderName+"', '"+storageSpace+"', '"+usageCostPerGB+"')"
        
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE CloudProviderData SET cloudProviderName = '"+cloudProviderName+"',  storageSpace = '"+storageSpace+"', usageCostPerGB = '"+usageCostPerGB+"' WHERE cloudProviderID = '"+unqid+"'" 
    if operation == "Delete" :
        sqlcmd = "DELETE FROM CloudProviderData WHERE cloudProviderID = '"+unqid+"'" 
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Error')) 
    cur3.execute(sqlcmd)
    cur3.commit()
    
    return redirect(url_for('CloudProviderDataListing')) 
    #return render_template('CloudProviderDataListing.html',  msg="Cloud Provider Information Successfully Created")

'''
    Cloud Provider Data Operation End
'''





'''
    Role Operation Start
'''

@app.route("/RoleListing")
def RoleListing():
    
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(6)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access Role"
        errType="Error"
        return redirect(url_for('Error'))
    
    if timeControlObject.canRoleA != "":
        todayA = datetime.today()
        
        
        ftime = time.strptime(timeControlObject.canRoleATime["FromTime"], '%H:%M')
        ttime = time.strptime(timeControlObject.canRoleATime["ToTime"], '%H:%M')
        
        todate = datetime(todayA.year, todayA.month, todayA.day, ttime.tm_hour, ttime.tm_min, 0)
        if ftime.tm_hour > ttime.tm_hour :
            todate +=  timedelta(days = 1)
            todate = todate.replace(hour=ttime.tm_hour)
            #todate = datetime.datetime(todate.year, todate.month, todate.day+1, ttime.tm_hour, ttime.tm_minute, 0)
        
        fromdate = datetime(todate.year, todate.month, todayA.day, ftime.tm_hour, ftime.tm_min, 0)
        if fromdate < todayA and todate > todayA:
            errorResult = "You Can't Access Between "+str(fromdate)+" and "+str(todate)
            errType="Error"
            return redirect(url_for('Error'))
       
    
    initialize()
    searchData = request.args.get('searchData')
    print(searchData)
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM Role WHERE roleName LIKE '"+searchData+"%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = RoleModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6],dbrow[7])
        
        records.append(row)
    
    return render_template('RoleListing.html', records=records, searchData=searchData)

@app.route("/RoleOperation")
def RoleOperation():
    
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(6)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access Role"
        errType="Error"
        return redirect(url_for('Error'))
    
    initialize()
    operation = request.args.get('operation')
    unqid = ""
    row = RoleModel(0, "",0,0,0,0,0,0)
    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        
        
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM Role WHERE roleID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row = RoleModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6],dbrow[7])
        
    return render_template('RoleOperation.html', row = row, operation=operation )


@app.route("/ProcessRoleOperation", methods=['POST'])
def ProcessRoleOperation():
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(6)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access Role"
        errType="Error"
        return redirect(url_for('Error'))
    
    
    initialize()
    print("ProcessRole")
    
    operation = request.form['operation']
    if operation != "Delete" :
        roleName = request.form['roleName']
    
    
    unqid = request.form['unqid'].strip()
    print(operation)
    conn3 = pypyodbc.connect(connString, autocommit=True)
    cur3 = conn3.cursor()
    
    canCloudProvider = 0
    canVideoData = 0
    canBlockchainReport = 0
    canBlockchainGeneration = 0
    canRole = 0
    canUser = 0
    print("request.form.get('canCloudProvider')----------------------------------------------------", request.form.get("canCloudProvider"))
    if request.form.get("canCloudProvider") != None :
        canCloudProvider = 1
    if request.form.get("canVideoData") != None :
        canVideoData = 1
    if request.form.get("canBlockchainReport") != None :
        canBlockchainReport = 1
    if request.form.get("canBlockchainGeneration") != None :
        canBlockchainGeneration = 1
    if request.form.get("canRole") != None :
        canRole = 1
    if request.form.get("canUser") != None :
        canUser = 1
    sqlcmd = ""
    if operation == "Create" :
        sqlcmd = "INSERT INTO Role (roleName, canCloudProvider, canVideoData, canBlockchainGeneration, canBlockchainReport, canRole, canUser) VALUES ('"+roleName+"', '"+str(canCloudProvider)+"', '"+str(canVideoData)+"', '"+str(canBlockchainGeneration)+"', '"+str(canBlockchainReport)+"', '"+str(canRole)+"', '"+str(canUser)+"')"
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE Role SET roleName = '"+roleName+"', canCloudProvider = '"+str(canCloudProvider)+"', canVideoData = '"+str(canVideoData)+"', canBlockchainGeneration = '"+str(canBlockchainGeneration)+"', canBlockchainReport = '"+str(canBlockchainReport)+"', canRole = '"+str(canRole)+"', canUser = '"+str(canUser)+"' WHERE roleID = '"+unqid+"'" 
    if operation == "Delete" :
        conn4 = pypyodbc.connect(connString, autocommit=True)
        cur4 = conn4.cursor()
        sqlcmd4 = "SELECT roleID FROM Users WHERE roleID = '"+unqid+"'" 
        dbrow4 = cur4.fetchone()
        if dbrow4:
            errorResult = "You Can't Delete this Role Since it Available in Users Table"
            errType="Error"
            return redirect(url_for('Error')) 
        
        sqlcmd = "DELETE FROM Role WHERE roleID = '"+unqid+"'" 
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Error')) 
    cur3.execute(sqlcmd)
    cur3.commit()
    
    return redirect(url_for('RoleListing')) 
    #return render_template('RoleListing.html',  msg="Cloud Provider Information Successfully Created")



'''
    Role Operation End
'''













'''
    Users Operation Start
'''

@app.route("/UserListing")
def UserListing():

    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(7)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType="Error"
        return redirect(url_for('Error'))
    
    
    if timeControlObject.canUserA != "":
        todayA = datetime.today()
        
        
        ftime = time.strptime(timeControlObject.canUserATime["FromTime"], '%H:%M')
        ttime = time.strptime(timeControlObject.canUserATime["ToTime"], '%H:%M')
        
        todate = datetime(todayA.year, todayA.month, todayA.day, ttime.tm_hour, ttime.tm_min, 0)
        if ftime.tm_hour > ttime.tm_hour :
            todate +=  timedelta(days = 1)
            todate = todate.replace(hour=ttime.tm_hour)
            #todate = datetime.datetime(todate.year, todate.month, todate.day+1, ttime.tm_hour, ttime.tm_minute, 0)
        
        fromdate = datetime(todate.year, todate.month, todayA.day, ftime.tm_hour, ftime.tm_min, 0)
        if fromdate < todayA and todate > todayA:
            errorResult = "You Can't Access Between "+str(fromdate)+" and "+str(todate)
            errType="Error"
            return redirect(url_for('Error'))
        
        
    initialize()
    searchData = request.args.get('searchData')
    print(searchData)
    if searchData == None:
        searchData = "";
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd1 = "SELECT userID, userName, emailID, roleID FROM Users WHERE UserName LIKE '"+searchData+"%'"
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        
        conn3 = pypyodbc.connect(connString, autocommit=True)
        cursor3 = conn3.cursor()
        print("dbrow[3]", dbrow[3])
        temp = str(dbrow[3])
        sqlcmd3 = "SELECT * FROM Role WHERE roleID = '"+temp+"'"
        print(sqlcmd3)
        cursor3.execute(sqlcmd3)
        rolerow = cursor3.fetchone()
        
        roleObj = None
        if rolerow:
           roleObj = RoleModel(rolerow[0], rolerow[1])
        else:
           print("Role Row is Not Available")
        
        row = UserModel(dbrow[0],dbrow[1],dbrow[2],roleObj)
        
        records.append(row)
    cursor.close()
    conn.close()
    return render_template('UserListing.html', records=records, searchData=searchData)

@app.route("/UserOperation")
def UserOperation():

    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(7)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType="Error"
        return redirect(url_for('Error'))
    
    
    initialize()
    operation = request.args.get('operation')
    unqid = ""
    row = UserModel(0, "", "", 0)
    rolesDDList = []
    
    conn4 = pypyodbc.connect(connString, autocommit=True)
    cursor4 = conn4.cursor()
    sqlcmd4 = "SELECT * FROM Role"
    cursor4.execute(sqlcmd4)
    while True:
        roleDDrow = cursor4.fetchone()
        if not roleDDrow:
            break
        
        roleDDObj = RoleModel(roleDDrow[0], roleDDrow[1])
        rolesDDList.append(roleDDObj)
    
    if operation != "Create" :
        
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT userID, userName, emailID, roleID FROM Users WHERE userID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            conn3 = pypyodbc.connect(connString, autocommit=True)
            cursor3 = conn3.cursor()
            print("dbrow[3]", dbrow[3])
            temp = str(dbrow[3])
            sqlcmd3 = "SELECT * FROM Role WHERE roleID = '"+temp+"'"
            print("sqlcmd3", sqlcmd3)
            cursor3.execute(sqlcmd3)
            rolerow = cursor3.fetchone()
        
            roleObj = None
            if rolerow:
                roleObj = RoleModel(rolerow[0], rolerow[1])
           
            row = UserModel(dbrow[0], dbrow[1], dbrow[2], roleObj)
            
        
    return render_template('UserOperation.html', row = row, operation=operation, rolesDDList=rolesDDList )


@app.route("/ProcessUserOperation", methods=['POST'])
def ProcessUserOperation():
    
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(7)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType="Error"
        return redirect(url_for('Error'))
    
    
    initialize()
    print("ProcessUserOperation")
    operation = request.form['operation']
    
    if operation != "Delete" :
        userName = request.form['userName']
        emailID = request.form['emailID']
        roleID = request.form['roleID']
    
    
    unqid = request.form['unqid'].strip()
    print(operation)
    conn3 = pypyodbc.connect(connString, autocommit=True)
    cur3 = conn3.cursor()
    
    
    sqlcmd = ""
    if operation == "Create" :
        sqlcmd = "INSERT INTO Users (userName, emailID, roleID) VALUES ('"+userName+"', '"+emailID+"', '"+roleID+"')"
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE Users SET UserName = '"+userName+"', emailID = '"+emailID+"', roleID = '"+roleID+"' WHERE userID = '"+unqid+"'" 
    if operation == "Delete" :
        sqlcmd = "DELETE FROM Users WHERE UserID = '"+unqid+"'" 
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Error')) 
    cur3.execute(sqlcmd)
    cur3.commit()
    
    return redirect(url_for('UserListing')) 
    #return render_template('UserListing.html',  msg="Cloud Provider Information Successfully Created")



'''
    Users Operation End
'''





'''
    Video Data Operation Start
'''

@app.route("/VideoDataListing")
def VideoDataListing():
    
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    
    
    if timeControlObject.canVideoDataA != "":
        todayA = datetime.today()
        
        
        ftime = time.strptime(timeControlObject.canVideoDataATime["FromTime"], '%H:%M')
        ttime = time.strptime(timeControlObject.canVideoDataATime["ToTime"], '%H:%M')
        
        todate = datetime(todayA.year, todayA.month, todayA.day, ttime.tm_hour, ttime.tm_min, 0)
        if ftime.tm_hour > ttime.tm_hour :
            todate +=  timedelta(days = 1)
            todate = todate.replace(hour=ttime.tm_hour)
            #todate = datetime.datetime(todate.year, todate.month, todate.day+1, ttime.tm_hour, ttime.tm_minute, 0)
        
        fromdate = datetime(todate.year, todate.month, todayA.day, ftime.tm_hour, ftime.tm_min, 0)
        if fromdate < todayA and todate > todayA:
            errorResult = "You Can't Access Between "+str(fromdate)+" and "+str(todate)
            errType="Error"
            return redirect(url_for('Error'))
        
        
    canRole = processRole(3)
    print("canRole-------------------------------", canRole)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access Video Data"
        errType="Error"
        return redirect(url_for('Error'))
    
    initialize()
    searchData = request.args.get('searchData')
    print(searchData)
    if searchData == None:
        searchData = "";
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd1 = "SELECT videoID, author, keywords, cloudProviderID, isDownloadedToServer, videoFileName FROM VideoData WHERE author LIKE '"+searchData+"%'"
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        
        conn3 = pypyodbc.connect(connString, autocommit=True)
        cursor3 = conn3.cursor()
        print("dbrow[3]", dbrow[3])
        temp = str(dbrow[3])
        sqlcmd3 = "SELECT * FROM CloudProviderData WHERE cloudProviderID = '"+temp+"'"
        print(sqlcmd3)
        cursor3.execute(sqlcmd3)
        cloudProviderRow = cursor3.fetchone()
        
        cloudProviderObj = None
        if cloudProviderRow:
           cloudProviderObj = CloudProviderDataModel(cloudProviderRow[0], cloudProviderRow[1])
        else:
           print("Cloud Provider Row is Not Available")
        
        row = VideoDataModel(dbrow[0],dbrow[1],dbrow[2],cloudProviderModel=cloudProviderObj, isDownloadedToServer=dbrow[4], videoFileName=dbrow[5])
        
        records.append(row)
    cursor.close()
    conn.close()
    return render_template('VideoDataListing.html', records=records, searchData=searchData)

@app.route("/VideoDataOperation")
def VideoDataOperation():
    
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(3)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access Video Data"
        errType="Error"
        return redirect(url_for('Error'))
    
    
    initialize()
    operation = request.args.get('operation')
    print("operation", operation)
    unqid = ""
    row = VideoDataModel(0, "")
    cloudProviderDDList = []
    
    conn4 = pypyodbc.connect(connString, autocommit=True)
    cursor4 = conn4.cursor()
    sqlcmd4 = "SELECT * FROM CloudProviderData"
    cursor4.execute(sqlcmd4)
    while True:
        cloudProviderDDrow = cursor4.fetchone()
        if not cloudProviderDDrow:
            break
        print("cloudProviderDDrow", cloudProviderDDrow[1])
        cloudProviderDDObj = CloudProviderDataModel(cloudProviderDDrow[0], cloudProviderDDrow[1])
        cloudProviderDDList.append(cloudProviderDDObj)
    
    if operation != "Create" :
        
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM VideoData WHERE videoID = '"+unqid+"'"
        print("sqlcmd1", sqlcmd1)
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            conn3 = pypyodbc.connect(connString, autocommit=True)
            cursor3 = conn3.cursor()
            print("dbrow[8]", dbrow[8])
            temp = str(dbrow[8])
            sqlcmd3 = "SELECT * FROM CloudProviderData WHERE cloudProviderID = '"+temp+"'"
            print("sqlcmd3", sqlcmd3)
            cursor3.execute(sqlcmd3)
            cloudproviderrow = cursor3.fetchone()
            cloudproviderObj = None
            if cloudproviderrow:
                cloudproviderObj = CloudProviderDataModel(cloudproviderrow[0], cloudproviderrow[1])
            row = VideoDataModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], dbrow[5],dbrow[6], dbrow[7],cloudProviderModel = cloudproviderObj)
            
    print("cloudProviderDDObj", len(cloudProviderDDList))    
    return render_template('VideoDataOperation.html', row = row, operation=operation, cloudProviderDDList=cloudProviderDDList )


@app.route("/ProcessVideoDataOperation", methods=['POST'])
def ProcessVideoDataOperation():
    
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(3)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access Video Data"
        errType="Error"
        return redirect(url_for('Error'))
    
    
    initialize()
    print("ProcessVideoDataOperation")
    operation = request.form['operation']
    if operation != "Delete" :
        author = request.form['author']
        keywords = request.form['keywords']
        cloudProviderID = request.form['cloudProviderID']
        mediaFormat = request.form['mediaFormat']
        closedCaption = request.form['closedCaption']
        contentData = request.form['contentData']
    
    unqid = request.form['unqid'].strip()
    fileName = ""
    fileSize = 0
    if len(request.files) != 0 :
        file = request.files['filetoupload']
        if file.filename != '':
            fileName = file.filename
            f = os.path.join('static', fileName)
            file.save(f)
            blob = request.files['filetoupload']
            blob.seek(0,2)
            fileSize = blob.tell()
            print("fileSize ......................................................................", fileSize)
            #fileSize = os.stat('UPLOADED_FILES/'+fileName).st_size
            ftp = ftplib.FTP('101.99.74.37', 'Student1','3Aj73#lc')
            #ftp.login(user=, passwd = )
            print("fileName", fileName)
            ftp.storbinary('STOR '+fileName, open('static/'+fileName, 'rb'))   # send the file                                   # close file and FTP
            ftp.quit()
            os.remove('static/'+fileName)
    print(3)
    conn3 = pypyodbc.connect(connString, autocommit=True)
    cur3 = conn3.cursor()
    
    print(4)
    sqlcmd = ""
    if operation == "Create" :
        sqlcmd = "INSERT INTO VideoData (author, keywords, mediaFormat, closedCaption, contentData, cloudProviderID, fileSize, videoFileName, isDownloadedToServer) VALUES ('"+author+"', '"+keywords+"', '"+mediaFormat+"', '"+closedCaption+"', '"+contentData+"', '"+cloudProviderID+"', '"+str(fileSize)+"', '"+fileName+"', 0)"
        
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE VideoData SET author = '"+author+"', keywords = '"+keywords+"', mediaFormat = '"+mediaFormat+"', closedCaption = '"+closedCaption+"', contentData = '"+contentData+"', cloudProviderID = '"+cloudProviderID+"', fileSize= '"+str(fileSize)+"', videoFileName = '"+fileName+"' WHERE videoID = '"+unqid+"'" 
    if operation == "Delete" :
        sqlcmd = "DELETE FROM VideoData WHERE videoID = '"+unqid+"'" 
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Error')) 
    cur3.execute(sqlcmd)
    cur3.commit()
    
    return redirect(url_for('VideoDataListing')) 
    #return render_template('UserListing.html',  msg="Cloud Provider Information Successfully Created")


@app.route("/FTPDownload")
def FTPDownload():
    global errorResult, errType
    unqid = request.args.get('unqid').strip()
    
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT videoFileName FROM VideoData WHERE videoID = '"+unqid+"'"
    cursor.execute(sqlcmd1)
    dbrow = cursor.fetchone()
    if dbrow:
        fileName = dbrow[0]
        
        conn3 = pypyodbc.connect(connString, autocommit=True)
        cur3 = conn3.cursor()
        sqlcmd = ""
        sqlcmd = "UPDATE VideoData SET isDownloadedToServer = 1 WHERE videoID = '"+unqid+"'" 
        cur3.execute(sqlcmd)
        cur3.commit()
        ftp = ftplib.FTP('101.99.74.37', 'Student1','3Aj73#lc')
        print("fileName", fileName)
        ftp.retrbinary('RETR '+fileName, open('static/UPLOADED_FILES/'+fileName, 'wb').write, 1024*1024)   # send the file                                   # close file and FTP
        ftp.quit()
        
            
    errorResult = "Downloaded to Server"
    errType="Success"
    return redirect(url_for('Error'))

'''
    Video Upload Operation End
'''

@app.route("/Error")
def Error():
    print("errorResult+++++++++++++++++++++++++++++++++", errorResult)
    return render_template('Error.html', errType=errType, errorResult = errorResult)

    
@app.route("/BlockChainGeneration")
def BlockChainGeneration():
    
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(4)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access Blockchain Generation"
        errType="Error"
        return redirect(url_for('Error'))
    
    
    if timeControlObject.canBlockchainGenerationA != "":
        todayA = datetime.today()
        
        
        ftime = time.strptime(timeControlObject.canBlockchainGenerationATime["FromTime"], '%H:%M')
        ttime = time.strptime(timeControlObject.canBlockchainGenerationATime["ToTime"], '%H:%M')
        
        todate = datetime(todayA.year, todayA.month, todayA.day, ttime.tm_hour, ttime.tm_min, 0)
        if ftime.tm_hour > ttime.tm_hour :
            todate +=  timedelta(days = 1)
            todate = todate.replace(hour=ttime.tm_hour)
            #todate = datetime.datetime(todate.year, todate.month, todate.day+1, ttime.tm_hour, ttime.tm_minute, 0)
        
        fromdate = datetime(todate.year, todate.month, todayA.day, ftime.tm_hour, ftime.tm_min, 0)
        if fromdate < todayA and todate > todayA:
            errorResult = "You Can't Access Between "+str(fromdate)+" and "+str(todate)
            errType="Error"
            return redirect(url_for('Error'))
        
    
    initialize()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT COUNT(*) FROM VideoData WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd)
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksCreated = dbrow[0]
    
    sqlcmd = "SELECT COUNT(*) FROM VideoData WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null"
    cursor.execute(sqlcmd)
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksNotCreated = dbrow[0]
    return render_template('BlockChainGeneration.html', blocksCreated = blocksCreated, blocksNotCreated = blocksNotCreated)


@app.route("/ProcessBlockchainGeneration", methods=['POST'])
def ProcessBlockchainGeneration():
    
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(4)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access Blockchain Generation"
        errType="Error"
        return redirect(url_for('Error'))
    
    
    initialize()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT COUNT(*) FROM VideoData WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd)
    blocksCreated = 0
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksCreated = dbrow[0]
    
    prevHash = ""
    print("blocksCreated", blocksCreated)
    if blocksCreated != 0 :
        connx = pypyodbc.connect(connString, autocommit=True)
        cursorx = connx.cursor()
        sqlcmdx = "SELECT * FROM VideoData WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null ORDER BY VideoID"
        cursorx.execute(sqlcmdx)
        dbrowx = cursorx.fetchone()
        print(2)
        if dbrowx:
            videoid = dbrowx[0]
            conny = pypyodbc.connect(connString, autocommit=True)
            cursory = conny.cursor()
            sqlcmdy = "SELECT Hash FROM VideoData WHERE videoID < '"+str(videoid)+"' ORDER BY VideoID DESC"
            cursory.execute(sqlcmdy)
            dbrowy = cursory.fetchone()
            if dbrowy:
                print(3)
                prevHash = dbrowy[0]
                print("prevHash1111", prevHash)
            cursory.close()
            conny.close()
        cursorx.close()
        connx.close()
    print("prevHash1111", prevHash)
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT * FROM VideoData WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null ORDER BY VideoID"
    cursor.execute(sqlcmd)
    
    while True:
        sqlcmd1 = ""
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        unqid = str(dbrow[0])
        
        block_serialized = json.dumps(dbrow[1]+" "+dbrow[2], sort_keys=True).encode('utf-8')
        block_hash = hashlib.sha256(block_serialized).hexdigest()
  
        conn1 = pypyodbc.connect(connString, autocommit=True)
        cursor1 = conn1.cursor()
        sqlcmd1 = "UPDATE VideoData SET isBlockChainGenerated = 1, hash = '"+block_hash+"', prevHash = '"+prevHash+"' WHERE videoID = '"+unqid+"'"
        cursor1.execute(sqlcmd1)
        cursor1.close()
        conn1.close()
        prevHash = block_hash
    return render_template('BlockchainGenerationResult.html')


@app.route("/BlockChainReport")
def BlockChainReport():
    
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(5)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access Blockchain Report"
        errType="Error"
        return redirect(url_for('Error'))
    
    if timeControlObject.canBlockchainReportA != "":
        todayA = datetime.today()
        
        
        ftime = time.strptime(timeControlObject.canBlockchainReportATime["FromTime"], '%H:%M')
        ttime = time.strptime(timeControlObject.canBlockchainReportATime["ToTime"], '%H:%M')
        
        todate = datetime(todayA.year, todayA.month, todayA.day, ttime.tm_hour, ttime.tm_min, 0)
        if ftime.tm_hour > ttime.tm_hour :
            todate +=  timedelta(days = 1)
            todate = todate.replace(hour=ttime.tm_hour)
            #todate = datetime.datetime(todate.year, todate.month, todate.day+1, ttime.tm_hour, ttime.tm_minute, 0)
        
        fromdate = datetime(todate.year, todate.month, todayA.day, ftime.tm_hour, ftime.tm_min, 0)
        if fromdate < todayA and todate > todayA:
            errorResult = "You Can't Access Between "+str(fromdate)+" and "+str(todate)
            errType="Error"
            return redirect(url_for('Error'))
        

    initialize()
    conn3 = pypyodbc.connect(connString, autocommit=True)
    cur3 = conn3.cursor()

    sqlcmd = "SELECT videoID, author, keywords, fileSize, mediaFormat, closedCaption, videoFileName, hash, prevHash FROM VideoData ORDER BY videoID"
    print(sqlcmd)
    cur3.execute(sqlcmd)

    records = []
    while True:
        row = cur3.fetchone()
        if row:

            pmodel = VideoDataModel(row[0], author=row[1], keywords=row[2], fileSize=row[3], mediaFormat=row[4],
                                    closedCaption=row[5], videoFileName=row[6], hash=row[7], prevHash=row[8])
            records.append(pmodel)
        else:
            break

    return render_template('BlockChainReport.html', records=records)

from CloudReportModel import CloudReportModel
import flask_excel as excel
excel.init_excel(app) 

@app.route("/CloudReportGeneration")
def CloudReportGeneration():
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd1 = "SELECT cloudProviderID, SUM(fileSize) FROM VideoData GROUP BY cloudProviderID ORDER BY cloudProviderID"
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        print(1)
        conn3 = pypyodbc.connect(connString, autocommit=True)
        cursor3 = conn3.cursor()

        temp = str(dbrow[0])
        sqlcmd3 = "SELECT cloudProviderName, storageSpace, usageCostPerGB FROM CloudProviderData WHERE cloudProviderID = '"+temp+"'"
        print(sqlcmd3)
        cursor3.execute(sqlcmd3)
        cloudProviderRow = cursor3.fetchone()
        if cloudProviderRow:
            print(1)
            cloudReportModelObj = CloudReportModel()
            cloudReportModelObj.cloudProviderName = cloudProviderRow[0]
            cloudReportModelObj.storageSpace = float(cloudProviderRow[1])
            cloudReportModelObj.usageCostPerGB = float(cloudProviderRow[2])
            totalUsedStorage = dbrow[1]
            if totalUsedStorage > 0:
                print(1)
                totalUsedStorage = totalUsedStorage / (1024 * 1024 * 1024)
                print(2)
                totalUsageCost = totalUsedStorage * float(cloudProviderRow[2])
                print(3)
                cloudReportModelObj.totalUsedStorage = totalUsedStorage
                print(4)
                cloudReportModelObj.totalUsageCost = totalUsageCost
            
            
            reprow = []
            reprow.append(cloudReportModelObj.cloudProviderName)
            reprow.append(cloudReportModelObj.storageSpace)
            reprow.append(cloudReportModelObj.usageCostPerGB)
            reprow.append(cloudReportModelObj.totalUsedStorage)
            reprow.append(cloudReportModelObj.totalUsageCost)
            records.append(reprow)
            print(">>>>>>>qw  dsad  w>>>>>>>>>>>>asdsdsadas>>", "%.5f" % (cloudReportModelObj.totalUsedStorage) , "%.5f" % cloudReportModelObj.totalUsageCost)
    cursor.close()
    conn.close()
    return excel.make_response_from_query_sets(records, ['Cloud Provider Name', 'Available Space', 'Cost Per GB', 'Used Space', "Usage Cost"], "xls", file_name="export_data")


if __name__=='__main__':
    app.run()
    


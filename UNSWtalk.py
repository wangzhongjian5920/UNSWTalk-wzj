#!/usr/bin/python3

# written by andrewt@cse.unsw.edu.au October 2017
# as a starting point for COMP[29]041 assignment 2
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/

import os,re
from flask import Flask, render_template, session, make_response
import sqlite3
from flask import g
from flask import request
from flask import Flask, url_for,redirect
import datetime




students_dir = "static/dataset-medium"

app = Flask(__name__)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

#==================================================================================
#                                     helper function
#==================================================================================

def connect_db():
    return sqlite3.connect('assn2.db')

@app.before_request
def before_request():
    g.db = connect_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


#==================================================================================
#                                     main function
#==================================================================================


#main page for user, if not login , will ask for login
#if log in, then show list of firends post
#var for this page should be list of post
@app.route('/', methods=['GET','POST'])
def begin():
    zid = request.cookies.get('zid')
    if zid == None:
        return render_template('login.html')
    postList,commentList,replyList = getPostByID(zid)
    return render_template('home.html', postList=postList,commentList=commentList,replyList=replyList)


#jump to the page
@app.route('/createAccount', methods=['GET','POST'])
def createAccount():
    return render_template('createAccount.html')

@app.route('/deleteUser', methods=['GET','POST'])
def deleteUser():
    ZID = request.cookies.get('zid')
    print(ZID)
    g.db.execute('delete from Users WHERE ZID = ?', [ZID])
    g.db.execute('delete from Posts WHERE fromID = ?', [ZID])
    g.db.execute('delete from courses WHERE ZID = ?', [ZID])
    g.db.execute('delete from friends WHERE ZID = ? or friend = ?', [ZID,ZID])
    g.db.commit()
    session['logged_in'] = False
    resp = make_response(redirect(url_for('begin')))
    resp.set_cookie('zid', "")
    return resp


@app.route('/createDone', methods=['GET','POST'])
def createDone():
    ZID = request.form.get('ZID')
    password = request.form.get('password')
    full_name = request.form.get('name')
    birthday = request.form.get('birthday')
    home_suburb = request.form.get('address')
    program = request.form.get('program')
    email = request.form.get('email')
    intro = request.form.get('details')
    print(ZID)
    print(password)
    print(full_name)
    print(birthday)
    print(home_suburb)
    print(program)
    print(email)
    print(intro)
    if intro == "":
        g.db.execute('INSERT INTO Users (ZID,password,full_name,birthday,email,program,home_suburb) VALUES (?,?,?,?,?,?,?)',
                     [ZID,password,full_name,birthday,email,program,home_suburb])
        g.db.commit()
    else:
        g.db.execute('INSERT INTO Users (ZID,password,full_name,birthday,email,program,home_suburb,intro) VALUES (?,?,?,?,?,?,?,?)',
                     [ZID,password,full_name,birthday,email,program,home_suburb,intro])
        g.db.commit()

    return redirect(url_for('login'))

#log in , once user log in, then jump to the home page, show the post of his friends
#path: /login set the cookie zid = zid
@app.route('/login', methods=['GET','POST'])
def login():
    zid = request.form.get('zid','')
    password = request.form.get('password','')
    for user in query_db('select * from Users where ZID = ?',[zid]):
        if user['password'] == password:
            session['logged_in'] = True
            resp = make_response(redirect(url_for('begin')))
            resp.set_cookie('zid', zid)
            return resp
        else:
            return render_template('login.html',error = "wrong zid or password")
    return render_template('login.html')

#log in , once user log in, then jump to the home page, show the post of his friends
#path: /login
@app.route('/logout')
def logout():
    session['logged_in'] = False
    resp = make_response(redirect(url_for('begin')))
    resp.set_cookie('zid', "")
    return resp


#get the cookie for user,
#TODO: need to improve more details
@app.route('/myProfile', methods=['GET','POST'])
def myProfile():
    va = request.cookies.get('zid')
    if va == "":
        return render_template('login.html')
    else:
        details_photo = "../" + students_dir + "/" + va + "/img.jpg"
        zid = getUserProfile(va)[0].get('ZID')
        return_name = getUserProfile(va)[0].get('full_name')
        return_home = getUserProfile(va)[0].get('home_suburb')
        return_program = getUserProfile(va)[0].get('program')
        return_birthday = getUserProfile(va)[0].get('birthday')
        return_intro = getUserProfile(va)[0].get('intro')
        postList= getUserPost(va)
        friend = getFriendByID(va)
        return render_template('userProfile.html', name=return_name, photo=details_photo,
                               home=return_home, program=return_program, friend=friend,
                               birthday=return_birthday, zid=zid, postList=postList,own="True",intro=return_intro)



#user profile page path: /zXXXXXX
@app.route('/<var>',methods=['GET','POST'])
def product(var):
    userID = request.cookies.get('zid')
    va = var.strip()
    details_photo = "../"+students_dir+"/"+va+"/img.jpg"
    print(userID)
    print(va)
    if userID == va:
        own = "True"
    else:
        own = "False"
    zid = getUserProfile(va)[0].get('ZID')
    return_name = getUserProfile(va)[0].get('full_name')
    return_home = getUserProfile(va)[0].get('home_suburb')
    return_program = getUserProfile(va)[0].get('program')
    return_birthday = getUserProfile(va)[0].get('birthday')
    return_intro = getUserProfile(va)[0].get('intro')
    state = checkFriendRe(userID,va)
    postList = getUserPost(va)
    friend = getFriendByID(va)
    return render_template('userProfile.html', name=return_name, photo=details_photo,
                           home=return_home,program=return_program, friend=friend,
                           birthday=return_birthday, zid=zid,postList=postList,state=state,userID=userID,own=own,intro=return_intro)


#search apge to search the name and post
@app.route('/search', methods=['GET','POST'])
def search():
    return render_template('show_entries.html')


#jump to the page
@app.route('/editProfile', methods=['GET','POST'])
def editProfile():
    return render_template('editProfile.html')


@app.route('/updateProfile', methods=['GET','POST'])
def updateProfile():
    #TODO:update the database, then jump back to myprofile
    userID = request.cookies.get('zid')
    password = request.form.get('password')
    full_name = request.form.get('name')
    birthday = request.form.get('birthday')
    address = request.form.get('address')
    program = request.form.get('program')
    email = request.form.get('email')
    intro = request.form.get('details')
    print(userID)
    if password != "":
        g.db.execute('UPDATE Users SET password=? WHERE ZID=?', [password, userID])
        g.db.commit()
    if full_name != "":
        g.db.execute('UPDATE Users SET full_name=? WHERE ZID=?', [full_name, userID])
        g.db.commit()
        print("ful" + full_name)
    if birthday != "":
        g.db.execute('UPDATE Users SET birthday=? WHERE ZID=?', [birthday, userID])
        g.db.commit()
        print(birthday)
    if address != "":
        g.db.execute('UPDATE Users SET home_suburb=? WHERE ZID=?', [address, userID])
        g.db.commit()
        print(address)
    if program != "":
        g.db.execute('UPDATE Users SET program=? WHERE ZID=?', [program, userID])
        g.db.commit()
        print(program)
    if email != "":
        g.db.execute('UPDATE Users SET email=? WHERE ZID=?', [email, userID])
        g.db.commit()
        print(email)
    if intro != "":
        g.db.execute('UPDATE Users SET intro=? WHERE ZID=?', [intro, userID])
        g.db.commit()
        print(intro)
    return redirect(url_for('myProfile'))


#search result of name and post
@app.route('/result', methods=['GET','POST'])
def result():
    select = request.form.get('param','')
    content = request.form.get('q','')
    print(select + " : " + content)
    if select == "name":
        iList = []
        cur = g.db.execute("select ZID,full_name from Users where full_name Like '%" + content + "%' ")
        rv = [dict((cur.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cur.fetchall()]
        for user in rv:
            iList.append(user['ZID']+"\n"+user['full_name'])

        num = iList.__len__()
        return render_template('result.html', select=select, content=content,iList=iList,num=num)
    else:
        iList = []
        cur = g.db.execute("select Posts.message, Posts.posttime,Users.full_name,Users.ZID FROM Posts , Users WHERE "+
                            "Posts.commentID is null AND Posts.replyID is null AND Posts.message like  '%" + content + "%' "+
                           "and Users.ZID=Posts.fromID ORDER BY Posts.posttime DESC")
        rv = [dict((cur.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cur.fetchall()]
        for post in rv:
            time = str(post['posttime']).split("T")
            time[1] = re.sub(r'\+0000', '', time[1])
            time = time[0] + " " + time[1]
            iList.append({
                "poster": post['full_name'],
                "content": post['message'],
                "time": time,
                "id": post['ZID'],
                "photo": "../static/dataset-medium/" + post['ZID'] + "/img.jpg"

            })

        num = iList.__len__()
        return render_template('result.html', select=select, content=content,iList=iList,len=len,num=num)

#get user friendList with relationship
def getFriendByID(id):
    currentUser = request.cookies.get('zid')
    frList = []
    for friend in query_db("select friends.ZID,friends.friend,Users.full_name,Users.ZID from friends,Users where Users.ZID=friends.friend AND friends.ZID=?",[id]):
        if currentUser is not None:
            state = checkFriendRe(currentUser,friend['friend'])
        frList.append({
            "ID":friend['friend'],
            "name":friend['full_name'],
            "state":state,
            "photo":"../static/dataset-medium/"+friend['friend']+"/img.jpg"
        })
    return frList

def getUserPost(id):
    postList = []
    for post in query_db('select ID,message,posttime from Posts '
                         'where '
                         'fromID = ? and zID = ?'
                         'and commentID is null '
                         'and replyID is null ORDER BY posttime DESC',[id,id]):
        time = str(post['posttime']).split("T")
        time[1] = re.sub(r'\+0000','',time[1])
        time = time[0]+" "+time[1]
        postList.append({
            "postID":post['ID'],
            "message":post['message'],
            "time":time
        })

    return postList

def getUserProfile(id):
    users = []
    for user in query_db('select ZID,full_name,birthday,home_suburb,program,intro from Users where ZID=?',[id]):

        users.append({
            "ZID":user['ZID'],
            "full_name":user['full_name'],
            "birthday":user['birthday'],
            "home_suburb": user['home_suburb'],
            "program":user['program'],
            "intro":user['intro']
        })
    return users


#TODO:check the link and add friends
#TODO:right now, it is we can unfollow(delete) and follow(pending add status to 0)
#TODO:we need to check the friend request and change status to 1

#delete friend
@app.route('/deleteFriend', methods=['GET'])
def deleteFriend():
    userid = request.args.get('userid')
    firendid = request.args.get('friendid')
    g.db.execute('delete from friends WHERE ZID = ? AND friend = ?', [userid, firendid])
    g.db.execute('delete from friends WHERE ZID = ? AND friend = ?', [firendid, userid])
    g.db.commit()
    print("delete successfully")

    return redirect(url_for('product',var=firendid))

@app.route('/sendFriendR', methods=['GET'])
def sendFriendR():
    userid = request.args.get('userid')
    firendid = request.args.get('friendid')
    g.db.execute('INSERT INTO friends (ZID,friend,status) VALUES (?,?,?)',[str(userid),str(firendid),1])
    g.db.execute('INSERT INTO friends (ZID,friend,status) VALUES (?,?,?)',[str(firendid),str(userid),1])
    g.db.commit()
    print("pending Successfully")
    #TODO: add from table status as 1
    return redirect(url_for('product',var=firendid))

@app.route('/deletePending', methods=['GET'])
def deletePending():
    userid = request.args.get('userid')
    firendid = request.args.get('friendid')
    g.db.execute('delete from friends WHERE ZID = ? AND friend = ?', [userid, firendid])
    g.db.execute('delete from friends WHERE ZID = ? AND friend = ?', [firendid, userid])
    g.db.commit()
    print("delete pending Successfully")
    return redirect(url_for('product',var=firendid))

#TODO: when we delete the post we also neet to check the post id to find list of comments id
#TODO: delte all of them
@app.route('/deletePost',methods=['GET'])
def deletePost():
    postID = request.args.get('postID')

    commentList = []
    for comment in query_db(
            "select Posts.ID,Users.full_name,Posts.message,Posts.posttime,Users.ZID from Posts,Users Where Posts.commentID = ? and Posts.fromID = Users.ZID ORDER BY Posts.posttime DESC",
            [postID]):
        commentList.append(comment['ID'])

    g.db.execute('delete from Posts WHERE ID = ? or commentID = ?', [postID,postID])
    g.db.commit()

    i = 0
    for i in commentList:
        g.db.execute('delete from Posts WHERE replyID = ?', [i])
        g.db.commit()



    print("delete succuessful")
    return redirect(url_for('myProfile'))

# zid is the id from poster, from id is the coolie zid
@app.route('/makeComment', methods=['GET','POST'])
def makeComment():
    message = request.form.get('comment', '')
    zID = request.form.get('zID', '')
    fromID = request.cookies.get('zid')
    commentID = request.form.get('postID', '')
    now = str(datetime.datetime.now()).split(' ')
    t = now[1].split('.')[0]
    posttime = now[0] + 'T' + t + '+0000'
    ID = g.db.execute('select count(*) from Posts').fetchone()[0]
    g.db.execute('INSERT INTO Posts (ID,zID,fromID,posttime,message,commentID) VALUES (?,?,?,?,?,?)',
                 [ID, zID, fromID, posttime, message,commentID])
    g.db.commit()
    print(zID)
    print(fromID)
    print(message)
    print(commentID)
    print(posttime)
    print(ID)
    return redirect(url_for('begin'))


# zid is the id from poster, from id is the coolie zid
@app.route('/makeReply', methods=['GET','POST'])
def makeReply():
    message = request.form.get('reply', '')
    zID = request.form.get('zID', '')
    fromID = request.cookies.get('zid')
    replyID = request.form.get('commentID', '')
    now = str(datetime.datetime.now()).split(' ')
    t = now[1].split('.')[0]
    posttime = now[0] + 'T' + t + '+0000'
    ID = g.db.execute('select count(*) from Posts').fetchone()[0]
    g.db.execute('INSERT INTO Posts (ID,zID,fromID,posttime,message,replyID) VALUES (?,?,?,?,?,?)',
                 [ID, zID, fromID, posttime, message, replyID])
    g.db.commit()
    print(zID)
    print(fromID)
    print(message)
    print(replyID)
    print(posttime)
    print(ID)
    return redirect(url_for('begin'))

@app.route('/makePost', methods=['GET','POST'])
def makePost():
    message = request.form.get('post','')
    print(message)
    zID = request.cookies.get('zid')
    fromID = request.cookies.get('zid')
    now = str(datetime.datetime.now()).split(' ')
    t = now[1].split('.')[0]
    posttime = now[0]+'T'+t+'+0000'
    ID = g.db.execute('select count(*) from Posts').fetchone()[0]
    # print(ID)
    g.db.execute('INSERT INTO Posts (ID,zID,fromID,posttime,message) VALUES (?,?,?,?,?)', [ID,zID,fromID,posttime,message])
    g.db.commit()
    # print(fromID)
    print("ADD post successful")
    return redirect(url_for('begin'))

#check if they are friend 1:friend, 0:pending
def checkFriendRe(userId,friendID):
    for friend in query_db("select ZID, friend, status from friends where ZID = ? AND friend = ?",[userId,friendID]):
        if friend['status'] == 1:
            return "True"
        elif friend['status'] == 0:
            return "Pending"
    return "False"


def getPostByID(zid):
    postList = []
    commentList = []
    replyList = []
    for post in query_db("SELECT Posts.ID, Users.full_name, Posts.message, Posts.posttime, Users.ZID FROM Posts , Users WHERE Posts.fromID=Users.ZID AND Posts.zID=Users.ZID AND " +
                    "Posts.commentID is null AND Posts.replyID is null AND ( Posts.zID IN (SELECT friend from friends WHERE ZID = '" + zid + "') OR Posts.zID = '" + zid + "')" +
                    "ORDER BY Posts.posttime DESC"):
        time = str(post['posttime']).split("T")
        time[1] = re.sub(r'\+0000', '', time[1])
        time = time[0] + " " + time[1]
        postList.append({
            "postID": post['ID'],
            "poster": post['full_name'],
            "content": post['message'],
            "time": time,
            "id": post['ZID'],
            "photo": "../static/dataset-medium/"+post['ZID']+"/img.jpg"
        })
    for p in postList:
        postID = p['postID']
        for comment in query_db("select Posts.ID,Users.full_name,Posts.message,Posts.posttime,Users.ZID from Posts,Users Where Posts.commentID = ? and Posts.fromID = Users.ZID ORDER BY Posts.posttime DESC",[postID]):
            timeC = str(comment['posttime']).split("T")
            timeC[1] = re.sub(r'\+0000', '', timeC[1])
            timeC = timeC[0] + " " + timeC[1]
            commentList.append({
                "fromPost":postID,
                "postID":comment['ID'],
                "poster": comment['full_name'],
                "content": comment['message'],
                "time": timeC,
                "id": comment['ZID'],
                "photo": "../static/dataset-medium/" + comment['ZID'] + "/img.jpg"
            })
    # print(commentList)
    for c in commentList:
        commentID = c['postID']
        for reply in query_db("select Posts.ID,Users.full_name,Posts.message,Posts.posttime,Users.ZID from Posts,Users Where Posts.replyID = ? and Posts.fromID = Users.ZID ORDER BY Posts.posttime DESC",[commentID]):
            timeR = str(reply['posttime']).split("T")
            timeR[1] = re.sub(r'\+0000', '', timeR[1])
            timeR = timeR[0] + " " + timeR[1]
            replyList.append({
                "fromComment": commentID,
                "postID": reply['ID'],
                "poster": reply['full_name'],
                "content": reply['message'],
                "time": timeR,
                "id": reply['ZID'],
                "photo": "../static/dataset-medium/" + reply['ZID'] + "/img.jpg"
            })
    # print(replyList)
    return postList,commentList,replyList



if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)

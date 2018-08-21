#!/usr/bin/python3

import sqlite3
import glob
import re

print("haha")
conn = sqlite3.connect('assn2.db')
conn.text_factory = str
print ("Opened database successfully")

paths = glob.glob("static/dataset-medium/*/student.txt")

for path in paths:
    # print(path)
    f = open(path, 'r')
    buff = f.read()
    buff = buff.split('\n')
    user=dict()
    user= {'zid':None,
            'name':None,
            'password':'',
            'home_latitude':None,
            'home_longitude':None,
            'email':None,
            'home_suburb':None,
            'birthday':None,
            'program':None,
            'intro':None}
#    print buff
    for line in buff:
        if re.match(r'\s*full_name', line):
            user['name'] = re.sub(r'\s*full_name:\s*',r'',line)
        elif re.match(r'zid:\s*',line):
            zid = re.sub(r'\s*zid:\s*',r'',line)
            zid = re.sub(r'\s*$',r'',zid)
            user['zid']= zid
        elif re.match(r'password:',line):
            password = re.sub(r'\s*password:\s*',r'',line)
            password = re.sub(r'\s*$',r'',password)
            user['password']= password
        elif re.match(r'home_latitude:',line):
            user['home_latitude']= re.sub(r'\s*home_latitude:\s*',r'',line)
        elif re.match(r'email:',line):
            user['email']= re.sub(r'\s*email:\s*',r'',line)
        elif re.match(r'program:',line):
            user['program']= re.sub(r'\s*program:\s*',r'',line)
        elif re.match(r'home_suburb',line):
            user['home_suburb']= re.sub(r'\s*home_suburb:\s*',r'',line)
        elif re.match(r'\s*home_longitude:',line):
            user['home_longitude']= re.sub(r'\s*home_longitude:\s*',r'',line)
        elif re.match(r'\s*birthday:',line):
            user['birthday']= re.sub(r'\s*birthday:\s*',r'',line)
        #print user['birthday']
    conn.execute("INSERT INTO users (zid, password, full_name, birthday, email, program, home_suburb, longitude, latitude,intro) VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (user['zid'],
                   user['password'],
                   user['name'],
                   user['birthday'],
                   user['email'],
                   user['program'],
                   user['home_suburb'],
                   user['home_longitude'],
                   user['home_latitude'],
                   user['intro']))
#
paths = glob.glob("static/dataset-medium/*/*.txt")


po = dict()
i = 0
for path in paths:
    if re.match(r'(^.*\/[0-9]+(\-)?([0-9]+)?(\-)?([0-9]+)?\.txt$)', path):
        m1=re.match(r'(^.*\/z\d+\/(\d+)\.txt$)', path)
        m2=re.match(r'(^.*\/z\d+\/(\d+)\-(\d+)\.txt$)', path)
        m3=re.match(r'(^.*\/z\d+\/(\d+)\-(\d+)\-(\d+)\.txt$)', path)
        if m1 :
            print(path)
            p=path.split('/')
            currpost=p[3]
            currpost=re.sub(r'\.txt','',currpost)
            currkey=p[2]+currpost
            po[currkey] = i
        #if its comment, get commentID from po
        if m2:
            print(path)
            p=path.split('/')
            c=p[3].split('-')
            commentID_key=p[2]+c[0]
            currcomment=p[3]
            currcomment=re.sub(r'\.txt','',currcomment)
            currkey=p[2]+currcomment
            # print(po[commentID_key])
            po[currkey] = i

        i +=1

# print(post)
i = 0

for path in paths:
    # path =postpath+"post.txt"

    # if re.match(r'(^.*\/[0-9]+(\-)?([0-9]+)?(\-)?([0-9]+)?\.txt$)', path):
    #     id = re.search(r'([0-9]+(\-)?([0-9]+)?(\-)?([0-9]+)?\.txt$)', path)
    #     id = id.group(1)
    #     id = re.sub(r'\s*.txt\s*','',id)
    #     po[id] = i
    if re.match(r'(^.*\/[0-9]+(\-)?([0-9]+)?(\-)?([0-9]+)?\.txt$)', path):
        m=re.search(r'(z\d{7})',path)
        zid=m.group(1)

        if re.match(r'(^.*\/[0-9]+\.txt$)', path):
            pId = re.search(r'([0-9]+\.txt$)', path)
            pId = pId.group(1)
            pId = re.sub(r'\s*.txt\s*', '', pId)
            # print("post + "+pId)
            #po = {pId: i}
            f = open(path, 'r')
            buff = f.read()
            buff = buff.split('\n')
            post=dict()
            post = {'postid':i,
                    'zid': zid,
                    'fromid': None,
                    'message': None,
                    'posttime': None,
                    'longitude': None,
                    'latitude': None,
                    'commentID': None,
                    'replyID': None}
            for line in buff:
                if re.match(r'^\s*message:\s*',line):
                    post['message'] = re.sub(r'^\s*message:\s*', "", line)
                elif re.match(r'^\s*from:',line):
                    post['fromid'] =re.sub(r'^\s*from:\s*', "", line)
                elif re.match(r'^\s*latitude:\s*', line):
                    post['latitude']= re.sub(r'^\s*latitude:\s*', "", line)
                elif re.match(r'^\s*longitude:\s*',line):
                    post['longitude'] =re.sub(r'^\s*longitude:\s*', "", line)
                elif re.match(r'^\s*time:\s*', line):
                    post['posttime'] = re.sub(r'^\s*time:\s*', "", line)
            #insert post

            conn.execute("INSERT INTO posts (ID, zid, fromID, posttime, latitutude, longitude, message, commentID, replyID) VALUES (?,?,?,?,?,?,?,?,?)",
                          (post['postid'],
                           post['zid'],
                           post['fromid'],
                           post['posttime'],
                           post['latitude'],
                           post['longitude'],
                           post['message'],
                           post['commentID'],
                           post['replyID']))


        if re.match(r'(^.*\/[0-9]+\-[0-9]+\.txt$)', path):
            id = re.search(r'([0-9]+\-[0-9]+\.txt$)', path)
            id = id.group(1)
            id = re.sub(r'\s*.txt\s*', '', id)
            idL = id.split("-")
            pId = idL[0]
            cId = idL[1]
            f = open(path, 'r')
            buff = f.read()
            buff = buff.split('\n')
            # print("comment "+pId + "-"+ cId + " comment id " + str(po.get(pId)))
            # print(po.get(pId))
            comment = dict()
            comment = {'postid': i,
                    'zid': zid,
                    'fromid': None,
                    'message': None,
                    'posttime': None,
                    'longitude': None,
                    'latitude': None,
                    'commentID': po.get(zid+pId),
                    'replyID': None}
            for line in buff :
                if re.match(r'^\s*message:\s*',line):
                    comment['message'] = re.sub(r'^\s*message:\s*', "", line)
                elif re.match(r'^\s*from:',line):
                    comment['fromid'] =re.sub(r'^\s*from:\s*', "", line)
                elif re.match(r'^\s*latitude:\s*', line):
                    comment['latitude']= re.sub(r'^\s*latitude:\s*', "", line)
                elif re.match(r'^\s*longitude:\s*',line):
                    comment['longitude'] =re.sub(r'^\s*longitude:\s*', "", line)
                elif re.match(r'^\s*time:\s*', line):
                    comment['posttime'] = re.sub(r'^\s*time:\s*', "", line)

            conn.execute("INSERT INTO posts (ID, zid, fromID, posttime, latitutude, longitude, message, commentID, replyID) VALUES (?,?,?,?,?,?,?,?,?)",
                          (comment['postid'],
                           comment['zid'],
                           comment['fromid'],
                           comment['posttime'],
                           comment['latitude'],
                           comment['longitude'],
                           comment['message'],
                           comment['commentID'],
                           comment['replyID']))

        if re.match(r'(^.*\/[0-9]+\-[0-9]+\-[0-9]+\.txt$)', path):
            id = re.search(r'([0-9]+\-[0-9]+\-[0-9]+\.txt$)', path)
            id = id.group(1)
            id = re.sub(r'\s*.txt\s*', '', id)
            idL = id.split("-")
            pId = idL[0]
            cId = idL[1]
            rId = idL[2]
            r = pId + "-" + cId
            # print("reply "+r + " " + rId + " reply id "+str(po.get(r)))
            # print(po.get(r))
            f = open(path, 'r')
            # po = {id: i}
            buff = f.read()
            buff = buff.split('\n')
            reply = dict()
            reply = {'postid': i,
                    'zid': zid,
                    'fromid': None,
                    'message': None,
                    'posttime': None,
                    'longitude': None,
                    'latitude': None,
                    'commentID': None,
                    'replyID': po.get(zid+r)}
            for line in buff :
                if re.match(r'^\s*message:\s*',line):
                    reply['message'] = re.sub(r'^\s*message:\s*', "", line)
                elif re.match(r'^\s*from:',line):
                    reply['fromid'] =re.sub(r'^\s*from:\s*', "", line)
                elif re.match(r'^\s*latitude:\s*', line):
                    reply['latitude']= re.sub(r'^\s*latitude:\s*', "", line)
                elif re.match(r'^\s*longitude:\s*',line):
                    reply['longitude'] =re.sub(r'^\s*longitude:\s*', "", line)
                elif re.match(r'^\s*time:\s*', line):
                    reply['posttime'] = re.sub(r'^\s*time:\s*', "", line)

            conn.execute("INSERT INTO posts (ID, zid, fromID, posttime, latitutude, longitude, message, commentID, replyID) VALUES (?,?,?,?,?,?,?,?,?)",
                          (reply['postid'],
                           reply['zid'],
                           reply['fromid'],
                           reply['posttime'],
                           reply['latitude'],
                           reply['longitude'],
                           reply['message'],
                           reply['commentID'],
                           reply['replyID']))
        i = i+1

#end of insert to post

#create table for courses and friends
paths = glob.glob("static/dataset-medium/*/student.txt")
for path in paths:
    m=re.search(r'(z\d{7})',path)
    zid=m.group(1)
    f = open(path, 'r')
    buff = f.read()
    buff = buff.split('\n')
    for line in buff:
        if re.match(r'^\s*courses:',line):
            courses = re.sub(r'^\s*courses:\s*',r'',line)
            courses = re.sub(r'^\s*\(|\)\s*$',r'',courses)
            courses = courses.split(',')
            for c in courses :
                c = re.sub(r'^\s*',r'',c)
                conn.execute("INSERT INTO courses (ZID, course) VALUES (?,?)",
                              (zid,
                               c))

        if re.match(r'^\s*friends:',line):
            friends = re.sub(r'^\s*friends:\s*',r'',line)
            friends = re.sub(r'^\s*\(|\)\s*$',r'',friends)
            friends = friends.split(',')
            status = 1
            for m in friends:
                m = re.sub(r'^\s*',r'',m)
                conn.execute("INSERT INTO friends (ZID, friend,status) VALUES (?,?,?)",
                              (zid,
                               m,
                               status))

conn.commit()
print ("success congrats")
conn.close()

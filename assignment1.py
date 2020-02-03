from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from random import randint
from datetime import datetime
from datetime import date
import time
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rideshare.db'
db = SQLAlchemy(app)


class user_details(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(80))

class ride_details(db.Model):
    rideid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    timestamp = db.Column(db.String(80))
    source = db.Column(db.Integer)
    destination = db.Column(db.Integer)

db.create_all()
cps =['1','0','2','3','4','5','6','7','8','9','a','b','c','d','e','f','A','B','C','D','E','F']

###############################################TASK 1################################################

@app.route("/api/v1/users",methods=["PUT"])
def add_user():
    un = request.get_json()["username"]
    ps = request.get_json()["password"]
    c = app.test_client()
    para1 = {
    "table"  : "user_details",
	"column" : ["username","password"],
	"where" :  "username = "+ un
    }
    response = c.post('/api/v1/db/read',json=para1,follow_redirects=True)
    if(response.get_json()): 
        return jsonify("Key already exists"),400
    if len(ps)!=40:
        return jsonify("Password is not of type SHA1 hash hex"),400
    else:
        for i in ps:
            if(i not in cps):
                return jsonify("Password is not of type SHA1 hash hex"),400
    c = app.test_client()
    para = {
    "table"  : "user_details",
	"column" : ["username","password"],
	"insert" : [un,ps]
    }
    response = c.post('/api/v1/db/write',json=para,follow_redirects=True)
    return {},201

###############################################TASK 2################################################

@app.route("/api/v1/users/<user>",methods=["DELETE"])
def delete_user(user):
    c = app.test_client()
    para1 = {
    "table"  : "user_details",
	"column" : ["username"],
	"where" :  "username = "+ user
    }
    response = c.post('/api/v1/db/read',json=para1,follow_redirects=True)
    #user1= user_details.query.filter_by(username = user).first()
    if(response.get_json()): 
        user_details.query.filter(user_details.username == user).delete() 
        db.session.commit()
    else:
        return jsonify("Username does not exist"),400
    return {},200

###############################################TASK 3################################################

@app.route("/api/v1/rides",methods=["POST"])
def add_ride():
    un = request.get_json()["created_by"]
    ts = request.get_json()["timestamp"]
    src = request.get_json()["source"]
    dest = request.get_json()["destination"]
    c = app.test_client()
    para1 = {
    "table"  : "user_details",
	"column" : ["username","password"],
	"where" :  "username = "+ un
    }
    response = c.post('/api/v1/db/read',json=para1,follow_redirects=True)
    print(response.get_json())
    if(response.get_json()): 
        rid = randint(0,9999)
        if((src>0)and(src<199)):
            if((dest>0)and(dest<199)):
                c = app.test_client()
                para = {
                        "table"  : "ride_details",
	                    "column" : ["rideid","username","timestamp","source","destination"],
	                    "insert" : [rid,un,ts,src,dest]
                }
                response = c.post('/api/v1/db/write',json=para,follow_redirects=True)
            else:
                return jsonify("Destination doesnot exist"), 400
        else:
            return jsonify("Source doesnot exist"), 400
    else:
        return jsonify("Username doesnot exist"), 400
    return {},201

###############################################TASK 4################################################


###############################################TASK 5################################################

###############################################TASK 6################################################

###############################################TASK 7################################################

@app.route("/api/v1/rides/<rid>",methods=["DELETE"])
def delete_ride(rid):
    c = app.test_client()
    para1 = {
    "table"  : "ride_details",
	"column" : ["rideid"],
	"where" :  "rideid = "+ rid
    }
    response = c.post('/api/v1/db/read',json=para1,follow_redirects=True)
    if(response.get_json()): 
        ride_details.query.filter(ride_details.rideid == rid).delete() 
        db.session.commit()
    else:
        return jsonify("Ride ID does not exist"),400
    return {},200

###############################################TASK 8################################################

@app.route("/api/v1/db/write",methods=["POST"])
def write_db():
    data = request.get_json()["insert"]
    cn = request.get_json()["column"]
    tn = request.get_json()["table"]
    tn=eval(tn) 
    new_user=tn()
    for i in range(len(data)):
        data1 = data[i]
        c1 = cn[i]
        setattr(new_user, c1, data1)
    db.session.add(new_user)
    db.session.commit()
    return {},200

###############################################TASK 9################################################


    
@app.route("/api/v1/db/read",methods=["POST"])
def read_db():
    data = request.get_json()["where"]
    cn = request.get_json()["column"]
    tn = request.get_json()["table"]
    tn=eval(tn) 
    new_user=tn()
    result = data.find('AND') 
    if(result==-1):
        ind = data.find('=')
        att = data[:ind-1]
        val = data[ind+2:]
        x = getattr(tn, att)
        user1= tn.query.filter((x == val)).first()
        d = {}
        if(user1 is not None):
            for j in cn:
                a = getattr(user1, j)
                d[j] = a
        return d
    else:
        q1 = data[:result-1]
        q2 = data[result+4:]
        i1 = q1.find('=')
        a1 = q1[:i1-1]
        v1 = q1[i1+2:]
        #print(a1)
        x1 = getattr(tn, a1)
        i2 = q1.find('=')
        a2 = q1[:i2-1]
        v2 = q1[i2+2:]
        x2 = getattr(tn, a2)
        user1= tn.query.filter((x1 == v1)&(x2 == v2)).all()
        #print(user1)
        d = {}
        #return str(user1)
        #return str(cn)
        for i in user1:
            cnt = 0
            for j in cn:
                if j not in d:
                    d[j] =[]
                    cnt =cnt+1
                a = getattr(i, j)
                d[j].append(a)
        return d
        #print(d)

if __name__ == "__main__":
    app.debug=True
    app.run()

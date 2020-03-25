from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_restful import Api, reqparse
from flask import json
from flask_jwt_extended import JWTManager
from flask import jsonify

from bson.objectid import ObjectId
from bson.json_util import dumps
from bson import json_util, ObjectId
from bson import ObjectId

from flask_pymongo import PyMongo
import urllib
#from urllib import unquote_plus
from urllib.parse import unquote_plus

from pytz import timezone

import json
import requests
import pandas
#import urllib.parse 
from flask_cors import CORS, cross_origin
import json
import datetime
import boto3
app = Flask(__name__)
cors = CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
##app.config['PROPAGATE_EXCEPTIONS'] = True
app=Flask(__name__,template_folder='static')
api = Api(app)

#app.config['MONGO_DBNAME'] = 'property'
#app.config["MONGO_URI"] = "mongodb://localhost:27017/property"
#app.config['MONGO_URI'] = 'mongodb://user:' + urllib.quote("pas") + '@chat-shard-00-00-9bj5r.mongodb.net:27017,chat-shard-00-01-9bj5r.mongodb.net:27017,chat-shard-00-02-9bj5r.mongodb.net:27017/admisi_chats?ssl=true&replicaSet=chat-shard-0&authSource=admin&retryWrites=true&w=majority'
app.config['MONGO_URI'] = 'mongodb://user:' + urllib.parse.quote_plus("pas") + '@chat-shard-00-00-9bj5r.mongodb.net:27017,chat-shard-00-01-9bj5r.mongodb.net:27017,chat-shard-00-02-9bj5r.mongodb.net:27017/admisi_chats?ssl=true&replicaSet=chat-shard-0&authSource=admin&retryWrites=true&w=majority'
#app.config['MONGO_URI'] = 'mongodb://user:' + urllib.quote("pas") + '@cluster0-shard-00-00-9w1yt.mongodb.net:27017,cluster0-shard-00-01-9w1yt.mongodb.net:27017,cluster0-shard-00-02-9w1yt.mongodb.net:27017/property?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true'
def non_empty_string(s):
    if not s:
        raise ValueError("Must not be empty string")
    return s

mongo = PyMongo(app)
data_chat = reqparse.RequestParser()
chats = reqparse.RequestParser()

data_chat.add_argument('messages', help= 'This field cannot be blank', required = True, type=non_empty_string)

chats.add_argument('chatId', help= 'This field cannot be blank', required = True, type=non_empty_string)
chats.add_argument('body', help= 'This field cannot be blank', required = False, type=non_empty_string)


CORS(app)
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
##app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(0.01)
jwt = JWTManager(app)

app.config['JWT_BLACKLIST_ENABLED'] = False
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


@app.route('/')
def main_world():
    return render_template('index.html')


def jsonDumps(get_data):
    return json.loads(json_util.dumps(get_data))
#====================Chats=======================#
@app.route('/list', methods=['GET'])
def get_all_chat():
  record=mongo.db.chats
  cursor=record.find()
  output = []
  for doc in cursor:
    data=jsonDumps(doc)
    output.append(data)
  return jsonify({"data":output,"status": "success"})

@app.route('/log_chats_today', methods=['GET'])
def log_chats_today():
  record=mongo.db.log_chats
  now = datetime.datetime.now(timezone('Asia/Bangkok'))
  print(now)
  cursor=record.find({"fromMe":False,"time": {"$gte":datetime.datetime(now.year, now.month, now.day, 00, 00 ,00) , "$lt":datetime.datetime(now.year, now.month, now.day,  23, 59, 59)}})
  output = []
  for doc in cursor:
    data=jsonDumps(doc)
    output.append(data)
  return jsonify({"data":output,"status": "success"})

@app.route('/log_chats_today_by_hour', methods=['GET'])
def log_chats_today_by_hour():
  record=mongo.db.log_chats
  now = datetime.datetime.now(timezone('Asia/Bangkok'))
  print(now)
  cursor=record.aggregate([{"$project": {"y":{"$year":"$time"},"m":{"$month":"$time"},"d":{"$dayOfMonth":"$time"},"h":{"$hour":"$time"}}},{"$group":{"_id": { "year":"$y","month":"$m","day":"$d","hour":"$h"},"total":{ "$sum": 1}}},{"$sort": {"_id": 1}}])
  output = []
  timeline_data = []
  timeline_hour = []
  now = datetime.datetime.now(timezone('Asia/Bangkok'))
  for doc in cursor:
    data=jsonDumps(doc)
    output.append(data)
    #print(data['_id']['day'])
    if(data['_id']['day']==now.day):
      timeline_hour.append(data['_id']['hour'])
      timeline_data.append(data['total'])
  return jsonify({"data_hours":timeline_hour,"total":timeline_data,"status": "success"})


@app.route('/count_log_chats_mounth', methods=['GET'])
def log_chats_mounth():
  record=mongo.db.log_chats
  now = datetime.datetime.now(timezone('Asia/Bangkok'))
  print(now)
  cursor=record.find({"time": {"$gte":datetime.datetime(now.year, now.month, 1) , "$lt":datetime.datetime(now.year, now.month, 28)}}).count()
  return jsonify({"data":cursor,"status": "success"})


@app.route('/count_log_by_status_mounth/<string:par1>', methods=['GET'])
def count_log_by_status_mounth(par1):
  record=mongo.db.log_chats
  now = datetime.datetime.now(timezone('Asia/Bangkok'))
  print(now)
  cursor=record.find({"user_type":par1, "time": {"$gte":datetime.datetime(now.year, now.month, 1) , "$lt":datetime.datetime(now.year, now.month, 28)}}).count()
  return jsonify({"data":cursor,"status": "success"})


@app.route('/status_log_chats_day', methods=['GET'])
def status_log_chats_day():
  record=mongo.db.log_chats
  now = datetime.datetime.now(timezone('Asia/Bangkok'))
  print(now)
  data_s = []
  data_cek = []
  cursor=record.aggregate([{"$match": {"time": {"$gte":datetime.datetime(now.year, now.month, now.day, 00, 00 ,00) , "$lt":datetime.datetime(now.year, now.month, now.day,  23, 59, 59)}}},{"$group": {"_id":"$user_type","count": {"$sum": 1}}}])

  for doc in cursor:
    data=jsonDumps(doc) 
    if(data['_id']=="unsolved"):
      data_un=(data['count'])
    elif(data['_id']=="follow"):
      data_fo=(data['count'])
    elif(data['_id']=="solved"):
      data_so=(data['count'])
    elif(data['_id']=="me"):
      data_sen=(data['count'])
  
  data_hasil=[data_un,data_fo,data_so,data_sen]
  return jsonify({"data":data_hasil,"status": "success"})


@app.route('/get_tranding_today', methods=['GET'])
def get_tranding_today():
  record=mongo.db.log_chats
  now = datetime.datetime.now(timezone('Asia/Bangkok'))
  print(now)
  data_s = []
  cursor=record.aggregate([{"$match": {"time": {"$gte":datetime.datetime(now.year, now.month, now.day, 00, 00 ,00) , "$lt":datetime.datetime(now.year, now.month, now.day,  23, 59, 59)}}},{"$match":{"fromMe":False}},{"$unwind":"$intens"},{"$sortByCount":"$intens"},{"$limit":10}])
  for doc in cursor:
    data=jsonDumps(doc) 
    if(data['_id'] != "Default Welcome Intent" and data['_id'] != "Default Fallback Intent" and data['_id'] != "Solved Respone"):
      data_s.append({"Intens":data['_id'],"total":data['count']})

  return jsonify({"data":data_s,"status": "success"})


@app.route('/count_chats_today/<string:par1>/<string:par2>/', methods=['GET'])
def count_chats_today(par1,par2):
  fromMe=unquote_plus(par1)
  if(fromMe=="me"):
    me=True
  else:
    me=False
  record=mongo.db.log_chats
  now = datetime.datetime.now(timezone('Asia/Bangkok'))
  cursor=record.find({"fromMe":me,"user_type":par2,"time": {"$gte":datetime.datetime(now.year, now.month, now.day, 00, 00 ,00) , "$lt":datetime.datetime(now.year, now.month, now.day,  23, 59, 59)}}).count()
  return jsonify({"status":"success","total":cursor})


@app.route('/count_log_all_by_status/<string:par1>/', methods=['GET'])
def count_log_all_by_status(par1):
  record=mongo.db.log_chats
  cursor=record.find({"user_type":par1}).count()
  return jsonify({"status":"success","total":cursor})


@app.route('/count_log_all/<string:par1>/', methods=['GET'])
def count_log_all(par1):
  fromMe=unquote_plus(par1)
  record=mongo.db.log_chats
  if(fromMe=="me"):
    me=True
  else:
    me=False
  cursor=record.find({"fromMe":me}).count()
  return jsonify({"status":"success","total":cursor})



@app.route('/show_data_per_mounth', methods=['GET'])
def show_data_per_mounth():
  record=mongo.db.log_chats
  #cursor=record.aggregate([{"$match": {"fromMe":False}},{"$group": {"_id": {"$month": "$time"},"count": {"$sum": 1}}},{"$sort": {"_id": 1}}])
  cursor=record.aggregate([{"$group": {"_id": {"$month": "$time"},"count": {"$sum": 1}}},{"$sort": {"_id": 1}}])
  output = []
  data_mounth = []
  data_time = []
  no=1
  for doc in cursor:
    data=jsonDumps(doc)
    output.append(data)
    data_time.append(data['count'])
  return jsonify({"data":data_time,"status": "success"})


@app.route('/show_data_per_mounth_by_status/<string:par1>/', methods=['GET'])
def show_data_per_mounth_by_status(par1):
  status=unquote_plus(par1)
  record=mongo.db.log_chats
  cursor=record.aggregate([{"$match": {"user_type":status}},{"$group": {"_id": {"$month": "$time"},"count": {"$sum": 1}}},{"$sort": {"_id": 1}}])
  #cursor=record.aggregate([{"$group": {"_id": {"$month": "$time"},"count": {"$sum": 1}}},{"$sort": {"_id": 1}}])
  output = []
  data_mounth = []
  data_time = []
  no=1
  for doc in cursor:
    data=jsonDumps(doc)
    output.append(data)
    data_time.append(data['count'])
  return jsonify({"data":data_time,"status": "success"})


@app.route('/show_by_status_data_per_mounth/<string:par1>', methods=['GET'])
def show_by_status_data_per_mounth(par1):
  record=mongo.db.log_chats
  cursor=record.aggregate([{"$match": {"fromMe":False}},{"$group": {"_id": {"$month": "$time"},"count": {"$sum": 1}}},{"$sort": {"_id": 1}}])
  #cursor=record.aggregate([{"$group": {"_id": {"$month": "$time"},"count": {"$sum": 1}}},{"$sort": {"_id": 1}}])
  output = []
  data_mounth = []
  data_time = []
  no=1
  for doc in cursor:
    data=jsonDumps(doc)
    output.append(data)
    data_time.append(data['count'])

  return jsonify({"data":data_time,"status": "success"})

@app.route('/list_log', methods=['GET'])
def get_all_chat_logs():
  record=mongo.db.log_chats
  cursor=record.find()
  output = []
  for doc in cursor:
    data=jsonDumps(doc) 
    output.append(data)
  return jsonify({"data":output,"status": "success"})

@app.route('/get_chat/<string:par1>/', methods=['GET'])
def get_chat_1(par1):
  record = mongo.db.chats
  cursor=record.find({'chatId':par1})
  output = []
  for doc in cursor:
    data=jsonDumps(doc) 
    output.append(data)
  return jsonify({"data":output,"status": "success"})

#Get Chat Dari Id_user
def get_chat(author):
  record = mongo.db.chats
  cursor=record.find({'author':author}).count()
  if(cursor>0):
    return ("1")
  else:
    return ("0")


#==================Get Logs User===================#

@app.route('/log_new_old_user_today', methods=['GET'])
def log_new_old_user_today():
  record=mongo.db.user_logs
  now = datetime.datetime.now(timezone('Asia/Bangkok'))
  print(now)
  data_s = []
  cursor=record.aggregate([{"$match": {"time": {"$gte":datetime.datetime(now.year, now.month, now.day, 00, 00 ,00) , "$lt":datetime.datetime(now.year, now.month, now.day,  23, 59, 59)}}},{"$group": {"_id":"$type","count": {"$sum": 1}}}])
  for doc in cursor:
    data=jsonDumps(doc) 
    if(data['_id']=="old"):
      data_old=(data['count'])
    elif(data['_id']=="new"):
      data_new=(data['count'])

  return jsonify({"data_new":data_new,"data_old":data_old,"status": "success"})


@app.route('/new_user_this_month', methods=['GET'])
def new_user_this_month():
  record=mongo.db.user_logs
  now = datetime.datetime.now(timezone('Asia/Bangkok'))
  print(now)
  data_s = []
  cursor=record.find({"type":"new", "time": {"$gte":datetime.datetime(now.year, now.month, 1) , "$lt":datetime.datetime(now.year, now.month, 28)}}).count()

  return jsonify({"data":cursor,"status": "success"})


#====================Dialogs=========================#
@app.route('/list_dialogs_all/', methods=['GET'])
def list_dialogs_all():
  record=mongo.db.dialogs
  cursor=record.aggregate([{"$match":{"log_chat.status":"solved"}},{"$project":{"nomor":"$author","status":"$type","avgRating":{"$avg":"$log_chat.total"}}}])
  output = []
  for doc in cursor:
    data=jsonDumps(doc) 
    output.append(data)
  return jsonify({"data":output,"status": "success"})

@app.route('/list_dialogs_all_res/', methods=['GET'])
def list_dialogs_all_res():
  record=mongo.db.dialogs
  cursor=record.find()
  output = []
  for doc in cursor:
    data=jsonDumps(doc) 
    output.append(data)
  return jsonify({"data":output,"status": "success"})



@app.route('/average_que/', methods=['GET'])
def average_que():
  record=mongo.db.dialogs
  cursor=record.aggregate([{"$match":{"log_chat.status":"solved"}},{"$project":{"nomor":"$author","status":"$type","avgRating":{"$avg":"$log_chat.total"}}}])
  output = []
  for doc in cursor:
    data=jsonDumps(doc) 
    output.append(data['avgRating'])
  hasil=sum(output) / len(output) 
  return jsonify({"data":hasil,"status": "success"})



def update_log_chat_user(chatId,status):
  author="5e47eca56a057105b9d5f16a"
  action=mongo.db.dialogs.update({"chatId":chatId,"log_chat.status":status},{"$inc": {"log_chat.$.total" : 1}},False,True)
  hasil=(jsonDumps(action))
  print(hasil)
  if(hasil['nModified']==1):
    print("Berhasil")
    if(status=="solved"):
      action=mongo.db.dialogs.update({"_id":ObjectId(author),"log_chat.status":"follow"},{"$set": {"log_chat.$.status" : "solved"}},False,True)
  else:
    action=mongo.db.dialogs.update({"_id":ObjectId(author)},{"$push":{"log_chat":{"status":"follow","total":1}}})

@app.route('/list_dialogs_by_status/<string:par1>', methods=['GET'])
def list_dialogs_by_status(par1):
  record=mongo.db.dialogs
  cursor=record.find({"type":par1})
  output = []
  for doc in cursor:
    data=jsonDumps(doc) 
    output.append(data)
  return jsonify({"data":output,"status": "success"})






@app.route('/hapus', methods=['GET'])
def deleteadvert():
  action=mongo.db.log_chat.delete_many({"fromMe":True})
    
  if(action.deleted_count > 0):
    return ({"success": True, "messege":"Berhasil Menghapus Iklan"})
  else:
    return ({"succes":False,"messege":"Gagal Menghapus Iklan, Mungkin Pesan sudah terhapus atau tidak ada"})  

#----Insert Data if new User in Collection Dialogs
def insert_new_contact(chatId,author,status,timenow):
  action_1=mongo.db.dialogs.insert_one({"chatId":chatId,"author":author,"time":datetime.datetime.utcnow(),"type":typee_user,"log_chat":[{"status":"follow","total":1}]})
  action_2=mongo.db.user_logs.insert_one({"chatId":chatId,"type":"old","time":timenow}) 
  if(action_1):
    return({"success":True})
  if(action_2):
    return({"success":True})

def update_contact_status(chatId,user_type):
  print(chatId)
  action=mongo.db.dialogs.update({"chatId":chatId},{"$set":{"type":user_type}})
  hasil=(jsonDumps(action))
  print(hasil)
  
@app.route('/chat', methods=['POST'])
def chat():
  data_s =chats.parse_args()
  chatId=(data_s["chatId"])
  pesan=(data_s['body'])
  r_1 = requests.post("https://eu68.chat-api.com/instance109289/sendMessage?token=tiuxhi6fl30q7o9mn", json={'phone': chatId,'body':pesan})
  return jsonify({"status":"success"})



@app.route('/bot_respone', methods=['POST'])
def bot_respon():
  data =data_chat.parse_args()
  messages = data['messages']
  chatId = data['messages']['chatId']
  fromMe= data['messages']['fromMe']
  author= data['messages']['author']
  body = data['messages']['body']
  time_unix = data['messages']['time']
  senderName = data['messages']['senderName']
  typee = data['messages']['type']
  quotedMsg = data['messages']['quotedMsgBody']
  chatName = data['messages']['chatName']
  time_convert = pandas.to_datetime(time_unix,unit='s')
  time=str(time_convert)
  ##print(time)
  jumlah=(len(chatId))
  #print(jumlah)
  cek = requests.get("https://api-dialogflow-admisi.herokuapp.com/?"+body)
  #print(cek.text)
  pesan_cek = (cek.text)
  data=cek.json()
  pesan=(data['data'])
  intens=(data['intent'])
  print(intens)
  if(fromMe==False and jumlah<21 and typee=="chat" ):
    #-----Bot Respon---------#
    print(get_chat(author))
    print_cek=get_chat(author)

    if(print_cek=="1"):
      r_1 = requests.post("https://eu68.chat-api.com/instance109289/sendMessage?token=tiulxhi6f30q7o9mn", json={'phone': chatId,'body':pesan})
      #Action Insert Collections Chats
      action=mongo.db.chats.insert_one({"chatId":chatId,"author":author,"body":body,"fromMe":fromMe,"time":datetime.datetime.utcnow(),"senderName":senderName,
        "type":typee,"quotedMsg":quotedMsg,"chatName":chatName})
      if(action):
        if(intens=="Solved Respone"):
          user_type="solved"
          print("solved")
          update_contact_status(chatId,user_type)  
          update_log_chat_user(chatId,user_type)
        elif(intens=="Default Fallback Intent"):
          user_type="unsolved"
          update_log_chat_user(chatId,user_type)
          update_contact_status(chatId,user_type)  
        else:
          user_type="follow"
          update_contact_status(chatId,user_type)  
          update_log_chat_user(chatId,user_type)  
        timenow = (datetime.datetime.today())
        #timenow = (datetime.datetime.today())
        #print(timenow)
        action=mongo.db.user_logs.insert_one({"chatId":chatId,"type":"old","time":timenow}) 
            
        log_chats(fromMe,timenow,intens,user_type)
        return jsonify({'status':'success'})
    else:
      r_1 = requests.post("https://eu68.chat-api.com/instance109289/sendMessage?token=tiuxkhi6fojo30q7o9mn", json={'phone': chatId,'body':pesan})      
      r_2 = requests.post("https://eu68.chat-api.com/instance109289/sendMessage?token=tiuxkhi6fojoo30q7o9mn", json={'phone': chatId,'body':"Hai Ini Kami dari CS admisi, Ini Pesan pertamamu kami nomor mu akan kami simpan yaa "})
      #Action Insert Collections Chats
      action=mongo.db.chats.insert_one({"chatId":chatId,"author":author,"body":body,"fromMe":fromMe,"time":datetime.datetime.utcnow(),"senderName":senderName,
        "type":typee,"quotedMsg":quotedMsg,"chatName":chatName})

      if(action):
        user_type="follow"
        timenow = (datetime.datetime.today())
        log_chats(fromMe,timenow,intens,user_type)
        typee_user="follow"
        insert_new_contact(chatId,author,typee_user,timenow)
        return jsonify({'status':'success'})

  elif(fromMe==True and jumlah<21 ):
    action=mongo.db.chats.insert_one({"chatId":chatId,"author":author,"body":body,"fromMe":fromMe,"time":datetime.datetime.utcnow(),"senderName":senderName,
      "type":typee,"quotedMsg":quotedMsg,"chatName":chatName})
    if(action):
      user_type="me"
      if(intens=="Solved Respone"):
        user_type_2="solved"
        print("solved lur")
        #update_contact_status(chatId,user_type_2)
      else:
        user_type_2="follow"
        #update_contact_status(chatId,user_type_2) 
      timenow = (datetime.datetime.today())

      log_chats(fromMe,timenow,intens,user_type)
      return jsonify({'status':'success'})
  else:
    return('gagal')  


def log_chats(fromMe,timenow,intens,user_type):
    print('berhasil')
    action=mongo.db.log_chats.insert_one({"fromMe":fromMe,"time":timenow,'intens':intens,"user_type":user_type})
    if(action):
      return ('berhasil')

@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The {} token has expired'.format(token_type)
    }), 401





if __name__ == '__main__':
     app.run(debug=True)

import json
from passlib.hash import pbkdf2_sha256 as sha256
from bson.objectid import ObjectId
from bson.json_util import dumps
from bson import json_util, ObjectId
from bson import ObjectId
from run import jsonify
from twilio.rest import Client
from run import mongo
import string
import random
from datetime import datetime

class UserModel():

	@staticmethod
	def generate_hash(password):
		return sha256.hash(password)

	@staticmethod
	def verify_hash(password, hash):
		return sha256.verify(password, hash)
	
	@staticmethod
	def InsertUser(data):
		data_user = UserModel.jsonDumps(data)
		password = UserModel.generate_hash(data_user['password'])
		return mongo.db.users.insert_one({"username":data_user['username'],"password":password,"email":data_user['email'],"gender":data_user['gender'],"nohp":[data_user['nohp']],"verified":False})
	@staticmethod
	def Getuser(id_user):
		action=mongo.db.users.find_one(ObjectId(id_user))
		data=UserModel.jsonDumps(action)
		if data is None:
			return {"data":"null"}
		else:
			del data["password"]
			return jsonify({"data":data})

	@staticmethod
	def OTPuser(number,id_user):
		print (id_user)

		code_activation = random.randint(1,10000)
		account_sid ="AC63b19cf6511058521818bc54b4abbc47"
		auth_token ="11d2474824b2d7939b5ce756a900e9cd"
		setnomor = number[1:]
		nomor = "+62"+str(setnomor)
		client = Client(account_sid, auth_token)
		message = client.messages \
                .create(
                     body="MarketPlace This is Your Code Activation: "+str(code_activation),
                     from_="+12063503291",
                     to='"'+nomor+'"'
                 )
		if(message):
                	UserModel.create_otp_token(id_user,code_activation)
                	response = jsonify({"success":True,
                			"message":"Varifed Code will be sent to :"+nomor+"",
                			"nomor":nomor})
                	response.headers.add('Access-Control-Allow-Origin', '*')
                	response.headers.add('Access-Control-Allow-Headers', '*')
                	return response
		else:
                	return ({"success":False})
	@staticmethod
	def create_otp_token(id_user,code_activation):
		today = str(datetime.today())
		action=mongo.db.otp.remove({"id_user":id_user})
		return mongo.db.otp.insert_one({"id_user":id_user,"code_activation":code_activation,"time":today})
	@staticmethod
	def activation_user(id_user,code_activation):
		cek_activation_number=mongo.db.otp.find({"id_user":id_user, "code_activation":code_activation}).count()
		if(cek_activation_number):
			mongo.db.users.update_one(
				{"_id":ObjectId(id_user)},
				{
				"$set":{"verified":True}
				}
				)
			return ({"success":True})
		else:
			return ({"success":False})
	@staticmethod
	def allUser():
		record=mongo.db.users
		cursor=record.find()
		output = []
		for doc in cursor:
			data=UserModel.jsonDumps(doc)
			output.append(data)
		return ({"succes":True,"data":output})

	@staticmethod
	def find_user_by_email(email):
		return mongo.db.users.find_one({"email":email})

	@staticmethod
	def find_user_by_password(password):
		return mongo.db.users.find_one({"password":password})

	@staticmethod
	def find_user_by_email_count(email):
		return mongo.db.users.find({"email":email}).count()

	@staticmethod
	def find_user_by_username_count(username):
		return mongo.db.users.find({"username":username}).count()

	@staticmethod		
	def jsonDumps(get_data):
		return json.loads(json_util.dumps(get_data))

	@staticmethod
	def InsertArtikel(data):
		data_user = UserModel.jsonDumps(data)
		return mongo.db.artikel.insert_one({"judul":data_user['judul'],"artikel":data_user['artikel']})

			
	

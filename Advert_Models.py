import json
import random
from passlib.hash import pbkdf2_sha256 as sha256
from bson.objectid import ObjectId
from bson.json_util import dumps
from bson import json_util, ObjectId
from bson import ObjectId
from twilio.rest import Client
from run import mongo
from run import jsonify
import string
from datetime import datetime
class AdvertModel():

	@staticmethod
	def GetAdvert(id_advert):
		action=mongo.db.advert.find_one(ObjectId(id_advert))
		data=AdvertModel.jsonDumps(action)

		get_image=data['foto']
		ini=0
		gambar=[]
		for doc in get_image:
			gambar.append(get_image[ini])
			ini=ini+1
			
		if data is None:
			return {"data":"null"}
		else:	
			get_id=(data['_id'])
			id_advert=(get_id['$oid'])
			del data["_id"]
			output=({
				"id":id_advert,
				"title":data['title'],
				"date":data['date'],
				"id_user":data['id_user'],
				"harga":data['harga'],
				"provinsi":data['provinsi'],
				"kab":data['kab'],
				"nego":data['nego'],
				"sertifikasi":data['sertifikasi'],
				"tersedia":data['tersedia'],
				"kategori":data['kategori'],
				"alamat":data['alamat'],
				"unggulan":data['unggulan'],
				"keterangan":data['keterangan'],
				"luas":data['luas']['luas_tanah'],
				"gambar":gambar

				})
			return ({"data":output})

	@staticmethod
	def GetImageLopp(id_advert):
		action=mongo.db.advert.find_one(ObjectId(id_advert))
		data=AdvertModel.jsonDumps(action)
		if data is None:
			return {"data":"null"}
		else:	
			get_id=(data['_id'])
			id_advert=(get_id['$oid'])
			del data["_id"]
			get_image=data['foto']
			ini=0
			gambar=[]
			for doc in get_image:
				gambar.append(get_image[ini])
				ini=ini+1	
			return gambar
		

	@staticmethod
	def GetAdvert_by_title(title,id_advert):
		alamat_foto="https://s3-ap-southeast-1.amazonaws.com/propertytoday/"
		action=mongo.db.advert.find_one({"$and":[{"title":title,"_id":ObjectId(id_advert)}]})
		data=AdvertModel.jsonDumps(action)
		get_id=(data['_id'])
		get_image=data['foto']
		id_user=data['id_user']
		ambil_user=mongo.db.users.find_one(ObjectId(id_user))
		data_user=AdvertModel.jsonDumps(ambil_user)
		ini=0
		gambar=[]
		for doc in get_image:
			gambar.append({"original":alamat_foto+get_image[ini],"thumbnail":alamat_foto+get_image[ini]})
			ini=ini+1

		id_advert=(get_id['$oid'])
		if data is None:
			return {"data":"null"}
		else:
			output=({
				"id":id_advert,
				"title":data['title'],
				"gambar":gambar,
				"date":data['date'],
				"harga":data['harga'],
				"provinsi":data['provinsi'],
				"kab":data['kab'],
				"nego":data['nego'],
				"sertifikasi":data['sertifikasi'],
				"tersedia":data['tersedia'],
				"nomor_hp":data_user['nohp'][0],
				"penjual":data_user['username'],
				"kategori":data['kategori'],
				"alamat":data['alamat'],
				"keterangan":data['keterangan'],
				"luas":data['luas']['luas_tanah']

				})
			return ({"data":output})

	@staticmethod
	def Pilihan_advert():
		record=mongo.db.advert
		cursor=record.aggregate([{"$match": {"unggulan":"true"}},{"$sample":{"size":12}}])
		##cursor=record.find({"unggulan":"true"}).sort("date",-1).limit(10)
		output = []
		alamat_foto="https://s3-ap-southeast-1.amazonaws.com/propertytoday/"
		for doc in cursor:
			data=AdvertModel.jsonDumps(doc)
			get_id=(data['_id'])
			id_advert=(get_id['$oid'])
			kab=data['kab'].capitalize()
			provinsi=data['provinsi'].capitalize()
			output.append({
				"id":id_advert,
				"kategori":data['kategori'],
				"title":data['title'],
				"harga":data['harga'],
				"nego":data['nego'],
				"sertifikasi":data['sertifikasi'],
				"luas":data['luas']['luas_tanah'],
				"alamat":kab+" - "+provinsi,
				"foto":alamat_foto+data['foto'][0]}
				)
		return ({"succes":True,"data":output})

	@staticmethod
	def getAdverts():
		record=mongo.db.advert
		cursor=record.find()
		output = []
		for doc in cursor:
			data=AdvertModel.jsonDumps(doc)
			output.append(data)
		return ({"succes":True,"data":output})
	
	@staticmethod
	def getCountAdvert():
		record=mongo.db.advert
		cursor= record.aggregate([{"$group":{"_id":"$kategori", "count":{"$sum":1}}}])
		output = []
		for doc in cursor:
			data=AdvertModel.jsonDumps(doc)
			output.append(data)
		return ({"succes":True,"data":output})
	
	@staticmethod
	def SearchAdvert(kategori, provinsi, kab, cari):
		record=mongo.db.advert
		search = []
		alamat_foto="https://s3-ap-southeast-1.amazonaws.com/propertytoday/"
		if provinsi == "semua" and kab == "semua" and cari == "" and kategori == "semua":
			cursor= record.find().sort([("number", 1), ("date", -1)])
			output = []
			for doc in cursor:
				data=AdvertModel.jsonDumps(doc)
				get_id=(data['_id'])
				id_advert=(get_id['$oid'])
				kab=data['kab'].capitalize()
				provinsi=data['provinsi'].capitalize()
				output.append(
					{
				"id":id_advert,
				"kategori":data['kategori'],
				"title":data['title'],
				"harga":data['harga'],
				"nego":data['nego'],
				"provinsi":data['provinsi'],
				"kab":data['kab'],
				"sertifikasi":data['sertifikasi'],
				"luas":data['luas']['luas_tanah'],
				"alamat":kab+" - "+provinsi,
				"foto":alamat_foto+data['foto'][0]}
				)
			return ({"succes":True,"data":output})
		else:
			if kategori !="semua":
				search.append({"kategori":kategori})
			if provinsi !="semua":
				search.append({"provinsi":provinsi})
			if kab !="semua":
				search.append({"kab":kab})
			if cari:
				search.append({ "$text": { "$search":cari } })

			#cursor=record.find({"$and":[{"provinsi":provinsi},{"kab":kab}, { "$text": { "$search": "rumah" } }]})	
			cursor=record.find({"$and":search}).sort([("number", 1), ("date", 1)])
			output = []
			for doc in cursor:
				data=AdvertModel.jsonDumps(doc)
				get_id=(data['_id'])
				id_advert=(get_id['$oid'])
				kab=data['kab'].capitalize()
				provinsi=data['provinsi'].capitalize()
				output.append({
				"id":id_advert,
				"kategori":data['kategori'],
				"title":data['title'],
				"harga":data['harga'],
				"nego":data['nego'],
				"sertifikasi":data['sertifikasi'],
				"luas":data['luas']['luas_tanah'],
				"alamat":kab+" - "+provinsi,
				"foto":alamat_foto+data['foto'][0]}
				)
			return ({"succes":True,"data":output})		

	@staticmethod		
	def jsonDumps(get_data):
		return json.loads(json_util.dumps(get_data))

	@staticmethod
	def InsertAdvert(title, keterangan, luas_bangunan,luas_tanah, harga, kategori,
		filenames, sertifikasi, nego, tersedia, provinsi, kab, id_user, alamat, unggulan):
		today = str(datetime.today())
		
		action=mongo.db.advert.insert({"title":title,"keterangan":keterangan,
			"luas":{"luas_tanah":luas_tanah,"luas_bangunan":luas_bangunan},
			"harga":harga,"kategori":kategori,"foto":filenames, "sertifikasi":sertifikasi,
			"nego":nego, "tersedia":tersedia, "provinsi":provinsi, "kab":kab, "id_user":id_user,
			"date":today, "alamat":alamat,"unggulan":unggulan
			})
		if(action):
			response=jsonify({"succes":True, "messege":"succes insert data"})
			response.headers.add('Access-Control-Allow-Origin', '*')
			response.headers.add('Access-Control-Allow-Headers', '*')
			return response
		else:
			return ({"succes":False, "messege":"Failed insert data"})


	@staticmethod
	def UpdateAdvert(id_advert,title, keterangan, luas_bangunan,luas_tanah, harga, kategori, sertifikasi, nego, tersedia, provinsi, kab, alamat, unggulan, id_user):
		action=mongo.db.advert.update({"_id":ObjectId(id_advert)},{"$set":{"title":title,"keterangan":keterangan,
			"luas":{"luas_tanah":luas_tanah},"kategori":kategori,"harga":harga,"tersedia":tersedia,"provinsi":provinsi,"kab":kab,"alamat":alamat,
			"unggulan":unggulan,"nego":nego,"sertifikasi":sertifikasi, "id_user":id_user
			}})
		if(action):
			response=jsonify({"succes":True, "messege":"succes insert data"})
			response.headers.add('Access-Control-Allow-Origin', '*')
			response.headers.add('Access-Control-Allow-Headers', '*')
			return response
		else:
			return ({"succes":False, "messege":"Failed insert data"})

	@staticmethod
	def deleteadvert(id_advert):
		action=mongo.db.advert.delete_one({"_id":ObjectId(id_advert)})
		
		if(action.deleted_count > 0):
			return ({"success": True, "messege":"Berhasil Menghapus Iklan"})
		else:
			return ({"succes":False,"messege":"Gagal Menghapus Iklan, Mungkin Pesan sudah terhapus atau tidak ada"})	

	@staticmethod
	def UpdateFoto(id_advert,file_lama,filename):
		#print id_advert
		record=mongo.db.advert
		cursor=record.update({"_id":ObjectId(id_advert), "foto":file_lama},
			{'$set':{"foto.$":filename}}
			)
		#if(record.modifiedCount > 0):
		#	return ('berhasil')
		#else:
		#	return ('Gagal')


	@staticmethod
	def getRandomAdvert():
		record=mongo.db.advert
		cursor=record.aggregate([
			{"$match":{"$or":[ {"unggulan":"true"},{"unggulan":"false"} ]}},
			{"$sample":{"size":120}}])
			
		output = []
		alamat_foto="https://s3-ap-southeast-1.amazonaws.com/propertytoday/"
		for doc in cursor:
			data=AdvertModel.jsonDumps(doc)
			get_id=(data['_id'])
			id_advert=(get_id['$oid'])
			kab=data['kab'].capitalize()
			provinsi=data['provinsi'].capitalize()
			output.append({
				"id":id_advert,
				"kategori":data['kategori'],
				"title":data['title'],
				"harga":data['harga'],
				"nego":data['nego'],
				"sertifikasi":data['sertifikasi'],
				"luas":data['luas']['luas_tanah'],
				"alamat":kab+" - "+provinsi,
				"foto":alamat_foto+data['foto'][0]}
				)
		return ({"succes":True,"data":output})



	
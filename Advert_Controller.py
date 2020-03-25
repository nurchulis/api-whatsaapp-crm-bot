import os
from flask_restful import Resource, reqparse
from flask import json, request
from run import app
from run import jsonify
from werkzeug import secure_filename
import random
import string
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from Advert_Models import AdvertModel
import boto3

file = reqparse.RequestParser()
data_property = reqparse.RequestParser()
data_update = reqparse.RequestParser()
data_gambarlama = reqparse.RequestParser()

def non_empty_string(s):
    if not s:
        raise ValueError("Must not be empty string")
    return s

file.add_argument('image', location=['headers', 'values'])
data_property.add_argument('title', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_property.add_argument('keterangan', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_property.add_argument('luas_bangunan', help= 'This field cannot be blank', required = False, type=non_empty_string)
data_property.add_argument('luas_tanah', help= 'This field cannot be blank', required = False, type=non_empty_string)
data_property.add_argument('kategori', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_property.add_argument('harga', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_property.add_argument('sertifikasi', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_property.add_argument('nego', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_property.add_argument('tersedia', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_property.add_argument('provinsi', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_property.add_argument('kab', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_property.add_argument('id_user', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_property.add_argument('unggulan', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_property.add_argument('alamat', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_gambarlama.add_argument('image_lama',help= 'This field cannot be blank', required = True, type=non_empty_string)

data_update.add_argument('title', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_update.add_argument('keterangan', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_update.add_argument('luas_bangunan', help= 'This field cannot be blank', required = False, type=non_empty_string)
data_update.add_argument('luas_tanah', help= 'This field cannot be blank', required = False, type=non_empty_string)
data_update.add_argument('kategori', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_update.add_argument('harga', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_update.add_argument('sertifikasi', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_update.add_argument('nego', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_update.add_argument('tersedia', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_update.add_argument('provinsi', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_update.add_argument('kab', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_update.add_argument('unggulan', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_update.add_argument('alamat', help= 'This field cannot be blank', required = True, type=non_empty_string)
data_update.add_argument('id_user', help= 'This field cannot be blank', required = True, type=non_empty_string)


def randomString():
	for x in range(100):
		return random.randint(1,1100000)

def allowed_file(filename):
	return '.' in filename and \
	filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def randomFile(stringLength=25):
    """Generate a random string of fixed length """
    letters= string.ascii_lowercase
    return ''.join(random.sample(letters,stringLength))
class Getadvert(Resource):
	def get(self,id_advert=None):
		if not id_advert:
			return 404
		return AdvertModel.GetAdvert(id_advert)
        
class Getadvert_title(Resource):
    def get(self):
        args = request.args
        cari=(args['cari'])
        id_advert=(args['id'])
        return AdvertModel.GetAdvert_by_title(cari,id_advert)

class countAdvert(Resource):
	def get(self):
		return AdvertModel.getCountAdvert()

class alladvert(Resource):
	def get(self):
		return AdvertModel.getAdverts()

class randomAdvert(Resource):
    def get(self):
        return AdvertModel.getRandomAdvert()

class searchAdvert(Resource):
	def get(self):
		args = request.args
		provinsi=(args['provinsi'])
		kab=(args['kab'])
		cari=(args['cari'])
		kategori=(args['kategori'])
		return AdvertModel.SearchAdvert(kategori,provinsi,kab,cari)

class PostAdvertaws(Resource):
    def post(self):
        # Get the name of the uplo
        uploaded_files = request.files.getlist("image")
        data =data_property.parse_args()
        title = data['title']
        keterangan =data['keterangan']
        luas_bangunan= data['luas_bangunan']
        luas_tanah= data['luas_tanah']
        kategori= data['kategori']
        harga = data['harga']
        tersedia = data['tersedia']
        nego = data['nego']
        sertifikasi = data['sertifikasi']
        provinsi = data['provinsi']
        kab = data['kab']
        id_user = data['id_user']
        alamat = data['alamat']
        unggulan = data['unggulan']
        filenames = []
        uniqe_name_data=randomString()
        ini=0
        for file in uploaded_files:
            # Check if the file is one of the allowed types/extensions
            if file and allowed_file(file.filename):
                # Make the filename safe, remove unsupported chars
                filename = secure_filename(file.filename)

                uniqe_name=randomFile()+filename
                s3 = boto3.resource('s3')
                s3.Bucket('propertytoday').put_object(Key=uniqe_name, Body=uploaded_files[ini])
                ini=ini+1
                filenames.append(uniqe_name)


        return AdvertModel.InsertAdvert(title, keterangan, luas_bangunan,luas_tanah, 
            harga, kategori,filenames, sertifikasi, nego, tersedia, provinsi, kab, id_user, alamat, unggulan)

class PostAdvert(Resource):
    def post(self):
        # Get the name of the uplo
        uploaded_files = request.files.getlist("image")
        data =data_property.parse_args()
        title = data['title']
        keterangan =data['keterangan']
        luas_bangunan= data['luas_bangunan']
        luas_tanah= data['luas_tanah']
        kategori= data['kategori']
        harga = data['harga']
        tersedia = data['tersedia']
        nego = data['nego']
        sertifikasi = data['sertifikasi']
        provinsi = data['provinsi']
        kab = data['kab']
        id_user = data['id_user']
        filenames = []
        uniqe_name_data=randomString()
        for file in uploaded_files:
            # Check if the file is one of the allowed types/extensions
            if file and allowed_file(file.filename):
                # Make the filename safe, remove unsupported chars
                filename = secure_filename(file.filename)

                uniqe_name=randomFile()+filename

                file.save(os.path.join(app.config['UPLOAD_FOLDER'], uniqe_name))
                filenames.append(uniqe_name)


       	return AdvertModel.InsertAdvert(title, keterangan, luas_bangunan,luas_tanah, 
       		harga, kategori,filenames, sertifikasi, nego, tersedia, provinsi, kab, id_user)


class UpdateAdvert(Resource):
    def post(self,id_advert= None):

        data =data_update.parse_args()
        title = data['title']
        keterangan =data['keterangan']
        luas_bangunan= data['luas_bangunan']
        luas_tanah= data['luas_tanah']
        kategori= data['kategori']
        harga = data['harga']
        tersedia = data['tersedia']
        nego = data['nego']
        sertifikasi = data['sertifikasi']
        provinsi = data['provinsi']
        kab = data['kab']
        alamat = data['alamat']
        unggulan = data['unggulan']
        id_user = data['id_user']

        return AdvertModel.UpdateAdvert(id_advert, title, keterangan, luas_bangunan,luas_tanah, 
            harga, kategori, sertifikasi, nego, tersedia, provinsi, kab, alamat, unggulan, id_user)

class UpdateFoto(Resource):
    def post(self, id_advert= None):
        uploaded_files = request.files.getlist("image")
        data =data_gambarlama.parse_args()
        #print data['image_lama']
        image_lama_array = []
        ini = request.form.getlist('image_lama')
        iniku =0
        if(uploaded_files):
            for file, file_lama in zip(uploaded_files, ini):
                # Check if the file is one of the allowed types/extensions
                if file and allowed_file(file.filename):
                    # Make the filename safe, remove unsupported chars
                    filename = secure_filename(file.filename)

                    uniqe_name=randomFile()+filename
                    s3 = boto3.resource('s3')
                    #print uniqe_name +"/"+file_lama 
                    AdvertModel.UpdateFoto(id_advert,file_lama,uniqe_name)
                    s3.Bucket('propertytoday').put_object(Key=uniqe_name, Body=uploaded_files[iniku])
                    #print file_lama
                    s3.Object('propertytoday', file_lama).delete()
                    iniku=iniku+1
                    #filenames.append(uniqe_name)

                else:
                    return('gagal')

        else:              
            return ('tidak ada')
        return ({'success':True})

class Hapusiklan(Resource):
    def get(self, id_advert= None):
        ini = AdvertModel.GetImageLopp(id_advert)
        theSum=0
        sets=0
        s3 = boto3.resource('s3')
        for gambar in ini:
            s3.Object('propertytoday', ini[sets]).delete()
            #print ini[sets]
            sets=sets+1

        return AdvertModel.deleteadvert(id_advert)

class Pilihan_advert(Resource):
    def get(self):
        return AdvertModel.Pilihan_advert()
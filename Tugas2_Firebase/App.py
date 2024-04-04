# app.py
# Required Imports
import os
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
import uuid
from datetime import datetime
# Initialize Flask App
app = Flask(__name__)
# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
produk_ref = db.collection('produk')

@app.route('/add', methods=['POST'])
def create():
    try:
        # Generate UUID for the document
        id = str(uuid.uuid4())
        # Set the generated UUID as ID for the document
        request.json['id'] = id
        # Add document to Firestore collection
        produk_ref.document(id).set(request.json)
        return jsonify({"success": True, "id": id}), 200
    except Exception as e:
        return f"An Error Occured: {e}"


@app.route('/list', methods=['GET'])
def read():
    try:
        # Check if ID was passed to URL query
        produk_id = request.args.get('id')
        if produk_id:
            # Fetch document by ID
            produk = produk_ref.document(produk_id).get()
            response = {
                "data": produk.to_dict(),
                "message": f"menampilkan data dengan ID {produk_id}",
                "data diambil pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return jsonify(response), 200
        else:
            # Fetch all documents
            all_produk = [doc.to_dict() for doc in produk_ref.stream()]
            response = {
                "data": all_produk,
                "message": "menampilkan semua produk",
                "data diambil pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return jsonify(response), 200
    except Exception as e:
        response = {
            "status": "error",
            "code": 500,
            "message": f"An Error Occurred: {e}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(response), 500

@app.route('/update', methods=['POST', 'PUT'])
def update():
    try:
        id = request.json['id']
        produk_ref.document(id).update(request.json)
        response = {
            "message": f"Produk dengan ID {id} berhasil di update.",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(response), 200
    except Exception as e:
        response = {
            "status": "error",
            "code": 500,
            "message": f"An Error Occurred: {e}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(response), 500

@app.route('/delete', methods=['GET', 'DELETE'])
def delete():
    try:
        # Check for ID in URL query
        produk_id = request.args.get('id')
        if produk_id:
            # Delete the document with the provided ID from Firestore
            produk_ref.document(produk_id).delete()
            response = {
                "message": f"produk dengan id {produk_id} berhasi dihapus",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return jsonify(response), 200
        else:
            response = {
                "message": "ID parameter is required",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return jsonify(response), 400
    except Exception as e:
        response = {
            "status": "error",
            "code": 500,
            "message": f"An Error Occurred: {e}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(response), 500

    

@app.route('/jenis', methods=['GET'])
def get_by_jenis():
    try:
        produk_jenis = request.args.get('jenis')
        if produk_jenis:
            # Query Firestore for documents with matching jenis
            query = produk_ref.where('jenis', '==', produk_jenis).stream()
            produk = [doc.to_dict() for doc in query]
            if produk:
                response = {
                    "message": f"menampilkan produk dengan jenis {produk_jenis}",
                    "data diambil pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": produk
                }
                return jsonify(response), 200
            else:
                response = {
                    "message": f"produk berjenis {produk_jenis} tidak ditemukan",
                    "data diambil pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                return jsonify(response), 404
        else:
            return jsonify({"error": "jenis parameter is required"}), 400
    except Exception as e:
        return f"An Error Occurred: {e}", 500



port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
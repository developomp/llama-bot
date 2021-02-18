import firebase_admin
from firebase_admin import credentials, firestore


class LlamaFirebase:
	# https://firebase.google.com/docs/firestore

	def __init__(self, certificate_path):
		# Document -> google.cloud.firestore_v1.document

		cred = credentials.Certificate(certificate_path)
		firebase_admin.initialize_app(cred, {"projectId": cred.project_id})
		self.db = firestore.client()

	def read_all(self):
		return {collection.id: {doc.id: doc.to_dict() for doc in collection.stream()} for collection in self.db.collections()}

	def read_collection(self, collection_name):
		return {doc.id: doc.to_dict() for doc in self.db.collection(u"%s" % collection_name).stream()}

	def create(self, collection_name, document_name, data_name, data):
		return self.db.collection(u"%s" % collection_name).document(u"%s" % document_name).set({"%s" % data_name: u"%s" % data}, merge=True)

	def read(self, collection_name, document_name):
		return self.db.collection(u"%s" % collection_name).document(u"%s" % document_name).get().to_dict()

	def delete(self, collection_name, document_name, data_name):
		return self.db.collection(u"%s" % collection_name).document(u"%s" % document_name).update({u"%s" % data_name: firestore.DELETE_FIELD})

	def exists(self, collection_name, discord_id):
		return True if self.db.collection(u"%s" % collection_name).document(u"%s" % discord_id).get().exists else False

	def write(self, collection_name, document_name, data_name, data, merge=True):
		if not isinstance(data, list):
			data = u"%s" % data
		return self.db.collection(u"%s" % collection_name).document(u"%s" % document_name).set({u"%s" % data_name: data}, merge=merge)

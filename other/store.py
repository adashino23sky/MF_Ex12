import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import pytz


game = "APEX"
now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
abc = "koreda"

cred = credentials.Certificate('chatapp-509c9-firebase-adminsdk-5tvj9-9106d52707.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
doc_ref = db.collection(u'chattest').document(str(now))
doc_ref.set({
    u'first': u'Adtaaaaaya',
    u'last': u'Lovetylace',
    u'born': 1815,
    game: game
})

import sys
import os
import datetime
from subprocess import call
from pymongo import MongoClient

type_object = sys.argv[1]
file_loc = sys.argv[2]

[username, hexid, filename] = file_loc.split('+++')
send_notif = True
rej_reason = None
if send_notif and len(sys.argv) >= 4:
    rej_reason = sys.argv[3]

client = MongoClient('127.0.0.1')
db = client.crackmesone

if type_object == "crackme":
	file_loc = "/home/crackmesone/crackmes.one/tmp/crackme/" + file_loc
	collection = db.crackme
	rating_diff = db.rating_difficulty
	rating_qual = db.rating_quality
	
elif type_object == "solution":
	file_loc = "/home/crackmesone/crackmes.one/tmp/solution/" + file_loc
	collection = db.solution
else:
	print("[-] I don't understand the type")
	sys.exit()

db_object = collection.find_one({'hexid': hexid})

if db_object is None:
	print("not found in db")
	os._exit(0)

print("[+] found in database !")
print(db_object)

# Cascade delete related data for crackme
if type_object == "crackme":
	# Delete all solutions for this crackme
	solution_count = db.solution.delete_many({"crackmeid": db_object["_id"]}).deleted_count
	print(f"[+] deleted {solution_count} solutions")

	# Delete all comments for this crackme
	comment_count = db.comment.delete_many({"crackmehexid": hexid}).deleted_count
	print(f"[+] deleted {comment_count} comments")

	# Delete all ratings for this crackme
	diff_count = db.rating_difficulty.delete_many({"crackmehexid": hexid}).deleted_count
	qual_count = db.rating_quality.delete_many({"crackmehexid": hexid}).deleted_count
	print(f"[+] deleted {diff_count} difficulty ratings and {qual_count} quality ratings")

# Delete the crackme/solution entry itself
collection.delete_one({'hexid': hexid})
print("[+] file deleted in db")

call(["rm", file_loc])
print("[+] rm " + file_loc)

if send_notif:
    print("[+] Sending " + type_object + " rejection notification!")
    notif_coll = db.notifications
    author_name = db_object["author"]
    if type_object == "solution":
        crackme_obj = db.crackme.find_one({'_id': db_object["crackmeid"]})
        notif_text = "Your solution for '" + crackme_obj["name"] + "' has been rejected!"
        if rej_reason is not None:
            notif_text += " Reason: " + rej_reason
        ins_id = notif_coll.insert_one({"user": author_name, "time": datetime.datetime.now(datetime.timezone.utc), "seen": False, "text": notif_text}).inserted_id
    elif type_object == "crackme":
        notif_text = "Your crackme '" + db_object["name"] + "' has been rejected!"
        if rej_reason is not None:
            notif_text += " Reason: " + rej_reason
        ins_id = notif_coll.insert_one({"user": author_name, "time": datetime.datetime.now(datetime.timezone.utc), "seen": False, "text": notif_text}).inserted_id
    # Set HexId here
    notif_coll.find_one_and_update({'_id': ins_id}, {'$set': {'hexid': str(ins_id)}})
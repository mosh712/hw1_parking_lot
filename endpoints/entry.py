from flask import request, jsonify
from datetime import datetime
import uuid
import logging
from database import get_connection
import json

def handle_entry():
    try:
        post_body = json.loads(request.data)
    except:
        return jsonify(error="Invalid POST request"), 400
    
    plate = post_body.get('plate', "")
    parking_lot = post_body.get('parkingLot', "")
    ticket_id = str(uuid.uuid4())
    entry_time = datetime.now()
    if parking_lot == "":
        return jsonify(error="Invalid parking request, , missing parking lot."), 400
    if plate == "": 
        return jsonify(error="Invalid parking request, missing plate number."), 400
    
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO entries (ticket_id, plate, parking_lot, entry_time)
                VALUES (%s, %s, %s, %s)
            """, (ticket_id, plate, parking_lot, entry_time))
        connection.commit()
    except: 
        logging.error(f"Failed to publish ticket {ticket_id}")
        connection.close()
        return jsonify(error=f"Failed to publish ticket {ticket_id}"), 400
    finally:
        connection.close()

    return jsonify(ticket_id=ticket_id)

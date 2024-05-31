from flask import request, jsonify
from datetime import datetime
from database import get_connection
import logging
import json 

def handle_exit():
    try:
        post_body = json.loads(request.data)
    except:
        return jsonify(error="Invalid POST request"), 400
    
    ticket_id = post_body.get('ticketId', "")
    if ticket_id == "":
        return jsonify(error="Invalid ticketId inserted"), 400
    
    exit_time = datetime.now()
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM entries WHERE ticket_id = %s and deletedAt is NULL
            """, (ticket_id,))
            entry_record = cursor.fetchone()

            if not entry_record:
                return jsonify(error="Invalid ticket ID"), 400

            parked_time = exit_time - entry_record['entry_time']
            total_minutes = parked_time.total_seconds() / 60
            charge = (total_minutes // 15) * (10 / 4) # $10 per hour, 15-minute increments
            if total_minutes % 15 > 0: 
                charge += 2.5
            cursor.execute("""
                UPDATE entries
                SET exit_time = %s, charge = %s, deletedAt = %s
                WHERE ticket_id = %s
            """, (exit_time, charge, exit_time, ticket_id))


        connection.commit()
    except:
        logging.error(f"Failed to exit ticket {ticket_id}")
        connection.close()
        return jsonify(error=f"Failed to exit ticket {ticket_id}"), 400
    finally:
        connection.close()

    return jsonify(
        plate=entry_record['plate'],
        total_parked_time=str(parked_time),
        parking_lot=entry_record['parking_lot'],
        charge=charge
    )

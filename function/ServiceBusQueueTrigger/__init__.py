import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # TODO: Get connection to database
    conn = psycopg2.connect(host = "",
                            port="5432",
                            user = "",
                            password = "",
                            dbname = "")
    try:
           # TODO: Get notification message and subject from database using the notification_id
        cur = conn.cursor()
        cur.execute("SELECT message,subject FROM notification WHERE id=%s;",(notification_id,))
        messagePlain, subject = cur.fetchone()
        # TODO: Get attendees email and name
        cur.execute("SELECT email,first_name FROM attendee;")
        attendees = cur.fetchall()
        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
          message = Mail(
              from_email='test@email.com',
              to_emails=attendee[0],
              subject='{}: {}'.format(attendee[1], subject),
              html_content=messagePlain)
          try:
              sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
              response = sg.send(message)
              print(response.status_code)
              print(response.body)
              print(response.headers)
          except Exception as e:
              print(str(e))
        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        total_attendees = 'Notified {} attendees'.format(len(attendees))
        completed_date = datetime.utcnow()
        cur.execute("UPDATE notification SET status = %s, completed_date =%s WHERE id=%s;", (total_attendees,completed_date,notification_id))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        conn.close()
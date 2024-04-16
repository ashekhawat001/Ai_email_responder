import os
import google.generativeai as genai
import time
from simplegmail import Gmail
from simplegmail.query import construct_query
from dotenv import load_dotenv


load_dotenv()
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

promt="""your role is to reply to customers of XYZ marketing agency. Write a professional and courteous email response to a customer inquiry about or requesting support. Write the email based on or as a reply to the text labeled 'input email' given below. In the email, be sure to:

    
    Acknowledge the customer's concern and thank them for contacting you.
    Briefly explain the issue based on the the email received
    Offer a solution if possible, or outline the next steps that will be taken to resolve the issue.
    Personalize the closing by including the customer's name (if available).
    don't end the email with [your name] instead use the company's name

    IMPORTANT -- NOT INCLUDE PLACE HOLDERS FOR DATA NOT AVAILBLE TO YOU, example [name], OR DATA THAT YOU INTEND TO FILL YOURSELF, ALWAYS GIVE PRESICSE RESPONSE DO'NT LEAVE ANYTHING UNFINISHED AS THESE ARE THE ACTUAL FINAL RESPONSE GOING OUT EXACTLY AS YPU WRITE THEM


    if body of email is empty then don't generate any response
    Also keep in kind to give the generated text in proper formamting by using next line "\" + n etc

    but keep in mind customers can inquire about other things like jobs posted by the agency or updates on ongoing work with the agency in those cases dont spin up facts just tell them to wait and that someone will resolve their query shortly
    IF THE query by customer is irrelevant keep the reply to one or two line

    input email :"""

gmail = Gmail()



query_params={
    "newer_than" : (1, 'day')
}




while True:
    messages = gmail.get_unread_messages(query=construct_query(query_params))
    count=0
    for message in messages:
        with open("email_store.txt", "w", encoding='utf-8') as store:
            fields = ["From", "Subject", "Date"]
            values = [message.sender, message.subject, message.date]

            for field, value in zip(fields, values):
                store.write(f"{field}: {value}\n")
            if message.plain:            
                store.write("body" + message.plain)
            else:
                store.write("body: ")
        count+=1
        
        with open('email_store.txt', 'r', encoding='utf-8') as store:
            email_content = store.read() 

        response = model.generate_content(str(promt+email_content))

        msg_html = str(response.text)
        msg_html = msg_html.replace("\n", "<br>")
        
        params = {
            "to": message.sender,
            "sender": message.recipient,
            "subject": "re"+ message.subject,
            "msg_html": msg_html,
            
        }

        message_to_send = gmail.send_message(**params)  # equivalent to send_message(to="you@youremail.com", sender=...)
        mark_as_read = message.mark_as_read()
        print(response.text)
        print("Message sent successfully")
    print("finished Found "+ str( count) +" messages")       
    time.sleep(10)    



    


    
    

   # print("Message Body: " + message.html)  # or message.html
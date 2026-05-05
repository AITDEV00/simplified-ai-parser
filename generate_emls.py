import email.message

msg = email.message.EmailMessage()
msg.set_content("This is a simple sample email body.\nIt is used for testing the .eml parser.\nThank you.")
msg['Subject'] = 'Sample Test Email'
msg['From'] = 'sender@example.com'
msg['To'] = 'receiver@example.com'

with open("tests/files/email/sample1.eml", "w") as f:
    f.write(msg.as_string())

msg2 = email.message.EmailMessage()
msg2.set_content("This is another test email.\nHave a great day!")
msg2.add_alternative("""\
<html>
  <head></head>
  <body>
    <p>This is another <b>test email</b>.</p>
    <p>Have a great day!</p>
  </body>
</html>
""", subtype='html')
msg2['Subject'] = 'HTML Test Email'
msg2['From'] = 'html_sender@example.com'
msg2['To'] = 'receiver@example.com'

with open("tests/files/email/sample2.eml", "w") as f:
    f.write(msg2.as_string())

print("Successfully created sample .eml files.")

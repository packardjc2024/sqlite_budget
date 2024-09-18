import imapclient
import pyzmail
import re
import calendar
from datetime import datetime
import os


class EmailChecker:
    def __init__(self):
        self.expenses = []

    def get_emails(self, password, username, client):
        imap_obj = imapclient.IMAPClient(client, ssl=True)
        imap_obj.login(username=username, password=password)

        # Select the inbox mail folder
        imap_obj.select_folder('INBOX', readonly=True)

        uids = imap_obj.search([['FROM', username],  # Because I emailed myself as an example
                        ['SUBJECT', 'Credit Card Example Testing']])

        for uid in uids:
            # Get the raw data from the email with a given identifier
            raw_messages = imap_obj.fetch(uid, 'BODY[]')

            # Format the raw data
            message = pyzmail.PyzMessage.factory(raw_messages[uid][b'BODY[]'])
            body = (message.html_part.get_payload().decode(message.html_part.charset))

            # Gets the date and formats it
            date_regexp = re.compile(r"you that on\s(.*?)\s(\d{1,2}),\s(\d{4}),\sat")
            date = date_regexp.search(body)
            months = {month: index for index, month in enumerate(calendar.month_name) if month == date.group(1)}
            formatted_date = f"{months[date.group(1)]}/{date.group(2)}/{date.group(3)}"
            formatted_date = datetime.strptime(formatted_date, '%m/%d/%Y')
            formatted_date = datetime.strftime(formatted_date, '%m/%d/%Y')

            # Gets the amount
            amount_regexp = re.compile(r'of\s\$(\d*?\.\d{1,2})\swas')
            amount = amount_regexp.search(body)

            # Gets the merchant purchased from
            merchant_regexp = re.compile(r',\sat\s(.*?),\sa\spending')
            merchant = merchant_regexp.search(body)

            self.expenses.append([amount.group(1), formatted_date, merchant.group(1)])

        # Log out of the icloud mail server
        imap_obj.logout()
        return self.expenses

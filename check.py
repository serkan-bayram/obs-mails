import requests
from bs4 import BeautifulSoup
import json

LOGIN_URL = "https://obs.bilecik.edu.tr/login.aspx"
MAILS_URL = "https://obs.bilecik.edu.tr/ogrenci/ogrencianasayfa.aspx/GelenKutusu"
READ_MAIL = "https://obs.bilecik.edu.tr/ogrenci/ogrencianasayfa.aspx/MesajOku"


def login(session):
    first_request = session.get(LOGIN_URL)

    soup = BeautifulSoup(first_request.content, 'html.parser')

    form = soup.find(id="form1")

    # Values that we need to pass as form data
    viewstate = form.find(id="__VIEWSTATE").get("value")
    viewstategenerator = form.find(id="__VIEWSTATEGENERATOR").get("value")
    eventvalidation = form.find(id="__EVENTVALIDATION").get("value")

    try:
        with open("auth.txt", "r") as f:
            lines = f.readlines()
            username = lines[0]
            password = lines[1]
    except FileNotFoundError:
        print("Create an auth.txt file and enter your credentials\nFirst line is username and second line is password")
        return False

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://obs.bilecik.edu.tr',
        'Pragma': 'no-cache',
        'Referer': 'https://obs.bilecik.edu.tr/login.aspx',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
    }

    payload = {"txtLoginKullaniciAdi": username.strip(),
               "txtLoginSifre": password.strip(),
               "__VIEWSTATE": viewstate,
               "__VIEWSTATEGENERATOR": viewstategenerator,
               "__EVENTVALIDATION": eventvalidation,
               "__LASTFOCUS": '',
               "__EVENTTARGET": '',
               "__EVENTARGUMENT": '',
               "btnGiris": "Giriş"
               }

    login_request = session.post(
        LOGIN_URL, headers=headers, data=payload)

    soup = BeautifulSoup(login_request.content, 'html.parser')

    print(soup.prettify())

    return login_request.status_code


# Gets the latest five mail from OBS
def get_last_five_mails(session):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json; charset=utf-8',
        'Origin': 'https://obs.bilecik.edu.tr',
        'Pragma': 'no-cache',
        'Referer': 'https://obs.bilecik.edu.tr/ogrenci/ogrencianasayfa.aspx',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
    }

    mails_request = session.post(MAILS_URL, headers=headers)

    if mails_request.status_code != 200:
        print(mails_request.status_code)
        return [], False

    mails = BeautifulSoup(
        mails_request.content, 'html.parser')

    # Mails
    json_data = mails.prettify()

    parsed_json = json.loads(json_data)

    messages = json.loads(parsed_json["d"])

    last_five = []
    for i in range(0, 5):
        # print("Message No:", messages[i]["MesajNo"])
        # print("Alan:", messages[i]["Alan"])
        # print("Konu:", messages[i]["Konu"])
        # print("Tarih:", messages[i]["Tarih"])
        # print("---------------")
        last_five.append(messages[i]["MesajNo"])

    return last_five, True


# Saves the latest five mails
def save_last_five_mails(last_five):
    with open("lastFiveMails.txt", "w") as f:
        for mail in last_five:
            f.write(f"{mail}\n")


# Gets the new mail message content
def get_new_mails(mails, session):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json; charset=UTF-8',
        'Origin': 'https://obs.bilecik.edu.tr',
        'Pragma': 'no-cache',
        'Referer': 'https://obs.bilecik.edu.tr/ogrenci/ogrencianasayfa.aspx',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
    }

    messages = []

    for mail in mails:
        payload = {"MesajNo": str(mail)}

        request = session.post(READ_MAIL, json=payload, headers=headers)

        if request.status_code != 200:
            return [], False

        message = BeautifulSoup(request.content, 'html.parser')

        json_data = message.prettify()

        parsed_json = json.loads(json_data)

        message = json.loads(parsed_json["d"])

        new_message = {
            "subject": message["Konu"], "content": message["Icerik"]}

        messages.append(new_message)

    return messages, True


# Checks for new mails, compares lastFiveMails.txt and last_five from get_last_five_mails
def is_there_new_mail(new_last_five, session):
    old_last_five = []
    with open("lastFiveMails.txt", "r") as f:
        for mail in f.readlines():
            old_last_five.append(int(mail.strip()))

    old_last_five = set(old_last_five)
    new_last_five = set(new_last_five)

    new_mails = list(new_last_five - old_last_five)

    if len(new_mails) > 0:
        messages, response = get_new_mails(mails=new_mails, session=session)

        if not response:
            print("Can't get mails.")
            return [], False
        else:
            return messages, True

    return [], False


def check():

    session = requests.Session()

    status = login(session=session)

    if status != 200:
        return False, "Can't log in."

    print("Logged in.")

    last_five, response = get_last_five_mails(session=session)

    if not response:
        return False, "Can't get mails from OBS."

    messages, response = is_there_new_mail(
        new_last_five=last_five, session=session)

    if not response:
        return True, "No new mails."

    save_last_five_mails(last_five=last_five)
    print("Last five mails are saved.")

    # New mails will be shown here.
    print(messages)
    return True, messages

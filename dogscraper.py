import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import smtplib
import os
from email.mime.text import MIMEText

load_dotenv()
url = os.getenv("URL")
user_agent = os.getenv("USER_AGENT")
sender = os.getenv("SENDER")
recipients = os.getenv("RECIPIENTS")
subject = os.getenv("SUBJECT")
password = os.getenv("PASSWORD")
mail_server = os.getenv("MAIL_SERVER")
base_url = os.getenv("BASE_URL")

with open("./known_dogs.txt", "r") as f:
    known_dogs = f.read().splitlines()
    print(f"Known dogs: {known_dogs}")


def scrapeDogs():
    headers = {"User-agent": user_agent}
    page = httpx.get(f"{base_url}/our-dogs", headers=headers)
    soup = BeautifulSoup(page, "html.parser")
    lists = soup.find_all("li")
    html = ""
    for i in lists[1:]:
        try:
            name = i.find_all("p")[0].string
            print(f"Checking {name} against known dogs...")
            if name not in known_dogs:
                known_dogs.append(name)
                image_url = i.find("img")["src"]
                link = i.find("a")["href"]
                description = i.find_all("p")[1].string
                html = (
                    html
                    + f"""
                        <head>
                        <h1><a href="{base_url}{link}">{name}</a></h1>
                        <h3>{description}</h3>
                        <img src="{image_url}"
                        style="width:250px;height:250px;">
                        </head>\n
                    """
                )
                with open("./known_dogs.txt", "a") as f:
                    f.write(f"{name}\n")
        except:
            continue
    return html


def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipients
    with smtplib.SMTP_SSL(mail_server, 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")


if __name__ == "__main__":
    html = str(scrapeDogs())
    if len(html) > 0:
        send_email(subject, html, sender, recipients, password)

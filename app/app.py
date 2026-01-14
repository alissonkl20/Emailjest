from flask import Flask, jsonify, render_template, request
import imaplib
import email
from email.header import decode_header
import re
from dotenv import load_dotenv
import os
from functools import lru_cache

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa o app Flask
app = Flask(__name__)

# Função para conectar ao servidor de e-mail e buscar mensagens
@lru_cache(maxsize=32)
def fetch_emails():
    # Configurações do servidor de e-mail
    username = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")

    if not username or not password:
        raise ValueError("As credenciais de e-mail não foram definidas no arquivo .env")

    # Conecta ao servidor IMAP
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    mail.select("inbox")

    # Busca todos os e-mails na caixa de entrada
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    emails = []

    for email_id in email_ids[-9:]:  # Busca os últimos 9 e-mails
        res, msg = mail.fetch(email_id, "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # Decodifica o e-mail
                msg = email.message_from_bytes(response[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                from_ = msg.get("From")

                # Extrai o corpo do e-mail
                # Decodifica o corpo do e-mail com tratamento de erros
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            body = part.get_payload(decode=True).decode(errors="replace")
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors="replace")

                # Adiciona o e-mail processado à lista
                emails.append({"subject": subject, "from": from_, "body": body})

    mail.logout()
    return emails

# Função para resumir o conteúdo do e-mail
def summarize_email(body):
    # Remove quebras de linha e espaços extras
    body = re.sub(r"\s+", " ", body)
    # Retorna um resumo simples (por exemplo, os primeiros 100 caracteres)
    return body[:100] + "..." if len(body) > 100 else body

# Rota principal para exibir os resumos dos e-mails
@app.route("/emails", methods=["GET"])
def get_emails():
    try:
        emails = fetch_emails()
        summarized_emails = [
            {
                "subject": email["subject"],
                "from": email["from"],
                "summary": summarize_email(email["body"]),
            }
            for email in emails
        ]

        # Renderiza o template HTML com os e-mails
        return render_template("emails.html", emails=summarized_emails)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
FROM python:3.10 
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY bot.py .

EXPOSE 80

CMD [ "gunicorn", "bot:app", "--workers=1", "--bind", "0.0.0.0:80", "--capture-output", "--access-logfile", "-", "--error-logfile", "-" ]
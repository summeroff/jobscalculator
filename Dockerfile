# Dockerfile
FROM python:3.8-slim-buster

WORKDIR /app

COPY . .

RUN pip install flask

# Run the database initialization script
RUN python db.py

CMD [ "python", "app.py" ]

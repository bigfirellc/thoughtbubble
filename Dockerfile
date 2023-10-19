# Your Python version
FROM python:3.10

# Web port of the application
EXPOSE 5000

# Install your application
WORKDIR /app
COPY /app/thoughtbubble/src/web /app
RUN pip install -r requirements.txt

# Start up command
CMD python main.py
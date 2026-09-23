FROM python:3.12-slim
RUN pip install --no-cache-dir flask==3.0.3
COPY app.py /app/app.py
COPY templates /app/templates
COPY static /app/static
WORKDIR /app
EXPOSE 5000
CMD ["python3", "app.py"]

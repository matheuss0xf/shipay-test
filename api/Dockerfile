FROM python:3.12.6-slim

WORKDIR /app

COPY ./api/ /app/

RUN pip install pipenv

RUN pipenv install --system --deploy

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]

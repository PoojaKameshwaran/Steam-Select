FROM apache/airflow:2.9.2

# Set the AIRFLOW_HOME environment variable
ENV AIRFLOW_HOME=/opt/airflow

# Set the working directory to your mounted project folder
WORKDIR ${AIRFLOW_HOME}/steam-select

# Copy everything from the local project directory to the container's working directory
COPY .env ${AIRFLOW_HOME}/steam-select/.env

COPY requirements.txt .
RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt

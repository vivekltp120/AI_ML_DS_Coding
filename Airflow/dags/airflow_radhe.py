from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta

def radhe_radhe():
    print("Radhe Radhe!")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.today(),
    'email_on_failure': True,
    'email_on_retry': False,
    'email_on_success': True,
    'retries': 1,
    'email': ['vivekltp120@gmail.com'],
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'radhe_radhe',
    default_args=default_args,
    description='A simple radhe radhe DAG', 
    schedule=None,
    catchup=False,
)   

hello_task = PythonOperator(
    task_id='radhe_radhe',
    executer='LocalExecutor',
    provide_context=True,
    python_callable=radhe_radhe,
    dag=dag,
)   

show_task = BashOperator(
    task_id='show_task',
    executer='LocalExecutor',
    provide_context=True,
    bash_command='echo "Hello from Airflow!" && echo "Radhe Radhe!" && ls -lhs >> airflow_radhe.txt',
    dag=dag,
)

hello_task >> show_task
# from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.operators.email import EmailOperator

# def send_slack_notification(slack_msg, webhook_token):
#     """
#     Function to send Slack notifications
#     """
#     return SlackWebhookOperator(
#         task_id='send_slack_notification',
#         http_conn_id='slack_connection',
#         webhook_token=webhook_token,
#         message=slack_msg,
#         username='airflow'
#     )

def notify_success(context, message = "The task succeeded!"):
    success_email = EmailOperator(
        task_id='success_email',
        to='steamrecommendation83@gmail.com',
        subject='Success Notification from Airflow',
        html_content=f'<p>{message}.</p>',
        dag=context['dag']
    )
    success_email.execute(context=context)

def notify_failure(context, message = "The task failed."):
    failure_email = EmailOperator(
        task_id='failure_email',
        to='steamrecommendation83@gmail.com',
        subject='Failure Notification from Airflow',
        html_content=f'<p>{message}</p>',
        dag=context['dag']
    )
    failure_email.execute(context=context)
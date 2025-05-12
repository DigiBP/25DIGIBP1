import requests
import time
from datetime import date
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from os.path import exists

CAMUNDA_ENGINE_URL = "https://digibp.engine.martinlab.science/engine-rest"
TOPIC = "store-feedback-in-db"
WORKER_ID = "python-worker-1"
EXCEL_FILE = "form_data.xlsx"

# openpyxl formating
bold = Font(bold=True)


def fetch_and_lock():
    response = requests.post(f"{CAMUNDA_ENGINE_URL}/external-task/fetchAndLock", json={
        "workerId": WORKER_ID,
        "maxTasks": 1,
        "usePriority": False,
        "topics": [{
            "topicName": TOPIC,
            "lockDuration": 10000,
            "tenantId": "25DIGIBP12"
        }]
    })
    return response.json()


def complete_task(task_id, variables):
    requests.post(f"{CAMUNDA_ENGINE_URL}/external-task/{task_id}/complete", json={
        "workerId": WORKER_ID,
        "variables": {}
    })


def write_to_excel(data: dict, task_id):
    if exists(EXCEL_FILE):
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active

        ws.cell(1, 1, "submissionID").font = bold
        ws.cell(1, 2, "feedbackDate").font = bold
        ws.cell(1, 3, "feedbackType").font = bold
        ws.cell(1, 4, "query").font = bold
        ws.cell(1, 5, "email").font = bold
        ws.cell(1, 6, "phone").font = bold
        ws.cell(1, 7, "firstName").font = bold
        ws.cell(1, 8, "lastName").font = bold
        ws.cell(1, 9, "feedbackText").font = bold
        ws.cell(1, 10, "needsClarification").font = bold
        ws.cell(1, 11, "urgency").font = bold
        ws.cell(1, 12, "impactScope").font = bold
        ws.cell(1, 13, "forwardToDepartment").font = bold
        ws.cell(1, 14, "linkToAdditForm").font = bold
        ws.cell(1, 15, "reminderSent").font = bold
        ws.cell(1, 16, "status").font = bold


    # get next empty row
    row = ws.max_row + 1

    print(data)

    feedback_date = str(date.today().strftime("%d.%m.%Y"))

    # write new data to excel
    ws.cell(row, 1, task_id)
    ws.cell(row, 2, feedback_date)
    ws.cell(row, 5, data["email"])
    ws.cell(row, 6, data["phone"])
    ws.cell(row, 7, data["firstName"])
    ws.cell(row, 8, data["lastName"])
    ws.cell(row,9,data["feedbackText"])


    # save excel
    wb.save(EXCEL_FILE)
    print("Data written to Excel.")


while True:
    tasks = fetch_and_lock()
    for task in tasks:
        task_id = task['id']
        variables = {k: v['value'] for k, v in task['variables'].items()}
        print(f"Fetched task {task_id} with variables {variables}")

        write_to_excel(variables, task_id)
        complete_task(task_id, variables)
    time.sleep(5)
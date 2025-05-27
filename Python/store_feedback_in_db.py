import time
import traceback
from pathlib import Path
from art import art
from datetime import date
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from os.path import exists

from SupportFunctions import *



TOPIC = "store_feedback_in_db"
WORKER_ID = "python-worker-17"



# openpyxl formating
bold = Font(bold=True)


def write_to_excel(data: dict, business_key):
    if exists(EXCEL_FILE):
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active

        ws.cell(1, 1, "businessKey").font = bold
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
        ws.cell(1, 17, "measuresTaken").font = bold


    # get next empty row
    row = ws.max_row + 1

    print(data)

    feedback_date = str(date.today().strftime("%d.%m.%Y"))

    # write new data to excel
    ws.cell(row,1, business_key)
    ws.cell(row,2, feedback_date)
    ws.cell(row,5, data["email"])
    ws.cell(row,6, data["phone"])
    ws.cell(row,7, data["firstName"])
    ws.cell(row,8, data["lastName"])
    ws.cell(row,9, data["feedbackText"])
    ws.cell(row,16, "open")

    # save excel
    wb.save(EXCEL_FILE)
    print("Data written to Excel.")



if __name__ == "__main__":
    print(f"Worker \"{Path(__file__).name}\" started — polling Camunda...")
    try:
        time.sleep(2)
        while True:
            try:
                for task in fetch_and_lock(worker_id=WORKER_ID, topic=TOPIC):
                    business_key = task.get("businessKey", "")
                    task_id = task["id"]
                    variables = {k: v["value"] for k, v in task["variables"].items()}
                    print(f"Worker \"{Path(__file__).name} fetched task {task_id} with business key {business_key}")
                    try:
                        write_to_excel(data=variables, business_key=business_key)
                        complete_task(task_id=task_id, variables=variables, worker_id=WORKER_ID)
                        print(f"Worker \"{Path(__file__).name} completed task {task_id} with business key {business_key}")
                    except Exception as exc:
                        print(f"Error in task {task_id}: {exc} {art('confused scratch')}")
                        traceback.print_exc()

            except Exception as exc:
                print(f"Fetch error: {exc} {art('table flip2')}")
                traceback.print_exc()

            time.sleep(5)

    except KeyboardInterrupt:
        pass
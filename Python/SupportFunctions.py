import pandas as pd


def get_date(submission_id):

    data = pd.read_excel("form_data.xlsx")
    data = data.set_index("submissionID")

    return data.loc[submission_id, "feedbackDate"]


"""

Launch all feedback management worker scripts as background subprocesses.

This script starts each defined Python worker in a separate process using `subprocess.Popen`.
It displays a startup banner, tracks all subprocesses, and ensures clean shutdown
on keyboard interrupt (Ctrl+C). Each worker handles a specific task in the
feedback management system (e.g., storing feedback, sending emails, updating Excel, etc.).


"""

import subprocess
import time
from art import tprint, art


if __name__ == "__main__":


    service_files = [
        "prepare_feedback_supplementation_form.py",
        "prepare_measure_documentation_form.py",
        "process_feedback_supplementation.py",
        "save_classification_in_db.py",
        "save_query_in_db.py",
        "save_measures_taken_in_db.py",
        "send_department_mail.py",
        "send_department_reminder_mail.py",
        "send_feedback_received.py",
        "send_information_ceo.py",
        "send_processed_soon.py",
        "send_query_mail.py",
        "send_query_reminder_mail.py",
        "send_thank_you_message.py",
        "send_feedback_implemented.py",
        "send_withdrawal_message.py",
        "set_review_board_in_db.py",
        "set_withdrawn_in_db.py",
        "store_feedback_in_db.py",
        "terminate_terminated_instances.py"
    ]

    # Store subprocesses to manage them later if needed
    processes = []

    tprint("25-DIGIBP-1", font="small")
    print(f"Starting all workers...\n\n{art('hugger')}\n\n")
    time.sleep(2)

    try:
        for file in service_files:
            p = subprocess.Popen(["python", file])
            processes.append(p)

        while True:
            time.sleep(5)

    # Handle safe shutdown
    except KeyboardInterrupt:
        print("\nStopping all workers...")
        for p in processes:
            p.kill()

        for p in processes:
            p.wait()

        time.sleep(2)
        print(f"\n{art('wizard2')} Woosh")
        print("\nAll workers stopped.")

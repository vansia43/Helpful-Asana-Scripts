import asana
import csv
import pandas as pd

personal_access_token = <ADD_YOUR_ACCESS_TOKEN>

def get_all_tasks(output_file, project_id):
    '''Obtains all tasks for project and write to a csv file defined in the function variables'''
    file = open(output_file, "w")
    fieldnames= ["gid", "name", "completed", "due_on"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    result = client.tasks.get_tasks_for_project(project_id, opt_fields=["name", "completed", "due_on"], opt_pretty=True)

    writer.writerows(list(result))
    file.close()
    
def clean_task_file(input_file):
    '''Opens created csv and creates a new, cleaned csv with only completed tasks using pandas'''
    df = pd.read_csv(input_file)
    df_complete = df[df["completed"] == True]
    df_no_date = df_complete[df_complete["due_on"].isnull()]
    return df_no_date

project_id = "<project_id>" 

client = asana.Client.access_token(personal_access_token)
get_all_tasks("output.csv", project_id)
clean_task_file("output.csv")

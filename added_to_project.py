import asana
from logging import exception
import datetime
import time
import os

# class for changing terminal output colors; helpful when run as a scheduled job
class bcolors:
    ERROR = "\033[91m"
    ENDC = "\033[0m"
    OKGREEN = "\033[92m"
    
# initialize timer to calculate job length
start_time = time.time()


# access token, project, added to project custom field; create this custom field in the asana project and ensure the field type is set to date
asana_access_token = "your_asana_access_token"
project_id = "project_gid"
created_field = "created_field_gid"


# connect to asana client
client = asana.Client.access_token(asana_access_token)

try:
  # retrieve gids for all tasks in project and unpack generator to list
  tasks = [x["gid"] for x in client.tasks.get_tasks_for_project(project_id, opt_pretty=True)]
  # for debugging specific tasks
  # tasks = ["insert_task_gid", "insert_task_gid"]
except Exception as e:
    # check that Asana is still online (https://status.asana.com/) or if the Asana API Key is invalid
    print("Couldn't retrieve tasks from Asana. Check that the API is available or verify your API key is active.")


print("Processing tasks...")
# variable to provide total number of updated tasks at the end of job
updated_tasks = 0

for task_id in tasks:
    try:
        # retrieve all stories for a given task; added to project is considered a story
        # stories are viewable in an asana task's comment stream
        stories = client.tasks.stories(task_id)
        # get the most recent added to project story for the project board
        latest_added_story = next((story for story in reversed([x for x in stories]) if story["resource_subtype"] == "added_to_project" and project_id in story["text"]), None)
        if latest_added_story is not None:
            # dates are returned with the full date and min/second; convert the date to YYYY-MM-DD
            created_at = datetime.datetime.strptime(latest_added_story["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            date_str = created_at.strftime("%Y-%m-%d")
            # retrieve the current date in the field if there is one to compare to the new one
            current_date = client.tasks.get_task(task_id, opt_fields=("custom_fields.display_value"), opt_pretty=True) 
            # set to None if there is no current date
            current_date_str = None
            for field in current_date["custom_fields"]:
                if field["gid'"] == created_field:
                    if field["display_value"] is not None:
                        # convert date for comparison
                        current_date = datetime.datetime.strptime(field["display_value"], "%Y-%m-%dT%H:%M:%S.%fZ")
                        current_date_str = current_date.strftime("%Y-%m-%d")
                    break
            # if there is no date or if the latest added story date does not equal the existing date
            if current_date_str is None or current_date_str != date_str:
                print(task_id, "==>", date_str)
                # update custom field
                update_field = client.tasks.update_task(task_id, {"custom_fields": {created_field: {"date": date_str}}}, opt_pretty=True)
                updated_tasks += 1
    except Exception as e:
        # tasks with errors; check if there was no added to project story 
        print(f"{bcolors.ERROR} ==> Unable to process task {task_id}: {e}{bcolors.ENDC}")

end_time = time.time()
elapsed_time = round(end_time - start_time, 2)

# total number of tasks updated plus elapsed time on job
print(bcolors.OKGREEN + f"{updated_tasks} task{'s' if updated_tasks != 1 else ''} updated in {elapsed_time} seconds" + bcolors.ENDC)

print("Job complete.")


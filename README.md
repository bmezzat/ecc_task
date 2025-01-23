## Install Pre-requisite packages
pip install -r /requirements.txt

## Create SQLite DB and update table with report values
```
py update_db.py
```

## Run script
```
py main.py
```

## Milestones
- Three tables are configured on models.py
  - CC050 which contains the EOD reports 
  - CI050 which contains the SOD/Intraday reports
  - ErrorChecks which logs any mismatch found 
- update_db.py creates the DB tables and update the CC050 and CI050 tables from the cc050.csv and ci050.csv files respectively.
- main.py runs the needed checks
- When running main.py user is requested to enter the needed check and date
- Needed reports will be fetched from DB, and rows with same clearing_member, account and margin_type are merged together using pandas
- Then margin values from both reports will be compared if any mismatch found
  - Table ErrorCheck will be updated with the report name, date and mismatch values
  - An email will be sent to a predefined mail list using the function send_email in email_helper.py
    - The email template used is found in email_template.html
- Any error in the code or logs like mismatch will also be logged in the console and in file app.log using the setup_logger function in logger.py

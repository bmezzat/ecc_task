import pandas as pd
from datetime import datetime
from models import SessionLocal, Base, engine, CC050, CI050
from sqlalchemy.orm import Session
from logger import setup_logger

logger = setup_logger(__name__)


def get_cc050_rows(all_data):
    entries = []
    for _, row in all_data.iterrows():
        try:
            new_entry = CC050(
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                clearing_member=row['clearing_member'],
                account=row['account'],
                margin_type=row['margin_type'],
                margin=row['margin']
            )
            entries.append(new_entry)
        except Exception as e:
            logger.error(f"Error processing row: {row} for table CC050. Error: {e}")
    return entries


def get_ci050_rows(all_data):
    entries = []
    for _, row in all_data.iterrows():
        try:
            new_entry = CI050(
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                time=datetime.strptime(row['time'], '%H:%M:%S').time(),
                clearing_member=row['clearing_member'],
                account=row['account'],
                margin_type=row['margin_type'],
                margin=row['margin']
            )
            entries.append(new_entry)
        except Exception as e:
            logger.error(f"Error processing row: {row} for CI050. Error: {e}")
    return entries


def update_table():
    db: Session = SessionLocal()
    csv_files = [
        {'file_name': 'cc050.csv', 'callback_function': get_cc050_rows, 'table': CC050},
        {'file_name': 'ci050.csv', 'callback_function': get_ci050_rows, 'table': CI050}
    ]

    for csv_file in csv_files:
        try:
            db.query(csv_file['table']).delete()
            all_data = pd.read_csv(csv_file['file_name'])
            entries = csv_file['callback_function'](all_data)
            db.bulk_save_objects(entries)
            logger.info(f"Data for {csv_file['file_name']} inserted successfully.")
        except Exception as e:
            logger.error(f"Error processing file {csv_file['file_name']}: {e}")

    db.commit()
    db.close()


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    update_table()

import pandas as pd
from datetime import datetime, timedelta, date
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import SessionLocal, CC050, CI050, ErrorChecks
from email_helper import send_email
from logger import setup_logger

logger = setup_logger(__name__)


def merge_reports_and_compare(db, report_date, subject, ci050_query, cc050_query):
    ci050_data = pd.read_sql(ci050_query.statement, db.bind)
    cc050_data = pd.read_sql(cc050_query.statement, db.bind)
    merged_date = pd.merge(
        ci050_data,
        cc050_data,
        on=['clearing_member', 'account', 'margin_type'],
        suffixes=('_ci050', '_cc050'),
        how='outer'
    )
    merged_date['status'] = merged_date.apply(
        lambda row: (
            'Mismatch' if pd.notna(row['margin_ci050']) and pd.notna(row['margin_cc050']) and row['margin_ci050'] !=
                          row['margin_cc050']
            else 'Missing in cc050' if pd.isna(row['margin_cc050'])
            else 'Missing in ci050' if pd.isna(row['margin_ci050'])
            else 'Match'
        ),
        axis=1
    )

    mismatch_rows = merged_date[merged_date['status'] != 'Match']
    if not mismatch_rows.empty:
        for index, row in mismatch_rows.iterrows():
            logger.info(f"On {report_date} Clearing member '{row['clearing_member']}', account '{row['account']}' and margin type "
                  f"'{row['margin_type']}', cc050 report value {row['margin_cc050']} where ci050 report value "
                  f"{row['margin_ci050']}")
            mismatch_entry = ErrorChecks(
                date=report_date,
                report=subject,
                clearing_member=row['clearing_member'],
                account=row['account'],
                margin_type=row['margin_type'],
                margin_ci050=row['margin_ci050'],
                margin_cc050=row['margin_cc050']
            )
            db.add(mismatch_entry)
        db.commit()
    else:
        logger.info("No mismatch found")

    return mismatch_rows


def first_ci050_with_last_day_cc050(db: Session, report_date: date):
    logger.info("Start Generating Report 'First CI050 compared to last Day CC050'.")
    try:
        previous_report_date = report_date - timedelta(days=1)
        ci050_first_day_report = (
            db.query(
                CI050.date,
                CI050.clearing_member,
                CI050.account,
                CI050.margin_type,
                CI050.margin
            )
            .filter(CI050.date == report_date)
            .group_by(CI050.clearing_member, CI050.account, CI050.margin_type)
            .having(CI050.time == func.min(CI050.time))
        )

        cc050_last_day_report = (
            db.query(
                CC050.date,
                CC050.clearing_member,
                CC050.account,
                CC050.margin_type,
                CC050.margin
            )
            .filter(CC050.date == previous_report_date)
        )
        subject = f"Earliest CI050 report compared to previous day CC050 report for {report_date}"
        mismatch_rows = merge_reports_and_compare(db, report_date, subject, ci050_first_day_report, cc050_last_day_report)
        send_email(subject, mismatch_rows)
    except Exception as e:
        logger.error(f"Error occurred: {e}")


def last_ci050_with_today_cc050(db: Session, report_date: date):
    logger.info("Start Generating Report 'Last CI050 compared to today CC050 values'.")
    try:
        ci050_end_day_report = (
            db.query(
                CI050.date,
                CI050.clearing_member,
                CI050.account,
                CI050.margin_type,
                CI050.margin
            )
            .filter(CI050.date == report_date)
            .group_by(CI050.clearing_member, CI050.account, CI050.margin_type)
            .having(CI050.time == func.max(CI050.time))
        )

        cc050_today_report = (
            db.query(
                CC050.date,
                CC050.clearing_member,
                CC050.account,
                CC050.margin_type,
                CC050.margin
            )
            .filter(CC050.date == report_date)
        )

        subject = f"Latest CI050 report compared to today CC050 report for {report_date}"
        mismatch_rows = merge_reports_and_compare(db, report_date, subject, ci050_end_day_report, cc050_today_report)
        send_email(subject, mismatch_rows)
    except Exception as e:
        logger.error(f"Error occurred: {e}")


def main():
    print("Reports:")
    print("1- First CI050 with last day CC050")
    print("2- Last CI050 with today's CC050")
    while True:
        report_number = input("Enter report number (1 or 2): ")
        if report_number in ['1', '2']:
            break
        else:
            print("Invalid report number. Please enter either 1 or 2.")

    while True:
        date_input = input("Enter the date in yyyy-mm-dd format: ")
        try:
            entered_date = datetime.strptime(date_input, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date format. Please enter the date in yyyy-mm-dd format.")

    db: Session = SessionLocal()
    report_date = entered_date.date()

    if report_number == '1':
        first_ci050_with_last_day_cc050(db, report_date)
    elif report_number == '2':
        last_ci050_with_today_cc050(db, report_date)
    main()


if __name__ == '__main__':
    main()


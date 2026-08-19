import logging

audit_logger = logging.getLogger("scamshield.audit")
audit_logger.setLevel(logging.INFO)

handler = logging.FileHandler("audit.log")
formatter = logging.Formatter("%(asctime)s | %(message)s")
handler.setFormatter(formatter)
audit_logger.addHandler(handler)


def log_report_submission(user_id: str, target_value: str, category: str):
    audit_logger.info(f"REPORT_SUBMITTED | user={user_id} | target={target_value} | category={category}")


def log_verification_check(check_type: str, target: str):
    audit_logger.info(f"VERIFICATION_CHECK | type={check_type} | target={target}")
from test.unit_test.db_manager_test import DBManagerTester
from test.unit_test.session_manager_test import SessionManagerTester


def testall():
    SessionManagerTester().all()
    DBManagerTester().all()

if __name__ == "__main__":
    testall()


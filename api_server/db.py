import mysql.connector
from colored import fg, bg, attr
from datetime import datetime
from jsondatetime import *

class DBManager:
    def __init__(self):
        self.cnx = mysql.connector.connect(user='root', password='1234',
                                           host='localhost',
                                           database='userdata')
        self.cursor = self.cnx.cursor()
        self._query_insert_userinfo = ("INSERT INTO userinfo "
                                      "(uid, name, given_name, email, signup_datetime) "
                                      "VALUES (%s, %s, %s, %s, %s)")
        self._query_select_userinfo_by_uid = ("SELECT * FROM userinfo "  # 마지막에 띄어쓰기 안해서 디버깅 40분동안 함
                                             "WHERE uid = %s")
        self._query_delete_userinfo_by_uid = ("DELETE FROM userinfo "
                                              "WHERE uid = %s")
        self._query_insert_todoitem = ("")
        self._query_select_todoitems_by_uid = ("")

    def _insert_userinfo(self, userinfo_dict: dict) -> bool: # use only when
        ud = userinfo_dict
        userinfo_values = (ud['uid'], ud['name'], ud['given_name'], ud['email'], JSONdate2datetime(ud['signup_datetime']))
        try:
            self.cursor.execute(self._query_insert_userinfo, userinfo_values)
            self.cnx.commit()
            print(f'{fg("white")}[DB] insert_userinfo {fg("white")}')
            return True
        except Exception as e:
            print(f'{fg("red")}[DB] failed: insert_userinfo{e} {fg("white")}')
            return False

    def _select_userinfo_by_uid(self, uid: str) -> dict or None:
        try:
            self.cursor.execute(self._query_select_userinfo_by_uid, (uid,))
            print(f'{fg("white")}[DB] select_userinfo_by_uid {fg("white")}')
            for tup in self.cursor: # uid is unique, so there is only one row or no rows.
                print(tup[4])
                return {'sub':tup[0], 'uid':tup[0], 'name':tup[1], 'given_name':tup[2], 'email':tup[3], 'signup_datetime':datetime2JSON(tup[4])}
            return None
        except Exception as e:
            print(f'{fg("red")}[DB] failed: select_userinfo_by_uid{e}{fg("white")}')
            return None

    def _delete_userinfo_by_uid(self, uid: str) -> bool:
        try:
            self.cursor.execute(self._query_delete_userinfo_by_uid, (uid,))
            self.cnx.commit()
            print(f'{fg("white")}[DB] delete_userinfo_by_uid {fg("white")}')
            return True
        except Exception as e:
            print(f'{fg("red")}[DB] failed: delete_userinfo_by_uid{e} {fg("white")}')
            return False

    def is_member(self, uid: str) -> bool:
        return self._select_userinfo_by_uid(uid) is not None

    def sign_up(self, userinfo_dict: dict) -> bool:
        if not self.is_member(userinfo_dict['uid']):
            userinfo_dict['signup_datetime'] = datetime2JSON(datetime.utcnow())
            if self._insert_userinfo(userinfo_dict):
                print(f'{fg("green")}[DB] sign_up: {userinfo_dict} {fg("white")}')
                return True
            else:
                print(f'{fg("red")}[DB] failed: sign_up: db error {fg("white")}')
                return False
        else:
            print(f'{fg("red")}[DB] failed: sign_up: already a member {userinfo_dict} {fg("white")}')
            return False

    def delete_account(self, uid: str) -> bool:
        if self.is_member(uid):
            if self._delete_userinfo_by_uid(uid):  # all todoitems are automatically deleted due to CASCADE
                print(f'{fg("green")}[DB] delete_account: {uid} {fg("white")}')
                return True
            else:
                print(f'{fg("red")}[DB] failed: delete_account: db error {fg("white")}')
                return False
        else:
            print(f'{fg("red")}[DB] failed: delete_account: not a member {uid} {fg("white")}')
            return False

    def get_userinfo(self, uid: str) -> dict or None:
        userinfo_dict = self._select_userinfo_by_uid(uid)
        if userinfo_dict is not None:
            print(f'{fg("green")}[DB] get_userinfo: {userinfo_dict} {fg("white")}')
            return userinfo_dict
        else:
            print(f'{fg("red")}[DB] failed: get_userinfo: not a member {uid} unless select failed {fg("white")}')
            return None

    def close(self):
        self.cnx.close()

def test():
    sampleuserinfo = {'uid': '13124', 'name': 'Sungwon', 'given_name': 'Yang', 'email': 'yyang3314@kaist.ac.kr'}
    uid = sampleuserinfo['uid']
    db = DBManager()
    db.sign_up(sampleuserinfo)
    db.get_userinfo(uid)
    db.delete_account(uid)
    db.get_userinfo(uid)
    db.close()

if __name__ == '__main__':
    test()
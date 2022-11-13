import mysql.connector
from colored import fg, bg, attr
from datetime import datetime
from jsondatetime import *

VERBOSE_DB = False

class DBManager:
    def __init__(self):
        self._query_insert_userinfo = ("INSERT INTO userinfo "
                                      "(uid, name, given_name, email, signup_datetime) "
                                      "VALUES (%s, %s, %s, %s, %s)")
        self._query_select_userinfo_by_uid = ("SELECT * FROM userinfo "  # 마지막에 띄어쓰기 안해서 디버깅 40분동안 함
                                             "WHERE uid = %s")
        self._query_delete_userinfo_by_uid = ("DELETE FROM userinfo "
                                              "WHERE uid = %s")
        self._query_insert_todoitem = ("INSERT INTO todoitem"
                                       "(uid, title, tags, deadline, is_repeated, repetition_id, memo, status)"
                                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        self._query_select_todoitem_by_uid = ("SELECT * FROM todoitem "
                                               "WHERE uid = %s")

    def _connect(self):
        try:
            self.cnx = mysql.connector.connect(user='root', password='1234',
                                               host='localhost',
                                               database='userdata')
            self.cursor = self.cnx.cursor()
        except Exception as e:
            print(f'{fg("red")}[DB] failed: _connect {e} {fg("white")}')

    def _close(self):
        try:
            self.cnx.close()
        except Exception as e:
            print(f'{fg("red")}[DB] failed: _close {e} {fg("white")}')

    def _insert_userinfo(self, userinfo_dict: dict) -> bool:
        res = False
        ud = userinfo_dict
        userinfo_values = (ud['uid'], ud['name'], ud['given_name'], ud['email'], JSONdate2datetime(ud['signup_datetime']))
        try:
            self._connect()
            self.cursor.execute(self._query_insert_userinfo, userinfo_values)
            self.cnx.commit()
            self._close()
            if VERBOSE_DB: print(f'{fg("white")}[DB] insert_userinfo {fg("white")}')
            res = True
        except Exception as e:
            print(f'{fg("red")}[DB] failed: insert_userinfo{e} {fg("white")}')

        return res

    def _select_userinfo_by_uid(self, uid: str) -> dict or None:
        res = None
        try:
            self._connect()
            self.cursor.execute(self._query_select_userinfo_by_uid, (uid,))
            if VERBOSE_DB: print(f'{fg("white")}[DB] select_userinfo_by_uid {fg("white")}')
            for tup in self.cursor: # uid is unique, so there is only one row or no rows.
                res = {'sub':tup[0], 'uid':tup[0], 'name':tup[1], 'given_name':tup[2], 'email':tup[3], 'signup_datetime':datetime2JSON(tup[4])}
                break
        except Exception as e:
            print(f'{fg("red")}[DB] failed: select_userinfo_by_uid{e}{fg("white")}')
        self._close()

        return res

    def _delete_userinfo_by_uid(self, uid: str) -> bool:
        res = False
        try:
            self._connect()
            self.cursor.execute(self._query_delete_userinfo_by_uid, (uid,))
            self.cnx.commit()
            self._close()
            if VERBOSE_DB: print(f'{fg("white")}[DB] delete_userinfo_by_uid {fg("white")}')
            res = True
        except Exception as e:
            print(f'{fg("red")}[DB] failed: delete_userinfo_by_uid{e} {fg("white")}')

        return res

    def _insert_todoitem(self, todoitem: dict) -> bool:
        def safe_get(dict: dict, key: str):
            if key in dict:
                res = dict[key]
                if type(res) is not str:
                    return int(res)
                else:
                    return res
            else:
                return None

        res = False
        try:
            self._connect()
            self.cursor.execute(self._query_insert_todoitem, (
                safe_get(todoitem, 'uid'), safe_get(todoitem, 'title'), safe_get(todoitem, 'tags'),
                safe_get(todoitem, 'deadline'), safe_get(todoitem, 'is_repeated'), safe_get(todoitem, 'repetition_id'),
                safe_get(todoitem, 'memo'), safe_get(todoitem, 'status')
                ))
            self.cnx.commit()
            self._close()
            if VERBOSE_DB: print(f'{fg("white")}[DB] insert_todoitem {fg("white")}')
            res = True
        except Exception as e:
            print(f'{fg("red")}[DB] failed: insert_todoitem{e} {fg("white")}')

        return res

    def _select_todoitem_by_uid(self, uid: str) -> list or None:
        res = None
        try:
            self._connect()
            self.cursor.execute(self._query_select_todoitem_by_uid, (uid,))
            if VERBOSE_DB: print(f'{fg("white")}[DB] select_todoitem_by_uid {fg("white")}')
            res = []
            for tup in self.cursor: # uid is unique, so there is only one row or no rows.
                res.append({'id':tup[0], 'title':tup[2], 'tags':tup[3], 'deadline':tup[4],
                            'is_repeated':bool(tup[5]), 'repetition_id':tup[6], 'memo':tup[7], 'status':tup[8]})
        except Exception as e:
            print(f'{fg("red")}[DB] failed: select_userinfo_by_uid{e}{fg("white")}')
        self._close()

        return res

    def is_member(self, uid: str) -> bool:
        return self._select_userinfo_by_uid(uid) is not None

    def sign_up(self, userinfo_dict: dict) -> bool:
        res = False
        if not self.is_member(userinfo_dict['uid']):
            userinfo_dict['signup_datetime'] = datetime2JSON(datetimenow())
            if self._insert_userinfo(userinfo_dict):
                print(f'{fg("green")}[DB] sign_up: {userinfo_dict} {fg("white")}')
                res = True
            else:
                print(f'{fg("red")}[DB] failed: sign_up: db error {fg("white")}')
        else:
            print(f'{fg("red")}[DB] failed: sign_up: already a member {userinfo_dict} {fg("white")}')

        return res

    def delete_account(self, uid: str) -> bool:
        res = False
        if self.is_member(uid):
            if self._delete_userinfo_by_uid(uid):  # all todoitems are automatically deleted due to CASCADE
                print(f'{fg("green")}[DB] delete_account: {uid} {fg("white")}')
                res = True
            else:
                print(f'{fg("red")}[DB] failed: delete_account: db error {fg("white")}')
        else:
            print(f'{fg("red")}[DB] failed: delete_account: not a member {uid} {fg("white")}')

        return res

    def get_userinfo(self, uid: str) -> dict or None:
        res = None
        userinfo_dict = self._select_userinfo_by_uid(uid)
        if userinfo_dict is not None:
            print(f'{fg("green")}[DB] get_userinfo: {userinfo_dict} {fg("white")}')
            res = userinfo_dict
        else:
            print(f'{fg("red")}[DB] failed: get_userinfo: not a member {uid} unless select failed {fg("white")}')

        return res

    def insert_one_todoitem(self, uid: str, todoitem: dict) -> bool:
        todoitem['uid'] = uid
        return self._insert_todoitem(todoitem)

    def insert_listof_todoitems(self, uid: str, todoitems: list) -> bool:
        for todoitem in todoitems:
            todoitem['uid'] = uid
            if self._insert_todoitem(todoitem) is False:
                return False
        return True

    def get_todoitems(self, uid: str) -> list:
        res = self._select_todoitem_by_uid(uid)
        if res is not None:
            return res
        else:
            return []

def test():
    global VERBOSE_DB
    VERBOSE_DB = True
    sampleuserinfo = {'uid': '13124', 'name': 'Sungwon', 'given_name': 'Yang', 'email': 'yyang3314@kaist.ac.kr'}
    uid = sampleuserinfo['uid']
    db = DBManager()
    db.sign_up(sampleuserinfo)
    db.get_userinfo(uid)
    db.delete_account(uid)
    db.get_userinfo(uid)

def test_todoitem_insert():
    global VERBOSE_DB
    VERBOSE_DB = True
    sampleuserinfo = {'uid': '777', 'name': 'Sungwon', 'given_name': 'Yang', 'email': 'yyang3314@kaist.ac.kr'}
    sampletododata = {'uid': '777', 'title': 'testitem!!', 'memo': 'this is insert todoitem test on python'}
    db = DBManager()
    db.sign_up(sampleuserinfo)
    db._insert_todoitem(sampletododata)
    res = db._select_todoitem_by_uid('777')
    print(res)

if __name__ == '__main__':
    test_todoitem_insert()
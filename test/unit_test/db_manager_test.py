from api_server.db_manager import DBManager

uid = "testuid123"
uinfo = {"uid": uid,
         "name": "testname",
         "given_name": "testgiven_name",
         "email": "testmail@easytodo.p-e.kr"}

non_existent_uid = "no_such_uid"

item1 = {"title": "testitem1"}
item2 = {"title": "testitem2"}
itemlist = [item1, item2]


class DBManagerTester:
    def sign_up_test(self):
        dbm = DBManager()
        dbm.delete_account(uid)
        assert dbm.sign_up(uinfo)
        assert dbm.sign_up(uinfo) == False

    def get_userinfo_test(self):
        dbm = DBManager()
        dbm.sign_up(uinfo)
        uinfodict = dbm.get_userinfo(uid)
        assert uinfodict["uid"] == uid
        assert uinfodict["name"] == "testname"
        assert dbm.get_userinfo(non_existent_uid) is None

    def delete_account_test(self):
        dbm = DBManager()
        dbm.sign_up(uinfo)
        dbm.get_userinfo(uid)
        assert dbm.delete_account(uid)
        assert dbm.get_userinfo(uid) is None

    def todoitem_test(self):
        dbm = DBManager()
        dbm.sign_up(uinfo)
        # insert test
        assert dbm.insert_one_todoitem(uid, item1)
        assert dbm.insert_listof_todoitems(uid, itemlist)
        # select test
        items = dbm.get_todoitems(uid)
        assert items is not None
        # delete test
        for it in items:
            assert dbm.delete_one_todoitem(uid, it["id"])
        assert dbm.get_todoitems(uid) == []
        # update test
        dbm.insert_one_todoitem(uid, item1)
        item = dbm.get_todoitems(uid)[0]
        item["title"] = "update test"
        assert dbm.update_one_todoitem(uid, item)
        assert dbm.get_todoitems(uid)[0]["title"] == "update test"

    def all(self):
        test_list = [['TC1.1. signup', self.sign_up_test],
                     ['TC1.2. get_userinfo', self.get_userinfo_test],
                     ['TC1.3. delete_account', self.delete_account_test],
                     ['TC1.4. todoitem', self.get_userinfo_test]]
        score = 0
        print('[DB_manager unit testing]')
        for i,t in enumerate(test_list):
            print(f'  ({t[0]}) ', end='')
            try:
                t[1]()
                print('success')
                score+=1
            except Exception as e:
                print(f'fail {e}')
        print(f'{score}/{len(test_list)} test cases passed\n')

if __name__ == "__main__":
    test = DBManagerTester()
    test.all()
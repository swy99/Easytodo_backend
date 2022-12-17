from api_server.session_manager import SessionManager


class SessionManagerTester:
    def login_test(self):
        sm = SessionManager(load=False,save=False)
        assert len(sm.login("uid").sid) == 40
        assert sm.login("uid") == sm.login("uid")

    def sid_to_uid_test(self):
        sm = SessionManager(load=False,save=False)
        uid = "randomuid"
        sid = sm.login(uid).sid
        assert sm.sid_to_uid(sid) == uid

    def logout_test(self):
        sm = SessionManager(load=False,save=False)
        uid = "randomuid"
        sid = sm.login(uid).sid
        assert sm.logout(sid)
        assert sm.sid_to_uid(sid) is None

    def all(self):
        test_list = [['TC2.1. login', self.login_test],
                     ['TC2.2. sid_to_uid', self.sid_to_uid_test],
                     ['TC2.3. logout', self.logout_test]]
        score = 0
        print('[session_manager unit testing]')
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
    test = SessionManagerTester()
    test.all()
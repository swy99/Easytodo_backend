from api_server.session_manager import SessionManager


class SessionManagerTest:
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
        self.login_test()
        self.sid_to_uid_test()
        self.logout_test()

if __name__ == "__main__":
    test = SessionManagerTest()
    test.all()
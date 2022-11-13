import random
import string
from datetime import datetime, timezone, timedelta
from jsondatetime import *

VERBOSE_SESSION = False

def randstr(length):
    letters_set = string.ascii_letters
    random_list = random.sample(letters_set, length)
    return ''.join(random_list)

class Session:
    def __init__(self, sid: str, uid: str, lifetime: timedelta):
        self.sid = sid
        self.uid = uid
        self.lifetime = lifetime
        self.timeout = datetimenow() + self.lifetime

    def __repr__(self):
        return f'Session(uid:{self.uid})'

    def __lt__(self, other):
        return self.timeout < other.timeout

    def __eq__(self, other):
        return self.timeout == other.timeout

    def resetTimeout(self) -> None:
        self.timeout = datetimenow() + self.lifetime

    def isTimeout(self) -> bool:
        return datetimenow() > self.timeout



class SessionManager:
    def __init__(self, lifetime: timedelta = timedelta(hours=1), sid_length: int = 40):
        self.sessions = []
        self.lifetime = lifetime
        self.sid_length = sid_length

    def _clearExpiredSessions(self) -> None:
        deleted_sessions = []
        for (i, session) in enumerate(self.sessions):
            if session.isTimeout():
                del self.sessions[i]
                deleted_sessions.append(session)
        if len(deleted_sessions) > 0:
            if VERBOSE_SESSION: print('[Timeout] ',end='')
            for session in deleted_sessions:
                print(session, end=', ')
            print('')

    def _search_session_by_uid(self, uid: str) -> Session:
        for session in self.sessions:
            if session.uid == uid:
                return session
        return None

    def _search_session_by_sid(self, sid: str) -> Session:
        for session in self.sessions:
            if session.sid == sid:
                return session
        return None

    def remove_session_by_sid(self, sid: str) -> bool:
        for session in self.sessions:
            if session.sid == sid:
                if VERBOSE_SESSION: print(f'[LOGOUT] {session}')
                self.sessions.remove(session)
                return True
        return False

    def remove_session_by_uid(self, uid: str) -> bool:
        for session in self.sessions:
            if session.uid == uid:
                if VERBOSE_SESSION: print(f'[LOGOUT] {session}')
                self.sessions.remove(session)
                return True
        return False

    def _createSession(self, uid: str) -> Session:
        newsid = randstr(self.sid_length)
        while self._search_session_by_sid(newsid) is not None:
            newsid = randstr(self.sid_length)
        new_session = Session(newsid, uid, self.lifetime)
        self.sessions.append(new_session)
        if VERBOSE_SESSION: print(f'[NEWSESSION] {new_session}')
        return new_session

    def verify_sid(self, sid: str) -> bool:
        self._clearExpiredSessions()
        for session in self.sessions:
            if session.sid == sid:
                return True
        return False

    def sid_to_uid(self, sid: str) -> str or None:
        self._clearExpiredSessions()
        for session in self.sessions:
            if session.sid == sid:
                return session.uid
        return None

    def login(self, uid: str) -> Session:
        self._clearExpiredSessions()
        session = self._search_session_by_uid(uid)
        if session is not None:
            session.resetTimeout()
        else:
            session = self._createSession(uid)
        # check the db if a new user
        return session

    def logout(self, sid: str) -> bool:
        self._clearExpiredSessions()
        return self.remove_session_by_sid(sid)


def test():
    global VERBOSE_SESSION
    VERBOSE_SESSION = True
    m = SessionManager()
    m.login('2222')
    import time
    time.sleep(1)
    print(m.sessions[0].sid)
    m.login('6665')
    print(m.sessions)
    time.sleep(3)
    m.login('11111')
    print(m.sessions)

if __name__ == '__main__':
    test()

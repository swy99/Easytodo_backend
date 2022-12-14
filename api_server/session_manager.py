import random
import string
from datetime import datetime, timezone, timedelta
from api_server.jsondatetime import *
import pickle
import os

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
    def __init__(self, lifetime:timedelta=timedelta(hours=1), sid_length:int=40, load:bool=True, save:bool=True):
        self.sessions = []
        self.lifetime = lifetime
        self.sid_length = sid_length
        self.load_enabled = load
        self.save_enabled = save
        self._load()

    def _load(self):
        if self.load_enabled:
            try:
                if os.path.isfile("session_manager.backup"):
                    with open('session_manager.backup', 'rb') as file:
                        session_manager = pickle.load(file)
                    self = session_manager
            except:
                pass
        self._clearExpiredSessions()

    def _save(self):
        if self.save_enabled:
            with open('session_manager.backup', 'wb') as file:
                pickle.dump(self, file)

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
        self._save()

    def _search_session_by_uid(self, uid: str) -> Session:
        res = None
        for session in self.sessions:
            if session.uid == uid:
                res = session
                break
        self._save()

        return res

    def _search_session_by_sid(self, sid: str) -> Session:
        res = None
        for session in self.sessions:
            if session.sid == sid:
                res = session
                break
        self._save()

        return res

    def remove_session_by_sid(self, sid: str) -> bool:
        res = False
        for session in self.sessions:
            if session.sid == sid:
                if VERBOSE_SESSION: print(f'[LOGOUT] {session}')
                self.sessions.remove(session)
                res = True
                break
        self._save()

        return res

    def remove_session_by_uid(self, uid: str) -> bool:
        res = False
        for session in self.sessions:
            if session.uid == uid:
                if VERBOSE_SESSION: print(f'[LOGOUT] {session}')
                self.sessions.remove(session)
                res = True
                break
        self._save()

        return res

    def _createSession(self, uid: str) -> Session:
        newsid = randstr(self.sid_length)
        while self._search_session_by_sid(newsid) is not None:
            newsid = randstr(self.sid_length)

        new_session = Session(newsid, uid, self.lifetime)
        self.sessions.append(new_session)

        if VERBOSE_SESSION:
            print(f'[NEWSESSION] {new_session}')
        self._save()

        return new_session

    def verify_sid(self, sid: str) -> bool:
        res = False
        self._clearExpiredSessions()
        for session in self.sessions:
            if session.sid == sid:
                res = True
                break
        self._save()

        return res

    def sid_to_uid(self, sid: str) -> str or None:
        res = None
        self._clearExpiredSessions()
        for session in self.sessions:
            if session.sid == sid:
                res = session.uid
                break
        self._save()

        return res

    def login(self, uid: str) -> Session:
        self._clearExpiredSessions()
        session = self._search_session_by_uid(uid)
        if session is not None:
            session.resetTimeout()
        else:
            session = self._createSession(uid)
        self._save()

        return session

    def logout(self, sid: str) -> bool:
        self._clearExpiredSessions()
        res = self.remove_session_by_sid(sid)
        self._save()

        return res


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

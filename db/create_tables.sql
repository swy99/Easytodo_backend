USE userdata;

DROP TABLE IF EXISTS todoitem;
DROP TABLE IF EXISTS userinfo;
DROP TABLE IF EXISTS session;

CREATE TABLE userinfo (
	uid VARCHAR(25) PRIMARY KEY,
    name VARCHAR(64),
    given_name VARCHAR(64),
    email VARCHAR(64),
    signup_datetime DATETIME
);

/*CREATE TABLE session (
	sid CHAR(40) PRIMARY KEY,
    uid VARCHAR(25) UNIQUE NOT NULL,
    timeout DATETIME NOT NULL,
    
    FOREIGN KEY (uid)
    REFERENCES userinfo(uid) ON UPDATE CASCADE ON DELETE CASCADE
);*/
    
CREATE TABLE todoitem (
	id INT PRIMARY KEY AUTO_INCREMENT,
	uid VARCHAR(25),
    title VARCHAR(128) NOT NULL,
    tags VARCHAR(128),
    deadline VARCHAR(32),
    is_repeated BOOLEAN,
    repetition_id INT,
    memo VARCHAR(1024),
    status VARCHAR(32),
    
    FOREIGN KEY (uid)
    REFERENCES userinfo(uid) ON UPDATE CASCADE ON DELETE CASCADE
);
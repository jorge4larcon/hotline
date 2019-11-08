BEGIN TRANSACTION;
DROP TABLE IF EXISTS "Configuration";
CREATE TABLE IF NOT EXISTS "Configuration" (
	"mac_address"	TEXT,
	"username"	TEXT,
	"ipv4_address"	TEXT,
	"ipv6_address"	TEXT,
	"inbox_port"	INTEGER,
	"ftp_port"	INTEGER,
	"ftp_banner"	TEXT,
	"ftp_max_connections"	INTEGER,
	"ftp_max_connections_per_ip"	INTEGER,
	"ftp_folder"	TEXT,
	"interlocutor_address"	INTEGER,
	"interlocutor_port"	INTEGER,
	"interlocutor_password"	INTEGER,
	"get_only_by_mac"	BOOLEAN
);
DROP TABLE IF EXISTS "SentMessage";
CREATE TABLE IF NOT EXISTS "SentMessage" (
	"receiver_contact"	TEXT NOT NULL,
	"content"	TEXT,
	"sent_timestamp"	DATETIME NOT NULL UNIQUE,
	"received_timestamp"	DATETIME,
	FOREIGN KEY("receiver_contact") REFERENCES "Contact"("mac_address") ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY("sent_timestamp")
);
DROP TABLE IF EXISTS "ReceivedMessage";
CREATE TABLE IF NOT EXISTS "ReceivedMessage" (
	"sender_contact"	TEXT NOT NULL,
	"content"	TEXT,
	"received_timestamp"	DATETIME NOT NULL UNIQUE,
	"sent_timestamp"	DATETIME,
	FOREIGN KEY("sender_contact") REFERENCES "Contact"("mac_address") ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY("received_timestamp")
);
DROP TABLE IF EXISTS "Contact";
CREATE TABLE IF NOT EXISTS "Contact" (
	"mac_address"	TEXT NOT NULL UNIQUE,
	"name"	TEXT,
	"ipv4_address"	TEXT,
	"ipv6_address"	INTEGER,
	"inbox_port"	INTEGER,
	"ftp_port"	INTEGER,
	PRIMARY KEY("mac_address")
);
INSERT INTO "Configuration" VALUES ('70:1c:e7:73:7b:61','lucia_alarconcio','192.168.1.72','fe80::721c:e7ff:fe73:7b61%19',42000,21,'Welcome to my FTP server, please be kind.',10,1,NULL,NULL,42000,'secret',1);
INSERT INTO "Contact" VALUES ('cccc.bbbb.eeee','juan_valdez','192.168.1.71','fe80::721c:e7ff:fe73:7b61%19',42000,21);
INSERT INTO "Contact" VALUES ('aaaa.eeee.ffff','lucia_alarcon','192.168.1.79','2806:104e:19:2548:721c:e7ff:fe73:7b61',42000,21);
INSERT INTO "Contact" VALUES ('701c.e773.7b65','jorge_alarcon','172.16.128.243','fe80::721c:e7ff:fe73:7b61%19',42000,21);
COMMIT;

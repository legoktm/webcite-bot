CREATE TABLE new_links ( wikipage VARCHAR(255), url VARCHAR(255), author VARCHAR(255), timestamp TIMESTAMP, oldid INT);
CREATE TABLE archived_links ( wikipage VARCHAR(255), archive_url VARCHAR(255), url VARCHAR(255), author VARCHAR(255), timestamp TIMESTAMP, oldid INT);
CREATE TABLE removed_links (wikipage VARCHAR(255), url VARCHAR(255), author VARCHAR(255), timestamp TIMESTAMP, oldid INT);
CREATE TABLE processed_links (wikipage VARCHAR(255), archive_url VARCHAR(255), url VARCHAR(255), author VARCHAR(255), timestamp TIMESTAMP, oldid INT, added_oldid INT);
ALTER TABLE `new_links` ADD id MEDIUMINT PRIMARY KEY NOT NULL AUTO_INCREMENT FIRST;
ALTER TABLE `archived_links` ADD id MEDIUMINT PRIMARY KEY NOT NULL AUTO_INCREMENT FIRST;
ALTER TABLE `processed_links` ADD id MEDIUMINT PRIMARY KEY NOT NULL AUTO_INCREMENT FIRST;
ALTER TABLE `removed_links` ADD id MEDIUMINT PRIMARY KEY NOT NULL AUTO_INCREMENT FIRST;

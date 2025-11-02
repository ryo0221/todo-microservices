-- auth 用
CREATE USER auth_user WITH ENCRYPTED PASSWORD 'auth_pass';
CREATE DATABASE auth_db OWNER auth_user;
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;

-- todo 用
CREATE USER todo_user WITH ENCRYPTED PASSWORD 'todo_pass';
CREATE DATABASE todo_db OWNER todo_user;
GRANT ALL PRIVILEGES ON DATABASE todo_db TO todo_user;

# Overview #

This is a web interface to the privilege system.

We are using django.

The model will be generated using the django ORM. The CLI will
eventually also interact with the same model.

# Initial Framework setup #

``` shell
#
# create project 'privweb'
$ django-admin startproject privweb

# create app 'priv'
$ django-admin startapp priv

# create admin data models
$ python manage.py migrate

# after changes in priv data model
$ python manage.py makemigrations priv
$ python manage.py migrate

# run server
$ python manage.py runserver
```

# Generated table schema (sqlite3) #

``` sql
CREATE TABLE IF NOT EXISTS "priv_user" (
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "acctname" varchar(24) NOT NULL,
  "first_name" varchar(24) NOT NULL,
  "last_name" varchar(24) NOT NULL);
  
CREATE TABLE IF NOT EXISTS "priv_role" (
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "role_name" varchar(80) NOT NULL);

CREATE TABLE IF NOT EXISTS "priv_permission" (
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "permission_name" varchar(80) NOT NULL);

CREATE TABLE IF NOT EXISTS "priv_role_users" (
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "role_id" integer NOT NULL REFERENCES "priv_role" ("id"),
  "user_id" integer NOT NULL REFERENCES "priv_user" ("id"));
CREATE UNIQUE INDEX "priv_role_users_role_id_user_id_70dac234_uniq"
  ON "priv_role_users" ("role_id", "user_id");
CREATE INDEX "priv_role_users_role_id_2ca99ccc"
  ON "priv_role_users" ("role_id");
CREATE INDEX "priv_role_users_user_id_37824c99" 
  ON "priv_role_users" ("user_id");

CREATE TABLE IF NOT EXISTS "priv_role_permissions" (
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "role_id" integer NOT NULL REFERENCES "priv_role" ("id"),
  "permission_id" integer NOT NULL REFERENCES "priv_permission" ("id"));
CREATE UNIQUE INDEX "priv_role_permissions_role_id_permission_id_9312c80d_uniq"
  ON "priv_role_permissions" ("role_id", "permission_id");
CREATE INDEX "priv_role_permissions_role_id_67d9e6cc"
  ON "priv_role_permissions" ("role_id");
CREATE INDEX "priv_role_permissions_permission_id_3c01964f"
  ON "priv_role_permissions" ("permission_id");
```


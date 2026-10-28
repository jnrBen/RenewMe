# RenewMe

RenewMe is a Windows desktop app for NHIS offices and health facilities in Ghana. It finds members whose policies expire within a set number of days (30 by default) and sends them an SMS reminder.

It was built as a final-year Computer Science project
## 

## What it does

* Connects to a MySQL, PostgreSQL or SQL Server database and lists NHIS members whose policies expire soon.
* Sends reminders to everyone on the list, or to one member at a time.
* Works with mNotify, Hubtel, Africa's Talking, Twilio, or a custom SMS endpoint.
* Searches the whole member table by name, phone number, membership number, date of birth or email.
* Logs every SMS attempt with a timestamp, status and failure reason.
* Maps your own table and column names in the Customize tab, so you don't have to change your database.
* Has local user logins and a dark and light mode.


## Requirements

* Windows 10 or 11
* Python 3.10 or newer (developed on 3.13)
* A member database in MySQL, PostgreSQL or SQL Server. For SQL Server you also need ODBC Driver 17.
* An account with one of the supported SMS providers

## Install and run

```
git clone https://github.com/jnrBen/RenewMe.git
cd RenewMe
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

Run it from the project folder, because the app uses relative paths for its `data/` folder.

On first run the app creates a `data/` folder and a default account:

## Set it up

1. **Customize, Column Mapping.** Enter your table name and the column that holds each field. The defaults are:

|Field|Default column|
|-|-|
|Name|`name`, or `first\_name` and `last\_name` if your table splits them|
|Phone|`phone\_number`|
|Policy end date|`end\_date`|
|Membership number|`membership\_number`|
|Date of birth|`dob`|
|Email|`email`|
|Insurance type|`insurance\_type`|



1. Only rows where the insurance type is "National Health Insurance Scheme" are picked up. The expiry window is also set here.
2. **Customize, API Provider.** Pick your SMS provider and enter its credentials and sender ID.
3. **Connection tab.** Enter the database details and click Connect. Expiring members appear in the Connection and Users tabs.

4\. Phone numbers can be in the form `0XXXXXXXXX`, `XXXXXXXXX` or `+233XXXXXXXXX`. Anything else is skipped and logged as failed.

## Where data and secrets go

The database password and SMS keys are stored in Windows Credential Manager through the `keyring` library. They are never written to a file in this project.

Everything else is local to the `data/` folder: the user database, SMS log, and settings. These files are not encrypted.



## Project layout

```
main.py             entry point, navigation, scheduled sending, notifications
config.py           shared app state and config file helpers
constants.py        defaults, SMS template, provider and payment fields
auth.py             local login accounts (SQLite)
database.py         connection, expiry query, member search
sms.py              SMS routing across providers, bulk and single send
session.py          connect and disconnect handling
utils.py            phone formatting, logging, saved connection details
ui/                 one file per tab: connection, log, users, customize, login
```


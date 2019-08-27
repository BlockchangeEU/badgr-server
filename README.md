# Badgr Server
*Digital badge management for issuers, earners, and consumers*

Badgr-server is the Python/Django API backend for issuing [Open Badges](http://openbadges.org). In addition to a powerful Issuer API and browser-based user interface for issuing, Badgr offers integrated badge management and sharing for badge earners. Free accounts are hosted by Concentric Sky at [Badgr.io](http://info.badgr.io), but for complete control over your own issuing environment, Badgr Server is available open source as a Python/Django application.

See also [badgr-ui](https://github.com/concentricsky/badgr-ui), the Angular front end that serves as users' interface for this project.

### About the Badgr Project
Badgr was developed by [Concentric Sky](https://concentricsky.com), starting in 2015 to serve as an open source reference implementation of the Open Badges Specification. It provides functionality to issue portable, verifiable Open Badges as well as to allow users to manage badges they have been awarded by any issuer that uses this open data standard. Since 2015, Badgr has grown to be used by hundreds of educational institutions and other people and organizations worldwide. See [Project Homepage](https://badgr.org) for more details about contributing to and integrating with Badgr.

## How to get started on your local development environment (Linux)
Visit https://github.com/concentricsky/badgr-server for README.md

## How to get started on your local development environment (Windows)
Prerequisites:

* PyCharm IDE
* Git
* Python 2.7.x
* MySQL

#### Installation steps (for Windows 10, 64-bit)
* Clone badgr-server project -> https://github.com/Sphereon-Opensource/badgr-server
* Download and install PyCharm IDE -> https://www.jetbrains.com/pycharm/download/
* From https://www.lfd.uci.edu/~gohlke/pythonlibs, download the following binaries:
    * MySQL_python-1.2.5-cp27-none-win_amd64.whl
    * mysqlclient-1.4.2-cp27-cp27m-win_amd64.whl
    * Pillow-6.0.0-cp27-cp27m-win_amd64.whl
    * pycairo-1.18.1-cp27-cp27m-win_amd64.whl

#### In PyCharm Terminal
* `pip install wheel` 
* `pip install MySQL_python-1.2.5-cp27-none-win_amd64.whl`
* `pip install mysqlclient-1.4.2-cp27-cp27m-win_amd64.whl`
* `pip install Pillow-6.0.0-cp27-cp27m-win_amd64.whl'`
* `pip install pycairo-1.18.1-cp27-cp27m-win_amd64.whl`
* `pip install mysql-connector-python`
* `pip install mysql-connector-python-rf`

#### In PyCharm Editor
* Configure Python interpreter (add python.exe) and install all recommended packages
* In *apps/mainsite/* copy *settings_local.py.example* file and rename to *settings_local.py*
* In this file, add username and password for MySQL database and add *['localhost', '127.0.0.1']* to *ALLOWED_HOSTS*
* Check if *mysql.connector* is imported (e.g. by creating a new *.py* file and type *import msql.connector*)

#### In PyCharm Terminal (venv)
* `python manage.py migrate`
* `python manage.py dist`
* `python manage.py createsuperuser`
    * Enter username
    * Enter email
    * Enter password
* `python manage.py runserver`
* Go to http://localhost:8000/staff
* Sign in as the superuser you created above

### Configuring Factom Blockchain Connection

In order to submit evidences to the Factom Blockchain, you will need access to:
* running `factomd` and `factom-walletd` instances
* an entry credit address to fund Factom Entries
    * To create a new address using the `factom-cli` see https://docs.factom.com/cli#newecaddress
* a 32 byte private seed for producing digital signatures using the Ed25519 algorithm. 
    * For testing, an easy way to do this is by going to https://www.random.org/bytes/, and generating a hex encoded 32 random bytes.
* Factom Chain Id where entries can be committed

This information needs to be included in the following variables in `./apps/mainsite/settings_local.py`

```python
#location where factomd is running eg. 'http://localhost:8088'
FACTOMD_HOST = '<insert-factomd-endpoint>'

#location where factom-walletd is running eg. 'http://localhost:8089' 
FACTOM_WALLETD_HOST = '<insert-factom-walletd-endpoint>'

#funded entry credit address that can fund Factom entries
EC_ADDRESS = '<insert-entry-credit-address>'

#seed for secret key used to sign badge commitments (should be 32 bytes in hex) 
SECRET_SIGNING_SEED = '<insert-secret-seed>'

#chain id where badges should be commited. must be an existing chain
BADGE_COMMIT_CHAIN_ID = '<insert-chain-id>'
```

Using the `factom-cli` you can create a new chain as follows:
```bash
factom-cli addchain -n {chainName} {EC_Public_Key} < {filename}
```
where the data for the first entry is contained in the file `{filename}`.

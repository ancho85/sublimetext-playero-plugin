# pylint:disable=C6666,R0201

from OpenOrange import *

errQuery = Query()
errQuery.sql = "SELECT SerNr, FROM Alotment"
errQuery.open()

errQuery2 = Query()

errQuery2.sql = "SELECT SerNr FROM Alotment alias1 INNER JOIN Deposit alias1"
errQuery2.open()
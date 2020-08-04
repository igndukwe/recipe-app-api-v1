# Simulate the db being avaliable or not
from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):
    # what happens when db is already avaliable
    def test_wait_for_db_ready(self):
        """Test waithing for db when db is available
        """
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')  # core/management/wait_for_db.py
            # check that getitem was called once
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db
        """
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # the 1st 5 times will raise an operational error
            # and 6th will be a success
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')  # core/management/wait_for_db.py
            # ckeck that getitem is called five times and sixth is a success
            self.assertEqual(gi.call_count, 6)

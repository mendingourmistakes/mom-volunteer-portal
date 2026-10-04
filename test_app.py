import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sqlalchemy
import app

class TestAppDatabaseErrorHandling(unittest.TestCase):

    @patch("app.get_db_engine")
    @patch("streamlit.error")
    def test_run_query_operational_error(self, mock_st_error, mock_get_db_engine):
        mock_engine = MagicMock()
        mock_engine.connect.side_effect = sqlalchemy.exc.OperationalError("Connection failed", None, Exception())
        mock_get_db_engine.return_value = mock_engine

        result = app.run_query("SELECT * FROM users")

        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertTrue(result.empty)
        mock_st_error.assert_called_once()
        self.assertIn("Database connection error", mock_st_error.call_args[0][0])

    @patch("app.get_db_engine")
    @patch("streamlit.error")
    def test_execute_db_operational_error(self, mock_st_error, mock_get_db_engine):
        mock_engine = MagicMock()
        mock_engine.begin.side_effect = sqlalchemy.exc.OperationalError("Connection failed", None, Exception())
        mock_get_db_engine.return_value = mock_engine

        # Should not raise exception
        app.execute_db("UPDATE users SET tier = 2")

        mock_st_error.assert_called_once()
        self.assertIn("Database connection error", mock_st_error.call_args[0][0])

    @patch("app.get_db_engine")
    @patch("streamlit.error")
    def test_run_query_engine_none(self, mock_st_error, mock_get_db_engine):
        mock_get_db_engine.return_value = None

        result = app.run_query("SELECT * FROM users")

        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertTrue(result.empty)
        mock_st_error.assert_called_once_with("Database connection configuration is missing or invalid.")

    @patch("app.get_db_engine")
    @patch("streamlit.error")
    def test_execute_db_engine_none(self, mock_st_error, mock_get_db_engine):
        mock_get_db_engine.return_value = None

        app.execute_db("UPDATE users SET tier = 2")

        mock_st_error.assert_called_once_with("Database connection configuration is missing or invalid.")

    def test_get_db_engine_missing_secrets(self):
        with patch("streamlit.secrets", {}, create=True):
            engine = app.get_db_engine()
            self.assertIsNone(engine)

    def test_get_supabase_client_missing_secrets(self):
        with patch("streamlit.secrets", {}, create=True):
            client = app.get_supabase_client()
            self.assertIsNone(client)

if __name__ == "__main__":
    unittest.main()

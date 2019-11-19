import dbfunctions
import configuration
import logging
import sys
import PyQt5
import ui

if __name__ == '__main__':
    configuration.configure_logging(logging.INFO)
    logging.info('Logging has been configured!')
    app_icon = None
    try:
        if configuration.running_as_a_python_process():
            logging.info('Running as a Python process')
            dbfunctions.set_dbpath(configuration.debug_database_path())
        else:
            logging.info('Not running as a Python process')
            dbfunctions.set_dbpath(configuration.bundled_database_path(__file__))
            app_icon = configuration.bundled_icon_path(__file__)
    except FileNotFoundError as f:
        logging.critical(f)
        logging.info('Closing application...')
        sys.exit(f.errno)
    except Exception as e:
        logging.error(e)

    app = PyQt5.QtWidgets.QApplication(sys.argv)
    if app_icon:
        app_icon = PyQt5.QtGui.QIcon(configuration.bundled_icon_path(__file__))
        app.setWindowIcon(app_icon)
    try:
        configuration.setup_network_information()
    except Exception as e:
        from PyQt5 import QtWidgets
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle('Error')
        msg.setText("Could not configure your network information, some of the features won't be available.")
        msg.setInformativeText("Are you connected to a network?")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
        answer = msg.exec_()

    window = ui.HotlineMainWindow()
    window.show()
    exit_code = app.exec_()
    logging.info('Closing app, setting some values in the DB')
    sys.exit(exit_code)

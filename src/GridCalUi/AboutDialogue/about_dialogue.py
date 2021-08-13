import sys
import subprocess
from PySide2.QtWidgets import QDialog
from typing import List
from GridCalUi.AboutDialogue.gui import *
from GridCal.__version__ import __GridCal_VERSION__, contributors_msg, copyright_msg
from GridCal.update import check_version, get_upgrade_command


class AboutDialogueGuiGUI(QDialog):

    def __init__(self, parent=None):
        """

        :param parent:
        """
        QDialog.__init__(self, parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self.setWindowTitle('About GridCal')
        self.setAcceptDrops(True)

        # check the version in pypi
        version_code, latest_version = check_version()

        self.upgrade_cmd: List[str] = ['']

        if version_code == 1:
            addendum = '\nThere is a newer version: ' + latest_version

            self.upgrade_cmd = get_upgrade_command(latest_version)
            command = ' '.join(self.upgrade_cmd)
            self.ui.updateLabel.setText('\n\nTerminal command to update:\n\n' + command)
            self.ui.updateButton.setVisible(False)

        elif version_code == -1:
            addendum = '\nThis version is newer than the version available in the repositories (' + latest_version + ')'
            self.ui.updateLabel.setText(addendum)
            self.ui.updateButton.setVisible(False)

        elif version_code == 0:
            addendum = '\nGridCal is up to date.'
            self.ui.updateLabel.setText(addendum)
            self.ui.updateButton.setVisible(False)

        elif version_code == -2:
            addendum = '\nIt was impossible to check for a newer version'
            self.ui.updateLabel.setText(addendum)
            self.ui.updateButton.setVisible(False)

        else:
            addendum = ''
            self.ui.updateLabel.setText(addendum)
            self.ui.updateButton.setVisible(False)

        # self.ui.mainLabel.setText(about_msg)
        self.ui.versionLabel.setText('GridCal version: ' + __GridCal_VERSION__ + ', ' + addendum)
        self.ui.copyrightLabel.setText(copyright_msg)
        self.ui.contributorsLabel.setText(contributors_msg)

        # click
        self.ui.updateButton.clicked.connect(self.update)

    def msg(self, text, title="Warning"):
        """
        Message box
        :param text: Text to display
        :param title: Name of the window
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        # msg.setInformativeText("This is additional information")
        msg.setWindowTitle(title)
        # msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def update(self):
        """
        Upgrade GridCal
        :return:
        """
        list_files = subprocess.run(self.upgrade_cmd, stdout=subprocess.PIPE, text=True,
                                    input="Hello from the other side")  # upgrade_cmd is a list already
        if list_files.returncode != 0:
            self.msg("The exit code was: %d" % list_files.returncode)
        else:
            self.msg('GridCal updated successfully')


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = AboutDialogueGuiGUI()
    # window.resize(1.61 * 700.0, 600.0)  # golden ratio
    window.show()
    sys.exit(app.exec_())


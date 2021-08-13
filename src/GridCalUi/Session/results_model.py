# This file is part of GridCal.
#
# GridCal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GridCal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GridCal.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from PySide2.QtWidgets import *
from PySide2 import QtCore
from GridCal.Engine.Simulations.result_types import ResultTypes
from GridCal.Engine.Simulations.results_table import ResultsTable


def fast_data_to_text(data, columns, index):
    # header first
    txt = '\t' + '\t'.join(columns) + '\n'

    # data
    for t, index_value in enumerate(index):
        if data[t, :].sum() != 0.0:
            txt += str(index_value) + '\t' + '\t'.join([str(x) for x in data[t, :]]) + '\n'

    return txt


def fast_data_to_numpy_text(data):

    if len(data.shape) == 1:
        txt = '[' + ', '.join(['{0:.6f}'.format(x) for x in data]) + ']'

    elif len(data.shape) == 2:

        if data.shape[1] > 1:
            # header first
            txt = '['

            # data
            for t in range(data.shape[0]):
                txt += '[' + ', '.join(['{0:.6f}'.format(x) for x in data[t, :]]) + '],\n'

            txt += ']'
        else:
            txt = '[' + ', '.join(['{0:.6f}'.format(x) for x in data[:, 0]]) + ']'
    else:
        txt = '[]'

    return txt


class ResultsModel(QtCore.QAbstractTableModel):
    """
    Class to populate a Qt table view with data from the results
    """
    def __init__(self, table: ResultsTable, parent=None):
        """

        :param table:
        """
        QtCore.QAbstractTableModel.__init__(self, parent)

        self.table = table

        self.units = table.units

    def flags(self, index):
        if self.table.editable and index.column() > self.table.editable_min_idx:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def rowCount(self, parent=None):
        """

        :param parent:
        :return:
        """
        return self.table.r

    def columnCount(self, parent=None):
        """

        :param parent:
        :return:
        """
        return self.table.c

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """

        :param index:
        :param role:
        :return:
        """
        if index.isValid():

            val = self.table.data_c[index.row(), index.column()]

            if role == QtCore.Qt.DisplayRole:

                if isinstance(val, str):
                    return val
                elif isinstance(val, complex):
                    if val.real != 0 or val.imag != 0:
                        return val.__format__(self.table.format_string)
                    else:
                        return '0'
                else:
                    if val != 0:
                        return val.__format__(self.table.format_string)
                    else:
                        return '0'

            elif role == QtCore.Qt.BackgroundRole:

                return None  # QBrush(Qt.yellow)

        return None

    def headerData(self, section, orientation, role=None):
        """
        Get the header value
        :param section: header index
        :param orientation: Orientation {QtCore.Qt.Horizontal, QtCore.Qt.Vertical}
        :param role:
        :return:
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if len(self.table.cols_c) > section:
                    return self.table.cols_c[section]

            elif orientation == QtCore.Qt.Vertical:
                if self.table.index_c is None:
                    return section
                else:
                    if self.table.isDate:
                        return self.table.index_c[section].strftime('%Y/%m/%d  %H:%M.%S')
                    else:
                        return str(self.table.index_c[section])
        return None

    def slice_cols(self, col_idx) -> "ResultsModel":
        """
        Make column slicing
        :param col_idx: indices of the columns
        :return: Nothing
        """
        return ResultsModel(self.table.slice_cols(col_idx))

    def search_in_columns(self, txt):
        """
        Search stuff
        :param txt:
        :return:
        """
        print('Searching', txt)
        mdl = self.table.search_in_columns(txt)

        if mdl is not None:
            print('Found')
            return ResultsModel(mdl)
        else:
            return None

    def copy_to_column(self, row, col):
        """
        Copies one value to all the column
        @param row: Row of the value
        @param col: Column of the value
        @return: Nothing
        """
        self.table.copy_to_column(row, col)

    def is_complex(self):
        return self.table.is_complex()

    def get_data(self):
        """
        Returns: index, columns, data
        """
        return self.table.get_data()

    def convert_to_cdf(self):
        """
        Convert the data in-place to CDF based
        :return:
        """

        # calculate the proportional values of samples
        self.table.convert_to_cdf()

    def convert_to_abs(self):
        """
        Convert the data to abs
        :return:
        """
        self.table.convert_to_abs()

    def to_df(self):
        """
        get DataFrame
        """
        return self.table.to_df()

    def save_to_excel(self, file_name):
        """
        save data to excel
        :param file_name:
        """
        self.to_df().to_excel(file_name)

    def save_to_csv(self, file_name):
        """
        Save data to csv
        :param file_name:
        """
        self.to_df().to_csv(file_name)

    def get_data_frame(self):
        """
        Save data to csv
        """
        return self.table.get_data_frame()

    def copy_to_clipboard(self):
        """
        Copy profiles to clipboard
        """
        n = len(self.table.cols_c)

        if n > 0:

            index, columns, data = self.get_data()

            txt = fast_data_to_text(data, columns, index)

            # copy to clipboard
            cb = QApplication.clipboard()
            cb.clear(mode=cb.Clipboard)
            cb.setText(txt, mode=cb.Clipboard)

        else:
            # there are no elements
            pass

    def copy_numpy_to_clipboard(self):
        """
        Copy profiles to clipboard
        """
        n = len(self.table.cols_c)

        if n > 0:

            index, columns, data = self.get_data()

            txt = fast_data_to_numpy_text(data)

            # copy to clipboard
            cb = QApplication.clipboard()
            cb.clear(mode=cb.Clipboard)
            cb.setText(txt, mode=cb.Clipboard)

        else:
            # there are no elements
            pass

    def plot(self, ax=None, selected_col_idx=None, selected_rows=None):
        """
        Plot the data model
        :param ax: Matplotlib axis
        :param selected_col_idx: list of selected column indices
        :param selected_rows: list of rows to plot
        """

        self.table.plot(ax=ax, selected_col_idx=selected_col_idx, selected_rows=selected_rows)

import warnings

from logik.controls import type_check
from logik.data import Data, Const
from logik.unit import Unit
from logik.formula import Formula


class Table:

    def __init__(self, column_names=[], columns=2, signs=[]):
        """
        Initialize a Table.
        :param column_names: List[str] = names of the columns
        :param columns: int = number of columns
        :param signs: List[Union[Unit, str]] = sign or unit of each column
        """

        self.datas = []
        self.columns = columns
        self.column_names = []
        self.units = []

        # create units
        if not signs:
            self.units = [Unit("") for i in range(self.columns)]
        else:
            for sign in signs:
                if isinstance(sign, str):
                    sign = sign.split("/")
                    if len(sign) > 1:
                        sign = ["" if s == "1" else s for s in sign]
                        unit = Unit(sign[0], sign[1])
                    else:
                        unit = Unit(sign[0])
                else:
                    unit = sign
                self.units.append(unit)

        # create column names
        if not column_names:
            self.column_names = [f"Column {i}" for i in range(self.columns)]
        else:
            self.column_names = column_names

    def __str__(self):
        """
        Method to show a Table.
        :return: str = Table as string formatted
        """

        # + 3 for " [" and "]", +4 for additional space
        width = [len(self.column_names[i]) + len(str(self.units[i])) + 3 + 4 if len(str(self.units[i])) > 0 \
                     else len(self.column_names[i]) + 4 for i in range(self.columns)]

        # check if a bigger column is necessary
        for column in range(self.columns):
            col_data = [data[column - 1] for data in self.datas]
            for slot_data in col_data:
                width[column - 1] = max(len(str(slot_data)) + 4, width[column - 1])

        # create table header
        string = ""
        for index, column_name in enumerate(self.column_names):
            unit_str = str(self.units[index])
            if unit_str != "":
                # the minus 3 is for the ' [' and ']'
                string += f"{column_name} [{unit_str}]" + " " * (width[index] - len(column_name) - len(unit_str) - 3)
            else:
                string += f"{column_name}" + " " * (width[index] - len(column_name))
            string += "|"
        string += "\n"

        # create separator (header - body)
        string += "-" * (sum(width) + len(width)) + "\n"

        # fill data into table
        for data in self.datas:
            for index, element in enumerate(data):
                string += f"{element}" + " " * (width[index] - len(str(element))) + "|"
            if not (data is self.datas[-1]):
                string += "\n"

        return string

    def __repr__(self):
        return self.__str__()

    def calc(self, formula, para_dict, column_name="", sign=True):
        """
        Method for calculating new columns with dependencies to others given by a formula.
        The new column is added to the current data.
        :param formula: Formula-Object = Connection between parameters, and table columns
        :param para_dict: Dict[str, Optional[int, str, Any]] = dictionary specifying which objects to use in formula
            key (str): name of variable or parameter in formula-object
            value (int): index of column in table for the parameter at key
            value (str): fixed parameter for equation. Should be str(<float>) (equal for all columns)
        :param column_name: str = Name of the arising column
        :param sign: Optional[Unit, str] = sign/unit of the arising column
        :return: void
        """

        type_check((formula, Formula))

        if not self.datas:
            warnings.warn(f"No data found in table.")
            return

        # add new column name
        if column_name == "":
            column_name = f"Column {self.columns}"
        self.column_names.append(column_name)

        # update number of columns
        self.columns += 1

        # add unit to column
        if sign is True:
            value_dict = {}
            for key in para_dict:
                if isinstance(para_dict[key], int):
                    if self.units[para_dict[key]] != Unit():
                        value_dict[key] = Const(1, self.units[para_dict[key]])
                    else:
                        value_dict[key] = 1
                elif isinstance(para_dict[key], str):
                    value_dict[key] = float(para_dict[key])
                else:
                    value_dict[key] = para_dict[key]

            unit = formula.calc_unit(value_dict)
            self.units.append(unit)
        elif sign is False:
            self.units.append(Unit(""))
        else:
            self.units.append(sign)

        # calculate data and insert them into the column
        datas = []
        for row in self.datas:
            value_dict = {key: row[para_dict[key]] if isinstance(para_dict[key], int) else float(para_dict[key])
            if isinstance(para_dict[key], str) else para_dict[key] for key in para_dict}
            value = formula.calc(value_dict)
            if isinstance(value, (Data, Const)):
                value.unit = Unit()
            datas.append(list(row) + [value])
        self.datas = datas

    def add(self, data_tuple):
        """
        Adds a data-row to table
        :param data_tuple: Tuple[Optional[int, float, Const, Data]] = data for each column of table
        :return: void
        """

        type_tuple = type(data_tuple)

        if type_tuple == list:
            data_tuple = tuple(data_tuple)
        elif type_tuple != tuple:
            raise ValueError(f"Expected a tuple, get {type_tuple} instead")

        if len(data_tuple) == self.columns:
            for index, data in enumerate(data_tuple):
                if isinstance(data, (Data, Const)):
                    if data.unit != self.units[index] and data.unit != Unit(""):
                        raise Exception(f"Can´t fill column of {self.units[index]} with {data.unit}")
                    elif data.unit == Unit(""):
                        data_tuple[index].unit = self.units[index]
                    else:
                        data_tuple[index].unit = Unit()
            self.datas.append(data_tuple)
        else:
            raise ValueError(f"Expected an tuple of {self.columns}, get tuple of {len(data_tuple)} instead")

    def arithmetic_average(self):
        """
        calculates the arithmetic_average and their std_error for all columns.
        In case of Data column the average will be the weighted average
        average: 1/N * sum(data)
        std_error: sqrt( sum(data - average)^2 * 1/(n * (n - 1)) )
        weighted average: 1 / sum(1/(error^2)) * sum(data/(error^2))
        weighted error: sqrt( sum(1/(error^2)) )
        :return: List[Data] = List for each column of average and std_error
        """

        averages = []
        n = len(self.datas)
        for i in range(self.columns):

            # calculate mean and error
            if isinstance(self.datas[0][i], Data):
                w = sum([1 / data[i].error ** 2 for data in self.datas])
                wx = sum([data[i].value / data[i].error ** 2 for data in self.datas])
                average = wx / w
                error = 1 / w ** 0.5
            elif isinstance(self.datas[0][i], Const):
                average = sum(data[i].value for data in self.datas) / n
                error = (sum((data[i].value - average) ** 2 for data in self.datas) / (n * (n - 1))) ** 0.5
            else:
                average = sum(data[i] for data in self.datas) / n
                error = (sum((data[i] - average) ** 2 for data in self.datas) / (n * (n - 1))) ** 0.5

            if error != 0.0:
                data = Data(value=str(average), error=str(error), n=2, sign=self.units[i])
            elif self.units[i].denominator or self.units[i].numerator:
                data = Const(value=average, sign=self.units[i])
            else:
                data = average
            averages.append(data)

        return averages

    def geometric_average(self):
        """
        calculates the geometric_average for all columns.
        average: product( data )^(1/n)
        :return: List[Optional[float, Const]]
        """

        averages = []
        n = len(self.datas)
        for i in range(self.columns):
            prod = 1
            for data in self.datas:
                if isinstance(data[i], (Data, Const)):
                    prod *= data[i].value
                else:
                    prod *= data[i]

            if self.units[i].denominator or self.units[i].numerator:
                value = Const(value=prod ** (1.0 / n), sign=self.units[i])
            else:
                value = prod ** (1.0 / n)
            averages.append(value)
        return averages

    def harmonic_average(self):
        """
        calculates the harmonic_average for all columns.
        average: n / sum(1 / data)
        :return: List[Optional[float, Const]]
        """

        averages = []
        n = len(self.datas)
        for i in range(self.columns):
            column_data = [data[i].value if isinstance(data[i], (Data, Const)) else data[i] for data in self.datas]
            average = n / sum(1 / data for data in column_data)

            if self.units[i].denominator or self.units[i].numerator:
                average = Const(value=average, sign=self.units[i])

            averages.append(average)
        return averages

    def median(self):
        """
        returns median for all columns
        median: is the value at the half list length if sorted by value
        :return: List[Optional[float, Const]]
        """

        medians = []
        for i in range(self.columns):
            column_data = [data[i].value if isinstance(data[i], (Data, Const)) else data[i] for data in self.datas]
            column_data.sort()

            length = len(column_data)
            if length % 2 == 1:
                data = column_data[length // 2]
            else:
                data = 0.5 * (column_data[length // 2 - 1] + column_data[length // 2])

            if self.units[i].denominator or self.units[i].numerator:
                data = Const(value=data, sign=self.units[i])

            medians.append(data)
        return medians

    def modus(self):
        """
        calculate modus of each column.
        modus: most common value in column
        :return: List[Optional[float, Const]]
        """

        modes = []
        for i in range(self.columns):
            column_data = [data[i].value if isinstance(data[i], (Data, Const)) else data[i] for data in self.datas]
            mode = column_data[0]
            counter = column_data.count(mode)
            for i2 in range(counter):
                column_data.remove(mode)

            while len(column_data) > 0:
                data = column_data[0]
                new_counter = column_data.count(data)
                if new_counter > counter:
                    mode = data
                    counter = new_counter
                for i2 in range(new_counter):
                    column_data.remove(data)

            if self.units[i] != Unit():
                mode = Const(value=mode, sign=self.units[i])
            modes.append(mode)
        return modes

    def max(self):
        """
        return the max of each column.
        :return: List[Optional[float, Data, Const]]
        """

        result = []
        for i in range(0, self.columns):
            current_column_datas = [element[i] for element in self.datas]
            maxi = False
            maxi_value = False
            for element in current_column_datas:
                if isinstance(element, (Data, Const)):
                    value = element.value
                else:
                    value = element

                if maxi is False or value > maxi_value:
                    maxi = element
                    maxi_value = value

            if not (self.units[i].denominator or self.units[i].numerator):
                pass
            elif isinstance(maxi, Data):
                maxi = Data(value=str(maxi.value), error=str(maxi.error), sign=self.units[i], power=maxi.power,
                            n=maxi.n)
            elif isinstance(maxi, Const):
                maxi = Const(value=maxi.value, sign=self.units[i])
            result.append(maxi)

        return result

    def min(self):
        """
        return the min of each column.
        :return: List[Optional[float, Data, Const]]
        """

        result = []
        for i in range(0, self.columns):
            current_column_datas = [element[i] for element in self.datas]
            mini = False
            mini_value = False
            for element in current_column_datas:
                if isinstance(element, Data):
                    value = element.value
                else:
                    value = element
                if mini is False or value < mini_value:
                    mini = element
                    mini_value = value

            if not (self.units[i].numerator or self.units[i].denominator):
                pass
            elif isinstance(mini, Data):
                mini = Data(value=str(mini.value), error=str(mini.error), sign=self.units[i], power=mini.power,
                            n=mini.n)
            elif isinstance(mini, Const):
                mini = Const(value=mini.value, sign=self.units[i])
            result.append(mini)

        return result

    def delete(self, line_index):
        """
        Delete the data-row at line_index.
        :param line_index: int = index for row to delete
        :return: void
        """

        del self.datas[line_index]
        return True

    def drop(self, line_index):
        """
        Return and delete data-row at line_index
        :param line_index: int = index for row to delete
        :return: Tuple[Optional[int, float, Const, Data]] = row to drop
        """

        results = self.datas.pop(line_index)
        new_results = []
        for index, result in enumerate(results):
            if self.units[index] != Unit():
                if isinstance(result, (Data, Const)):
                    result.unit = self.units[index]
                    new_results.append(result)
                else:
                    new_result = Const(value=result, sign=self.units[index])
                    new_results.append(new_result)
            else:
                new_results.append(result)
        return new_results

    def add_column(self, name="", sign=""):
        """
        Adds a column to table.
        :param name: str = name of the new table
        :param unit: Union[str, Unit] = unit of the new column
        :return: void
        """

        if name == "":
            self.column_names.append(f"Column {self.columns}")
        else:
            self.column_names.append(name)
        self.columns += 1

        if isinstance(sign, str):
            sign = sign.split("/")
            if len(sign) > 1:
                sign = ["" if s == "1" else s for s in sign]
                unit = Unit(sign[0], sign[1])
            else:
                unit = Unit(sign[0])
            self.units.append(unit)

        elif isinstance(sign, Unit):
            self.units.append(sign)
        else:
            raise TypeError(f"Expected unit or string got {type(sign)} instead")

        for index in range(len(self.datas)):
            element = self.datas[index][:]
            element = list(element)
            element += [""]
            element = tuple(element)
            self.datas[index] = element
        return True

    def insert(self, line, column, value):
        """
        insert a value at line, column in table
        :param line: int; line in the table
        :param column: int; column in the table
        :param value: Optional[float, int, Data, Const]; new value for slot
        :return: void
        """

        if isinstance(value, Data):
            value = Data(value=str(value.value), error=str(value.error), sign=Unit(""), n=value.n, power=value.power)
        elif isinstance(value, Const):
            value = Const(value=value.value, sign=Unit(""))
        data_l = self.datas[line][:]
        data_l = list(data_l)
        data_l[column] = value
        data_l = tuple(data_l)
        self.datas[line] = data_l
        return True

    def export(self, path, name, replace_dot=False):
        """
        Exports data in .csv format
        :param path: path to .csv file (.csv in name needed)
        :param replace_dot: difference between english and german floats "3.11", "3,11"
        :return: void
        """

        # check if any value in a column has an error (is a Data)
        data_cols = [any([isinstance(row[i], Data) for row in self.datas]) for i in range(self.columns)]

        with open(path + "/" + name, "w", encoding="UTF-8") as doc:
            # write table headers
            doc.write("".join([f"{h_str};;" if data_col else f"{h_str};"
                               for data_col, h_str in zip(data_cols,
                                                          [f"{column_name} [{unit}]" if unit != Unit("")
                                                           else column_name
                                                           for column_name, unit in zip(self.column_names, self.units)])
                               ]) + "\n")

            doc.write("".join(["Bestwert; Fehler;" if data_col else "Bestwert;" for data_col in data_cols]) + "\n")

            # write data
            for row in self.datas:
                data_string = "".join([f"{data.value};{data.error};" if data_col
                                       else f"{data.value};" if type(data) == Const else f"{data};"
                                       for data, data_col in zip(row, data_cols)]) + "\n"
                if replace_dot:
                    data_string = data_string.replace(".", ",")

                doc.write(data_string)


if __name__ == "__main__":
    pass
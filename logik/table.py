from logik.data import Data, Const
from logik.unit import Unit
from logik.formula import Formula


class Table(object):

    def __init__(self, column_names=[], columns=2, signs=[]):
        """
        Creates a Table-Object
        :param column_names: List[str]; Names of the columns
        :param columns: int; number of columns
        :param signs: List[Optional[Unit, str]]; sign or unit of each column
        """
        self.datas = []
        self.columns = columns
        self.column_names = []

        if not signs:
            self.units = [Unit("") for i in range(self.columns)]
        else:
            self.units = []
            for sign in signs:
                if type(sign) == str:
                    sign = sign.split("/")
                    if len(sign) > 1:
                        unit = Unit(sign[0], sign[1])
                    else:
                        unit = Unit(sign[0])
                else:
                    unit = sign
                self.units.append(unit)

        if column_names == []:
            for i in range(self.columns):
                self.column_names.append("Column %s" % i)
        else:
            self.column_names = column_names

    def __str__(self):
        """
        Method to show a Table-Object
        :return: str = Table as string formatted
        """
        # + 3 for " [" and "]", +4 for additional space
        width = [len(self.column_names[i]) + len(str(self.units[i])) + 3 + 4 if len(str(self.units[i])) > 0\
                 else len(self.column_names[i]) + 4 for i in range(self.columns)]

        # check if a bigger column is necessary
        for column in range(self.columns):
            col_data = [data[column - 1] for data in self.datas]
            for slot_data in col_data:
                width[column - 1] = max(len(str(slot_data)) + 4, width[column - 1])

        string = ""
        for index, column_name in enumerate(self.column_names):
            unit_str = str(self.units[index])
            if unit_str != "":
                string += "%s" % column_name + " [" + unit_str + "]" + " " * (width[index] - len(column_name) - len(unit_str) - 3)
            else:
                string += "%s" % column_name + " " * (width[index] - len(column_name))
            # die -3 kommen aus " [" und "]"
            string += "|"
        string += "\n"
        string += "-" * (sum(width) + len(width)) + "\n"
        # Spaltennamen mit Einheiten einfügen

        for data in self.datas:
            for index, element in enumerate(data):
                """Alternative:"""
                if type(element) == Data:
                    new_element = Data(str(element.value), str(element.error), n=element.n)
                elif type(element) == Const:
                    new_element = element.value
                else:
                    new_element = element
                """ENDE Alternative"""
                string += "%s" % new_element + " " * (width[index] - len(str(new_element)))
                string += "|"
            if not (data is self.datas[-1]):
                string += "\n"
        #Spalten füllen

        return string

    def __add__(self, other):
        """
        merge two tables: Add the data of the other table into first one.
        :param other: Table-Object.
        :return: void
        """
        type_other = type(other)
        if type_other == Table:
            if self.columns == other.columns:
                if self.column_names != other.column_names:
                    raise NameError("Columns have different names")
                if self.units != other.units:
                    raise ValueError("At least two Columns have a different unit")
                new_table = Table(columns=self.columns, column_names=self.column_names, signs=self.units)
                new_table.datas = self.datas + other.datas
                return new_table
            else:
                raise ValueError("Tables have diffrent numbers of columns")
        else:
            raise ValueError("Unsupported operation '+' for table an %s" % type_other)

    def calc(self, formula, index_dict, column_name="", sign=True):
        """
        Method for calculating new columns with dependencies to others given by a formula.
        The new column is added to the current data.
        :param formula: Formula-Object; Connection between parameters, and table columns
        :param index_dict: Dict[str, Optional[int, str]];
            key (str): name of variable or parameter in formula-object
            value (int): index of column in table for the parameter at key
            value (str): fixed parameter for equation. Should be str(<float>) (equal for all columns)
        :param column_name: str; Name of the arising column
        :param sign: Optional[Unit, str]; sign/unit of the arising column
        :return: void
        """
        # formula = Object of class Formula; index_dict = {"x":1,"y":0}
        if type(formula) != Formula:
            raise ValueError("Given formula is not of type formula!")

        if column_name == "":
            column_name = "Column %s" % self.columns
        self.column_names.append(column_name)
        # add column_name

        self.columns += 1
        # Update column-counter

        new_data = []
        for element in self.datas:
            new_dict = {}
            type_dict = {}
            for key, index in index_dict.items():
                if type(index) == int:
                    new_dict[key] = element[index]
                    type_dict[key] = type(element[index])
                elif type(index) == str:
                    new_dict[key] = float(index)
                    type_dict[key] = float
                else:
                    new_dict[key] = index
                    type_dict[key] = type(self.datas[0][index])
            result = formula.calc(new_dict)

            new_data.append(tuple(list(element) + [result]))
        self.datas = new_data
        # calculate for all rows in Table and update self.datas

        if self.datas:
            if sign is True:
                unit = formula.calc_unit(new_dict, type_dict)
                self.units.append(unit)
            elif sign is False:
                self.units.append(Unit(""))
            else:
                self.units.append(sign)
            # update units

    def add(self, data_tuple):
        """
        Adds a data-row to table
        :param data_tuple: Tuple[Optional[int, float, Const, Data]] data for each column of table
        :return: void
        """
        type_tuple = type(data_tuple)

        if type_tuple == list:
            data_tuple = tuple(data_tuple)
        elif type_tuple != tuple:
            raise ValueError("Expected a tuple, get %s instead" % type_tuple)

        if len(data_tuple) == self.columns:
            for index, data in enumerate(data_tuple):
                if type(data) in [Data, Const]:
                    if data.unit != self.units[index] and data.unit != Unit(""):
                        raise Exception("Can´t fill column of %s with %s" % (self.units[index], data.unit))
                    elif data.unit == Unit(""):
                        data_tuple[index].unit = self.units[index]
            self.datas.append(data_tuple)
        else:
            raise ValueError("Expected an tuple of %s, get tuple of %s instead" % (self.columns, len(data_tuple)))

    def arithmetic_average(self):
        """
        calculates the arithmetic_average and their std_error for all columns.
        In case of Data column the average will be the weighted average
        average: 1/N * sum(data)
        std_error: sqrt( sum(data - average)^2 * 1/(n * (n - 1)) )
        weighted average: 1 / sum(1/(error^2)) * sum(data/(error^2))
        weighted error: sqrt( sum(1/(error^2)) )
        :return: List[Data]; List for each column of average and std_error
        """
        averages = []
        n = float(len(self.datas))
        for i in range(self.columns):
            if type(self.datas[0][i]) != Data:
                if type(self.datas[0][i]) == Const:
                    average = sum(data[i].value for data in self.datas) / n
                    error = (sum((data[i].value - average) ** 2 for data in self.datas) / (n * (n - 1))) ** 0.5
                else:
                    average = sum(data[i] for data in self.datas) / n
                    error = (sum((data[i] - average) ** 2 for data in self.datas) / (n * (n - 1))) ** 0.5
            else:
                w = sum([1 / data[i].error ** 2 for data in self.datas])
                wx = sum([data[i].value / data[i].error ** 2 for data in self.datas])

                average = wx / w
                error = 1 / w ** 0.5

            if error != 0.0:
                data = Data(value=str(average),
                            error=str(error),
                            n=2,
                            sign=self.units[i])
            elif self.units[i].denominator or self.units[i].numerator:
                data = Const(value=average,
                             sign=self.units[i])
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
        n = float(len(self.datas))
        for i in range(self.columns):
            prod = 1
            for data in self.datas:
                if type(data) in [Data, Const]:
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
        n = float(len(self.datas))
        for i in range(self.columns):
            column_data = [data[i].value if type(data) in [Data, Const] else data[i] for data in self.datas]
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
            column_data = [data[i].value if type(data[i]) in [Data, Const] else data[i] for data in self.datas]
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

    def find_peaks(self):
        """
        search for all peaks in all columns. A peak is defined as x_{n-1} < x_{n} > x_{n+1}
        :return: List[List[Optional[float, Const, Data]]]
        """
        peaks = []
        n = len(self.datas)
        for i in range(self.columns):
            current_peaks = []
            current_indice = []
            column_data = [data[i].value if type(data) in [Data, Const] else data[i] for data in self.datas]

            for index in range(1, n - 1):
                if column_data[index] > column_data[index + 1] and column_data[index] > column_data[index - 1]:
                    current_indice.append(index)

            has_unit = self.units[i].denominator or self.units[i].numerator
            for current_index in current_indice:
                data = self.datas[current_index][i]
                if type(data) == Data:
                    new_data = Data(value=str(data.value),
                                    error=str(data.error),
                                    sign=self.units[i],
                                    power=data.power,
                                    n=data.n)
                elif type(data) == Const:
                    new_data = Const(value=data.value,
                                     sign=self.units[i])
                elif has_unit:
                    new_data = Const(value=data,
                                     sign=self.units[i])
                else:
                    new_data = data
                current_peaks.append(new_data)
            peaks.append(current_peaks)
        return peaks

    def find_dips(self):
        """
        search for all dips in all columns. A dip is defined as x_{n-1} > x_{n} < x_{n+1}
        :return: List[List[Optional[float, Const, Data]]]
        """
        dips = []
        n = len(self.datas)
        for i in range(self.columns):
            current_dips = []
            current_indice = []
            column_data = [data[i].value if type(data) in [Data, Const] else data[i] for data in self.datas]

            for index in range(1, n - 1):
                if column_data[index] < column_data[index + 1] and column_data[index] < column_data[index - 1]:
                    current_indice.append(index)

            has_unit = self.units[i].denominator or self.units[i].numerator
            for current_index in current_indice:
                data = self.datas[current_index][i]
                if type(data) == Data:
                    new_data = Data(value=str(data.value),
                                    error=str(data.error),
                                    sign=self.units[i],
                                    power=data.power,
                                    n=data.n)
                elif type(data) == Const:
                    new_data = Const(value=data.value,
                                     sign=self.units[i])
                elif has_unit:
                    new_data = Const(value=data,
                                     sign=self.units[i])
                else:
                    new_data = data
                current_dips.append(new_data)
            dips.append(current_dips)
        return dips

    def modus(self):
        """
        calculate modus of each column.
        modus: most common value in column
        :return: List[Optional[float, Const, Data]]
        """
        modes = []
        for i in range(self.columns):
            column_data = [data[i].value if type(data[i]) in [Data, Const] else data[i] for data in self.datas]
            mode = [column_data[0]]
            counter = column_data.count(mode[0])
            for i2 in range(counter):
                column_data.remove(mode[0])

            while len(column_data) > 0:
                data = column_data[0]
                new_counter = column_data.count(data)
                if new_counter > counter:
                    mode = [data]
                    counter = new_counter
                elif new_counter == counter:
                    mode.append(data)
                for i2 in range(new_counter):
                    column_data.remove(data)

            if self.units[i].denominator or self.units[i].numerator:
                mode = Const(value=mode,
                             sign=self.units[i])
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
                if type(element) == Data:
                    value = element.value
                else:
                    value = element
                if maxi is False or value > maxi_value:
                    maxi = element
                    maxi_value = value

            if not (self.units[i].denominator or self.units[i].numerator):
                pass
            elif type(maxi) == Data:
                maxi = Data(value=str(maxi.value),
                            error=str(maxi.error),
                            sign=self.units[i],
                            power=maxi.power,
                            n=maxi.n)
            elif type(maxi) == Const:
                maxi = Const(value=maxi.value,
                             sign=self.units[i])

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
                if type(element) == Data:
                    value = element.value
                else:
                    value = element
                if mini is False or value < mini_value:
                    mini = element
                    mini_value = value

            if not (self.units[i].numerator or self.units[i].denominator):
                pass
            elif type(mini) == Data:
                mini = Data(value=str(mini.value),
                            error=str(mini.error),
                            sign=self.units[i],
                            power=mini.power,
                            n=mini.n)
            elif type(mini) == Const:
                mini = Const(value=mini.value,
                             sign=self.units[i])
            result.append(mini)
        return result

    def delete(self, line_index):
        """
        delete the data-row at line_index
        :param line_index: int
        :return: void
        """
        del self.datas[line_index]
        return True

    def drop(self, line_index):
        """
        return and delete data-row at line_index
        :param line_index: int
        :return: Tuple[Optional[int, float, Const, Data]]
        """
        results = self.datas.pop(line_index)
        new_results = []
        for index, result in enumerate(results):
            if self.units[index].denominator or self.units[index].numerator:
                if type(result) in [Data, Const]:
                    result.unit = self.units[index]
                    new_results.append(result)
                else:
                    new_result = Const(value=result,
                                   sign=self.units[index])
                    new_results.append(new_result)
        return new_results

    def add_column(self, name=""):
        """
        Adds a column to table.
        :param name: str; name of the new table
        :return: void
        """
        if name == "":
            self.column_names.append("Column %s" % self.columns)
        else:
            self.column_names.append(name)
        self.columns += 1

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
        if type(value) == Data:
            value = Data(value=str(value.value),
                         error=str(value.error),
                         sign=Unit(""),
                         n=value.n,
                         power=value.power)
        elif type(value) == Const:
            value = Const(value=value.value,
                          sign=Unit(""))
        data_l = self.datas[line][:]
        data_l = list(data_l)
        data_l[column] = value
        data_l = tuple(data_l)
        self.datas[line] = data_l
        return True

    def export(self, path, replace_dot=False):
        """
        Exports data in .csv format
        :param path: path to .csv file (.csv in name needed)
        :param replace_dot: difference between english and german floats "3.11", "3,11"
        :return: void
        """
        data_cols = [any([isinstance(row[i], Data) for row in self.datas]) for i in range(self.columns)]

        doc = open(path, "w", encoding="UTF-8")
        try:
            # columnname1|   |
            # value| error |

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

        finally:
            doc.close()

    def import_(self, path):
        pass


if __name__ == "__main__":
    from logik.formula import Formula
    tab = Table(columns=2, column_names=["x", "y"], signs=["", "mV"])

    for i in range(1, 100):
        tab.add([i, Data(str(i), "0.05")])
    #print(tab)

    f = Formula("2/x")
    tab.calc(f, {"x": 0}, column_name="z")
    tab.calc(f, {"x": 1}, column_name="a")

    f = Formula("a * x / y * z")
    tab.calc(f, {"a": "3", "x": 1, "y": 2, "z": 3})
    print(tab)
    tab.export(r"C:\Users\NPC\Desktop\dummy.csv", replace_dot=True)
    #print(tab.datas[0][3])
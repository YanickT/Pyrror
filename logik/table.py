from logik.data import Data, Const
from logik.unit import Unit
from logik.formula import Formula


class Table(object):

    def __init__(self, column_names=[], columns=2, signs=[]):
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

    def __str__(self):  # str()
        width = [len(self.column_names[i]) + len(str(self.units[i])) + 3 + 4 if len(str(self.units[i])) > 0\
                 else len(self.column_names[i]) + 4 for i in range(self.columns)]
        # die + 3 kommen aus " [" und "]". Die +4 sind ein zusätzlicher Abstand
        # Mindestbreite jeder Spalte

        for column in range(self.columns):
            col_data = [data[column - 1] for data in self.datas]
            for slot_data in col_data:
                width[column - 1] = max(len(str(slot_data)) + 4, width[column - 1])
        #überprüfen ob ein Datensatz eine größere Spalte braucht

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

    def __add__(self, other):  # +
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
                self.units.append("")
            else:
                self.units.append(sign)
            # update units

    def add(self, data_tuple):
        type_tuple = type(data_tuple)

        if type_tuple == list:
            data_tuple = tuple(data_tuple)
        elif type_tuple != tuple:
            raise ValueError("Expected a tuple, get %s instead" % type_tuple)

        if len(data_tuple) == self.columns:
            """
            new_data = []
            for index, data in enumerate(data_tuple):
                if type(data) == Data:
                    if self.units[index] != Unit(""):
                        if self.units[index] != data.unit and data.unit != Unit(""):
                            raise Exception("Can´t fill column of %s with %s" % (self.units[index], data.unit))
                        new_one = Data(value=str(data.value),
                                       error=str(data.error),
                                       n=data.n,
                                       sign=Unit(""))
                        new_data.append(new_one)
                    else:
                        new_data.append(data)

                elif type(data) == Const:
                    if self.units[index] != Unit(""):
                        if self.units[index] != data.unit and data.unit != Unit(""):
                            raise Exception("Can´t fill column of %s with %s" % (self.units[index], data.unit))
                        new_one = Const(value=data.value,
                                        sign=Unit(""))
                        new_data.append(new_one)
                    else:
                        new_data.append(data)
                        
                else:
                    new_data.append(data)
            self.datas.append(new_data)
            """
            """Alternative:"""
            for index, data in enumerate(data_tuple):
                if type(data) in [Data, Const]:
                    if data.unit != self.units[index] and data.unit != Unit(""):
                        raise Exception("Can´t fill column of %s with %s" % (self.units[index], data.unit))
                    elif data.unit == Unit(""):
                        data_tuple[index].unit = self.units[index]
            self.datas.append(data_tuple) # alternativ dieses entfernen
        else:
            raise ValueError("Expected an tuple of %s, get tuple of %s instead" % (self.columns, len(data_tuple)))

    def arithmetic_average(self):
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
        del self.datas[line_index]
        return True

    def drop(self, line_index):
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


if __name__ == "__main__":
    from logik.formula import Formula
    tab = Table(columns=2, column_names=["x", "y"], signs=["", "mV"])

    for i in range(1,100):
        tab.add([i, Data(str(i), "0.05")])
    print(tab)

    f = Formula("2/x")
    tab.calc(f, {"x": 0}, column_name="z")
    tab.calc(f, {"x": 1}, column_name="a")

    f = Formula("a * x / y * z")
    tab.calc(f, {"a": "3", "x": 1, "y": 2, "z": 3})
    print(tab)
    print(tab.datas[0][3])
from flask import Flask, request, render_template
import re
import math

import generator

# шаблоны для поиска необходимых частей и операций в коде
i_for = 'for\s+\(i?n?t?\s*[a-zA-Z]+\w*\s*=\s*\w+;\s*[a-zA-Z]+\w*\s*[<>!]=?\s*\w+;\s*[a-zA-Z]+\w*[\+\-][\+\-\=]\s*[\-]?\w*\)'
i_var = 'int\s+[a-zA-Z]+\w*\s*=\s*[\-]?\d+;'
i_arr = 'int\[\]\s+[a-zA-Z]+\w*\s*=\s*new\s+int\[[\-]?\w+\];'
i_in = '[a-zA-Z]+\w*\[[a-zA-Z]+\w*\s*[\+\-]?\s*\w*\]\s*=\s*\(?[a-zA-Z]+\w*\s*[\+\-]?\s*\w*\)?\s*\*\s*\(?[a-zA-Z]+\w*\s*[\+\-]?\s*\w*\)?;'
i_inp = '[a-zA-Z]+\w*\[[a-zA-Z]+\w*\s*[\+\-]?\s*\w*\]\s*=\s*\(int\)\s*Math\.pow\s*\(\(?[a-zA-Z]+\w*\s*[\+\-]?\s*\w*\)?,\s*2\);'
i_out = 'System\.out\.printl?n?\s*\([a-zA-Z]+\w*\[[a-zA-Z]+\w*\s*[\+\-]?\s*\w*\]\);'

name_inc = ''  # имя счетчика в цикле
name_size = ''  # имя переменной для определения массива
name_arr = ''  # имя массива
name_size_value = 0  # размер массива
name_inc_start = 0  # начальное значение счетчика в цикле
name_inc_end = ''  # максимальное значение счетчика в цикле
max_value = 0  # максимальное значение счетчика в цикле
type_compare = ''  # тип сравнения в условии цикла
type_next = ''  # тип выражения перехода на следующую итерацию цикла
num_next = 1  # на сколько увеличивается счетчик цикла при переходе на следующую итерацию

allowed_type_compare = ['<', '<=', '>', '>=', '!=']  # возможные типы сравнения в условии цикла
allowed_type_next = ['++', '+=', '--', '-=']  # возможные типы выражения перехода на следующую итерацию цикла
var_set = []  # объявленные переменные в программе


def default_values(num=0):
    global name_inc, name_inc_start, name_inc_end, max_value, type_compare, type_next, num_next
    global name_size, name_size_value, name_arr
    name_inc = ''
    name_inc_start = 0
    name_inc_end = ''
    max_value = 0
    type_compare = ''
    type_next = ''
    num_next = 1
    if num != 0:
        name_arr = ''
        name_size = ''
        name_size_value = 0


def check_var(answer):
    global name_size, name_size_value
    global var_set
    message = []
    find_var = re.findall(i_var, answer)
    if len(find_var) == 0:
        message.append('Переменная для значения размера массива не объявляется в программе!')
        return message
    f = re.search('int\s+[a-zA-Z]+\w*\s*=', find_var[0]).group(0)
    find_var[0] = find_var[0][len(f):]
    f = f[len(re.search('int\s+', f).group(0)):]
    name_size = re.match('[a-zA-Z]+\w*', f).group(0)
    var_set.append(name_size)

    f = re.search('\s*[\-]?\d+;', find_var[0]).group(0)
    find_var[0] = find_var[0][len(f):]
    f = f[len(re.search('\s*', f).group(0)):]
    name_size_value = int(re.match('[\-]?\d+', f).group(0))
    if name_size_value <= 0:
        message.append('Задан нулевой или отрицательный размер массива!')

    if len(message) == 0:
        message.append('Размер массива определен корректно.')
    return message


def check_arr(answer):
    global name_arr
    message = []
    find_arr = re.findall(i_arr, answer)
    if len(find_arr) == 0:
        message.append('Массив не объявлен в программе!')
        return message
    f = re.search('int\[\]\s+[a-zA-Z]+\w*\s*=', find_arr[0]).group(0)
    find_arr[0] = find_arr[0][len(f):]
    f = f[len(re.search('int\[\]\s+', f).group(0)):]
    name_arr = re.match('[a-zA-Z]+\w*', f).group(0)
    var_set.append(name_arr)

    f = re.search('new\s+int\[[\-]?\w+\];', find_arr[0]).group(0)
    find_arr[0] = find_arr[0][len(f):]
    f = f[len(re.search('new\s+int\[', f).group(0)):]
    n = re.match('[\-]?\w+', f).group(0)
    if n.isdigit():
        if int(n) != name_size_value:
            message.append('Размер массива не совпадает с указанным выше!')
            if int(n) <= 0:
                message.append('Задан нулевой или отрицательный размер массива!')
    elif n not in var_set:
        message.append('Неопределенный идентификатор ' + n)
    elif name_size != n:
        message.append('Размер массива не совпадает с указанным выше!')

    if len(message) == 0:
        message.append('Массив определен корректно.')
    return message


def check_for(answer, number):
    global name_inc, name_inc_start, name_inc_end, max_value, num_next
    global type_compare, type_next, allowed_type_compare, allowed_type_next
    message = []
    find_for = re.findall(i_for, answer)
    if len(find_for) == 0:
        message.append('Цикл for не найден в программе!')
        return message
    f = re.search('i?n?t?\s*[a-zA-Z]+\w*\s*=\s*\w+;\s*', find_for[number]).group(0)
    find_for[number] = find_for[number][len(f):]
    _int = re.search('int\s+', f)
    if _int != None:
        f = f[len(_int.group(0)):]
    name_inc = re.match('[a-zA-Z]+\w*', f).group(0)
    if _int != None:
        var_set.append(name_inc)
    if name_inc not in var_set:
        message.append('Неопределенный идентификатор ' + name_inc)
    f = f[len(name_inc):]
    f = f[len(re.match('\s*=\s*', f).group(0)):]
    inc_start = re.match('\w+', f).group(0)
    if inc_start.isdigit():
        name_inc_start = int(inc_start)
    elif inc_start == name_size:
        name_inc_start = name_size_value
    else:
        message.append('Не определено стартовое значение счетчика цикла!')

    f = re.search('[a-zA-Z]+\w*\s*[<>!]=?\s*\w+;', find_for[number]).group(0)
    find_for[number] = find_for[number][len(f):]
    n = re.match('[a-zA-Z]+\w*', f).group(0)
    if n != name_inc:
        message.append('Условие цикла не контролирует счетчик!')
        if n not in var_set:
            message.append('Неопределенный идентификатор ' + n)
    f = f[len(n):]
    f = f[len(re.match('\s*', f).group(0)):]
    type_compare = re.search('[<>!]=?', f).group(0)
    if type_compare not in allowed_type_compare:
        message.append('Условное выражение цикла некорректно!')
    f = f[len(type_compare):]
    f = f[len(re.match('\s*', f).group(0)):]
    name_inc_end = re.match('\w+', f).group(0)
    if not name_inc_end.isdigit():
        if name_inc_end not in var_set:
            message.append('Неопределенный идентификатор ' + name_inc_end)

    f = re.search('[a-zA-Z]+\w*[\+\-][\+\-\=]\s*[\-]?\w*', find_for[number]).group(0)
    find_for[number] = find_for[number][len(f):]
    f = f[len(name_inc):]
    type_next = re.search('[\+\-][\+\-\=]', f).group(0)
    if type_next not in allowed_type_next:
        message.append('Выражение перехода на следующую итерацию цикла некорректно!')
    f = f[len(type_next):]
    f = f[len(re.match('\s*', f).group(0)):]
    a = re.search('[\-]?\w*', f)
    if a.group(0) == '-':
        message.append('Не определен шаг итераций цикла!')
    elif len(a.group(0)) != 0:
        if a.group(0).isdigit():
            num_next = int(a.group(0))
        elif a.group(0) not in var_set:
            message.append('Неопределенный идентификатор ' + a.group(0))
        elif (a.group(0) == name_inc) or (a.group(0) == name_size_value):
            message.append('Индекс выходит за пределы массива в цикле!')
    if num_next == 0:
        message.append('Счетчик не изменяет значение в течение цикла!')
    elif type_next == '-=':
        num_next *= -1
    elif type_next == '--':
        num_next = -1

    max_num = 0
    if name_inc_end == name_size:
        max_num = name_size_value
    elif name_inc_end.isdigit():
        max_num = int(name_inc_end)

    if type_compare == '<':
        max_value = max_num
    elif type_compare == '<=':
        max_value = max_num + 1
    elif type_compare == '>':
        max_value = name_inc_start
    elif type_compare == '>=':
        max_value = name_inc_start + 1

    if type_compare in ['<', '<=']:
        if num_next < 0:
            message.append('Тело цикла никогда не выполнится!')
        elif max_value - name_inc_start <= 0:
            message.append('Тело цикла никогда не выполнится!')
        elif max_value - name_inc_start > name_size_value:
            message.append('Индекс выходит за пределы массива в цикле!')
        elif max_value - name_inc_start < name_size_value:
            message.append('Цикл охватывает не все элементы массива!')
    elif type_compare in ['>', '>=']:
        if num_next > 0:
            message.append('Тело цикла никогда не выполнится!')
        if max_value - max_num <= 0:
            message.append('Тело цикла никогда не выполнится!')
        elif max_value - max_num > name_size_value:
            message.append('Индекс выходит за пределы массива в цикле!')
        elif max_value - max_num < name_size_value:
            message.append('Цикл охватывает не все элементы массива!')
        else:
            message.append('Условное выражение цикла некорректно!')

    if math.fabs(num_next) > 1:
        message.append('Цикл охватывает не все элементы массива!')

    if len(message) == 0:
        message.append('Цикл for найден, применяется корректно.')
    return message


def check_in(answer):
    message = []

    def check_arr_name(find):
        nonlocal f
        f = re.search('[a-zA-Z]+\w*\[[a-zA-Z]+\w*\s*[\+\-]?\s*\w*\]\s*=', find[0]).group(0)
        find[0] = find[0][len(f):]
        arr = re.match('[a-zA-Z]+\w*', f).group(0)
        if arr != name_arr:
            if arr not in var_set:
                message.append('Неопределенный идентификатор ' + arr)
            else:
                message.append('Имя массива не совпадает с именем объявленного ранее!')
        f = f[len(arr):]
        f = f[len(re.match('\[', f).group(0)):]
        ind_n = re.match('[a-zA-Z]+\w*', f).group(0)
        f = f[len(ind_n):]
        f = f[len(re.match('\s*', f).group(0)):]
        ind_z = re.match('[\+\-]?', f).group(0)
        f = f[len(ind_z):]
        f = f[len(re.match('\s*', f).group(0)):]
        ind_v = re.match('\w*', f).group(0)
        if (ind_n != name_inc) and (ind_v != name_inc):
            if ind_n not in var_set:
                message.append('Неопределенный идентификатор ' + ind_n)
            else:
                message.append('Вычисляется все время один и тот же элемент массива!')
        elif not ind_v.isdigit() and len(ind_v) != 0:
            if ind_v not in var_set:
                message.append('Неопределенный идентификатор ' + ind_v)
        elif len(ind_v) != 0:
            if (int(ind_v) - name_inc_start != 0) and (ind_z == '-'):
                message.append('Индекс выходит за пределы массива в цикле!')
            if (int(ind_v) - name_inc_start != 2) and (ind_z == '+'):
                message.append('Индекс выходит за пределы массива в цикле!')
        else:
            if ind_n == name_inc:
                message.append('Индекс выходит за пределы массива в цикле!')
            elif ind_n not in var_set:
                message.append('Неопределенный идентификатор ' + ind_n)
            else:
                message.append('Вычисляется все время один и тот же элемент массива!')
        if (ind_z == '*') and (ind_z == '/'):
            message.append('Риск выхода за пределы массива!')
        elif (ind_z != '-') and (ind_z != '+') and (ind_z != ''):
            message.append('Недопустимый арифметический знак внутри индекса элемента массива!')

    def check_num():
        nonlocal f
        set_n = re.match('[a-zA-Z]+\w*', f).group(0)
        f = f[len(set_n):]
        f = f[len(re.match('\s*', f).group(0)):]
        set_z = re.match('[\+\-]?', f).group(0)
        f = f[len(set_z):]
        f = f[len(re.match('\s*', f).group(0)):]
        set_v = re.match('\w*', f).group(0)
        f = f[len(set_v):]
        if set_v.isdigit():
            if (int(set_v) == 0) and (set_z == '/'):
                message.append('Деление на ноль при вычислении значения!')
            elif (int(set_v) == 0) and (set_z == '*'):
                message.append('Результат вычисления значения всегда равен нулю!')
        elif (set_n != name_inc) and (set_v != name_inc):
            message.append('При вычислении значения элемента массива результат не соответствует требуемому!')
        return set_n + set_z + set_v

    find_in = re.findall(i_in, answer)
    find_inp = re.findall(i_inp, answer)
    if (len(find_in) == 0) and (len(find_inp) == 0):
        message.append('Программа не заполняет массив квадратами чисел!')
        return message
    if len(find_inp) == 0:
        check_arr_name(find_in)
        f = re.search('\(?[a-zA-Z]+\w*\s*[\+\-]?\s*\w*\)?\s*\*\s*\(?[a-zA-Z]+\w*\s*[\+\-]?\s*\w*\)?;', find_in[0]).group(0)
        f = f[len(re.match('\(?', f).group(0)):]
        a1 = check_num()
        f = f[len(re.match('\)?\s*\*\s*\(?', f).group(0)):]
        a2 = check_num()
        if a1 != a2:
            message.append('Программа не заполняет массив квадратами чисел!')
    elif len(find_in) == 0:
        check_arr_name(find_inp)
        f = re.search('\(int\)\s*Math\.pow\s*\(\(?[a-zA-Z]+\w*\s*[\+\-]?\s*\w*\)?,\s*2\);', find_inp[0]).group(0)
        f = f[len(re.match('\(int\)\s*Math\.pow\s*\(\(?', f).group(0)):]
        check_num()

    if len(message) == 0:
        message.append('Заполнение массива происходит корректно.')
    return message


def check_out(answer):
    message = []
    find_out = re.findall(i_out, answer)
    if len(find_out) == 0:
        message.append('Программа не выводит массив на экран!')
        return message
    f = re.search('System\.out\.printl?n?\s*\(', find_out[0]).group(0)
    find_out[0] = find_out[0][len(f):]
    f = re.search('[a-zA-Z]+\w*\[[a-zA-Z]+\w*\s*[\+\-]?\s*\w*\]\);', find_out[0]).group(0)
    arr = re.match('[a-zA-Z]+\w*', f).group(0)
    if arr != name_arr:
        if arr not in var_set:
            message.append('Неопределенный идентификатор ' + arr)
        else:
            message.append('Имя массива не совпадает с именем объявленного ранее!')
    f = f[len(arr):]
    f = f[len(re.match('\[', f).group(0)):]
    ind = re.match('[a-zA-Z]+\w*', f).group(0)
    f = f[len(ind):]
    f = f[len(re.match('\s*', f).group(0)):]
    z = re.match('[\+\-]?', f).group(0)
    f = f[len(z):]
    f = f[len(re.match('\s*', f).group(0)):]
    num = re.match('\w*', f).group(0)
    if (ind != name_inc) and (num != name_inc):
        if ind not in var_set:
            message.append('Неопределенный идентификатор ' + ind)
        else:
            message.append('Выводится все время один и тот же элемент массива!')
    elif not num.isdigit() and len(num) != 0:
        if num not in var_set:
            message.append('Неопределенный идентификатор ' + num)
    elif len(num) != 0:
        if (int(num) - name_inc_start != 0) and (z == '-'):
            message.append('Индекс выходит за пределы массива в цикле!')
        if (int(num) - name_inc_start != 2) and (z == '+'):
            message.append('Индекс выходит за пределы массива в цикле!')
    else:
        if ind != name_inc:
            if ind not in var_set:
                message.append('Неопределенный идентификатор ' + ind)
            else:
                message.append('Выводится все время один и тот же элемент массива!')
    if (z == '*') and (z == '/'):
        message.append('Риск выхода за пределы массива!')
    elif (z != '-') and (z != '+') and (z != ''):
        message.append('Недопустимый арифметический знак внутри индекса элемента массива!')

    if len(message) == 0:
        message.append('Массив выводится корректно.')
    return message


app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    global var_set
    if request.method == 'POST':
        var_set = []
        stud_answer = request.form['answer']
        print(check_var(stud_answer))
        print(check_arr(stud_answer))
        print(check_for(stud_answer, 0))
        t = type_compare
        print(check_in(stud_answer))
        default_values()
        print(check_for(stud_answer, 1))
        print(check_out(stud_answer))
        generator.start(stud_answer, name_size, name_arr, name_inc, name_size_value, t, type_compare)
        default_values(1)

    return render_template('test.html')


if __name__ == "__main__":
    app.run()

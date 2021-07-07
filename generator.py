from main import *


def start(answer, var_per, arr, inc, max_elem, comp, comp1, m=0):
    if len(var_per) == 0:
        var_per = 'n'
    if len(arr) == 0:
        arr = 'arr'
    if len(inc) == 0:
        inc = 'i'

    outfile = open('program.java', 'w')
    message = check_var(answer)
    if message[0] == 'Размер массива определен корректно.':
        outfile.write(re.search(i_var, answer).group(0) + '\n')
    elif 'Задан нулевой или отрицательный размер массива!' in message:
        if max_elem < 0:
            outfile.write('int ' + var_per + ' = ' + str(0 - max_elem) + ';\n')
        else:
            outfile.write('int ' + var_per + ' = 5;\n')
    else:
        outfile.write('int ' + var_per + ' = 5;\n')

    message = check_arr(answer)
    if message[0] == 'Массив определен корректно.':
        outfile.write(re.search(i_arr, answer).group(0) + '\n')
    else:
        outfile.write('int[] ' + arr + ' = new int[' + var_per + '];\n')

    message = check_for(answer, 0)
    if message[0] == 'Цикл for найден, применяется корректно.':
        outfile.write(re.search(i_for, answer).group(0) + '\n')
    else:
        if comp == '<':
            outfile.write('for (int ' + inc + ' = 0; ' + inc + ' < ' + var_per + '; ' + inc + '++)\n')
        elif comp == '>':
            outfile.write('for (int ' + inc + ' = ' + var_per + '; ' + inc + ' > 0; ' + inc + '--)\n')
        elif comp == '>=':
            outfile.write('for (int ' + inc + ' = ' + var_per + ' -1; ' + inc + ' >= 0; ' + inc + '--)\n')
        else:
            outfile.write('for (int ' + inc + ' = 1; ' + inc + ' <= ' + var_per + '; ' + inc + '++)\n')

    message = check_in(answer)
    if message[0] == 'Заполнение массива происходит корректно.':
        if re.search(i_in, answer):
            outfile.write('\t' + re.search(i_in, answer).group(0) + '\n')
        else:
            outfile.write('\t' + re.search(i_inp, answer).group(0) + '\n')
    else:
        if comp in ['<', '>']:
            outfile.write('\t' + arr + '[' + inc + '] = (' + inc + '+1) * (' + inc + '+1);\n')
        else:
            outfile.write('\t' + arr + '[' + inc + '-1] = ' + inc + ' * ' + inc + ';\n')

    default_values()
    message = check_for(answer, 1)
    if message[0] == 'Цикл for найден, применяется корректно.':
        outfile.write(re.findall(i_for, answer)[1] + '\n')
    else:
        if comp1 == '<=':
            outfile.write('for (int ' + inc + ' = 1; ' + inc + ' <= ' + var_per + '; ' + inc + '++)\n')
        elif comp1 == '>':
            outfile.write('for (int ' + inc + ' = ' + var_per + '; ' + inc + ' > 0; ' + inc + '--)\n')
        elif comp1 == '>=':
            outfile.write('for (int ' + inc + ' = ' + var_per + ' -1; ' + inc + ' >= 0; ' + inc + '--)\n')
        else:
            outfile.write('for (int ' + inc + ' = 0; ' + inc + ' < ' + var_per + '; ' + inc + '++)\n')

    message = check_out(answer)
    if message[0] == 'Массив выводится корректно.':
        outfile.write('\t' + re.search(i_out, answer).group(0) + '\n')
    else:
        if comp1 in ['<=', '>=']:
            outfile.write('\tSystem.out.println(' + arr + '[' + inc + '-1]);\n')
        else:
            outfile.write('\tSystem.out.println(' + arr + '[' + inc + ']);\n')

    outfile.close()
    if m == 0:
        if int(input('Чтобы запустить кейсы, нажмите 1 ')) == 1:
            case()


def case():
    for i in range(6):
        with open('cases/case' + str(i+1) + '.txt') as testing:
            stud_answer = testing.read()
            print('Кейс №', i+1)
            print(check_var(stud_answer))
            print(check_arr(stud_answer))
            print(check_for(stud_answer, 0))
            t = type_compare
            print(check_in(stud_answer))
            default_values()
            print(check_for(stud_answer, 1))
            print(check_out(stud_answer))
            start(stud_answer, name_size, name_arr, name_inc, name_size_value, t, type_compare, 1)
            default_values(1)
            print()

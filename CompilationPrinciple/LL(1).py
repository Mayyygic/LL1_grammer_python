"""
 -*- coding: utf-8 -*-
@Author  : njupt-B20030428梅家诚
@Time    : 2022/12/7
@Function: 实现LL(1)语法分析器
"""
import copy
import experiment1 as exp1


def get_vn(grammar):
    """获得一个语法的非终结符号集"""
    tmp_vn = []
    for key in grammar.keys():
        tmp_vn.append(key)
    tmp_vn = list(set(tmp_vn))
    return tmp_vn


def get_vt(grammar, vn):
    """获得一个语法的终结符号集"""
    tmp_vt = []
    for value in grammar.values():
        # print(value)
        for ele in value:
            for i in range(len(ele)):
                if ele[i] not in vn and ele[i] != "'":
                    tmp_vt.append(ele[i])
    tmp_vt = list(set(tmp_vt))
    return tmp_vt


def get_grammar(filename):
    """获得一个原始语法，返回：语法字典，非终结符号集，终结符号集"""
    fr = open(filename, encoding='utf-8')
    array_of_lines = fr.readlines()
    grammar = {}
    # 按行读取
    for line in array_of_lines:
        # 去除所读行的前后空格
        line = line.strip()
        # 分离产生式的左右部
        list_from_line = line.split('->')
        # 将读取的内容加入对应的字典的键的值中
        if list_from_line[0] not in grammar:
            grammar[list_from_line[0]] = list_from_line[1].split('|')
        for value in list_from_line[1].split('|'):
            grammar[list_from_line[0]].append(value)
        # 删除重复候选式
        grammar[list_from_line[0]] = list(set(grammar[list_from_line[0]]))
    o_vn = get_vn(grammar)
    o_vt = get_vt(grammar, o_vn)
    return grammar, list(grammar.keys())[0], o_vn, o_vt


def eliminate_left_recursion(o_grammar):
    """消除文法的左递归，返回：语法字典，非终结符号集，终结符号集"""
    new_grammar = {}
    for key in o_grammar.keys():
        # flg判断是否有形如A->Aα|β的文法
        flag = False
        for elm in o_grammar[key]:
            if elm[0] == key:
                flag = True
        for elm in o_grammar[key]:
            # 如果有形如A->Aα|β的形式
            if flag:
                if elm[0] == key:
                    tmp = ''
                    if key + "'" not in new_grammar.keys():
                        new_grammar[key + "'"] = []
                        for i in range(1, len(elm)):
                            tmp += elm[i]
                        tmp += key + "'"
                        new_grammar[key + "'"].append(tmp)
                    else:
                        for i in range(1, len(elm)):
                            tmp += elm[i]
                        tmp += key + "'"
                        new_grammar[key + "'"].append(tmp)
                    if 'ε' not in new_grammar[key + "'"]:
                        new_grammar[key + "'"].append('ε')
                else:
                    if key not in new_grammar.keys():
                        new_grammar[key] = []
                        new_grammar[key].append(elm + key + "'")
                    else:
                        new_grammar[key].append(elm + key + "'")
            # 如果没有上述形式否文法不改写
            else:
                if key not in new_grammar.keys():
                    new_grammar[key] = []
                    new_grammar[key].append(elm)
                else:
                    new_grammar[key].append(elm)
    new_vn = get_vn(new_grammar)
    new_vt = get_vt(new_grammar, new_vn)
    return new_grammar, new_vn, new_vt


def is_dict_equal(dict1, dict2):
    """判断两个字典包含的内容是否一样，注意不是完全相等！"""
    if len(dict1.keys()) != len(dict2.keys()):
        return False
    else:
        for key in dict1.keys():
            if key not in dict2.keys():
                return False
            else:
                if len(dict1[key]) != len(dict2[key]):
                    return False
                else:
                    for value in dict1[key]:
                        if value not in dict2[key]:
                            return False
    return True


def get_first(grammar, vn, vt):
    """获取一个语法中所有符号的FIRST集，以及产生式右部的FIRST集"""
    first = {}
    for x in vt:
        first[x] = []
        first[x].append(x)
    for x in vn:
        first[x] = []
    # 获取一个语法中所有符号的FIRST集
    while True:
        last_dict = copy.deepcopy(first)
        for x in vn:
            for value in grammar[x]:
                if value[0] == 'ε' or value[0] in vt:
                    first[x].append(value[0])
                else:
                    pointer = 0
                    while pointer < len(value):
                        if pointer < len(value) - 1 and value[pointer + 1] == "'":
                            tmp = value[pointer] + "'"
                            pointer += 1
                        else:
                            tmp = value[pointer]
                        if tmp not in first.keys():
                            first[tmp] = []
                        for y in first[tmp]:
                            if y != 'ε':
                                first[x].append(y)
                        if 'ε' not in grammar[tmp]:
                            break
                        pointer += 1
                    if pointer == len(value):
                        first[x].append('ε')
        for key in first.keys():
            first[key] = list(set(first[key]))
        new_dict = copy.deepcopy(first)
        if is_dict_equal(new_dict, last_dict):
            break
    # 获取产生式右部的FIRST集
    first_right = {}
    for value in grammar.values():
        for elm in value:
            if elm not in first_right.keys():
                first_right[elm] = []
            pointer = 0
            while pointer < len(elm):
                if pointer < len(value) - 1 and value[pointer + 1] == "'":
                    tmp = elm[pointer] + "'"
                    pointer += 1
                else:
                    tmp = elm[pointer]
                for y in first[tmp]:
                    if y != 'ε':
                        first_right[elm].append(y)
                if 'ε' not in first[tmp]:
                    break
                pointer += 1
            if pointer == len(elm):
                first_right[elm].append('ε')
    for key in first_right.keys():
        first_right[key] = list(set(first_right[key]))
    return first, first_right


def get_follow(grammar, start, first, vn):
    """获取一个语法中非终结符号的FOLLOW集"""
    follow = {}
    for n_value in vn:
        follow[n_value] = []
    follow[start].append('#')
    while True:
        last_follow = copy.deepcopy(follow)
        for sign in vn:
            for key in grammar.keys():
                for elm in grammar[key]:
                    flag = False
                    index = -1
                    if len(sign) == 1:
                        pos = 0
                        while pos < len(elm):
                            if sign == elm[pos] and pos + 1 < len(elm) and elm[pos + 1] != "'":
                                index = pos
                                flag = True
                            if sign == elm[pos] and pos == len(elm) - 1:
                                index = pos
                                flag = True
                            pos += 1
                    else:
                        pos = 0
                        while pos < len(elm) - 1:
                            if sign == elm[pos] + elm[pos + 1]:
                                flag = True
                                index = pos + 1
                            pos += 1

                    if flag:
                        if index == len(elm) - 1:
                            if sign != key:
                                for item in follow[key]:
                                    follow[sign].append(item)
                        else:
                            if index + 2 < len(elm) and elm[index + 2] == "'":
                                tmp = elm[index + 1] + "'"
                            else:
                                tmp = elm[index + 1]
                            for item in first[tmp]:
                                if item != 'ε':
                                    follow[sign].append(item)
                            # print()
                            if tmp in vn and 'ε' in grammar[tmp]:
                                if key != sign:
                                    for next_item in follow[key]:
                                        follow[sign].append(next_item)
                follow[sign] = list(set(follow[sign]))
        new_follow = copy.deepcopy(follow)
        if is_dict_equal(new_follow, last_follow):
            break
    return follow


def create_table(grammar, first, follow, vn, vt):
    """创建文法的分析表"""
    table = {}
    for value1 in vn:
        table[value1] = {}
        for value2 in vt:
            if value2 != 'ε':
                table[value1][value2] = []
        table[value1]['#'] = []
    for key in grammar.keys():
        for value in grammar[key]:
            for elm_fir in first[value]:
                if elm_fir != 'ε':
                    table[key][elm_fir].append(value)
                else:
                    for elm_fol in follow[key]:
                        table[key][elm_fol].append(value)
    return table


def record_al(log, step, log_analysis, log_info, expression):
    """记录分析器的一步分析信息"""
    full_log = '{: <10}'.format(str(step)) + '{: <20}'.format(log_analysis) + \
               '{: >20}'.format(log_info) + 10 * " " + '{: <20}'.format(expression)
    log.append(full_log)


def is_ll1(grammar, first_r, follow):
    """判断该文法是否是LL(1)文法"""
    for key in grammar.keys():
        if len(grammar[key]) > 1:
            for i in range(len(grammar[key])):
                for j in range(i + 1, len(grammar[key])):
                    # FIRST(α) ∩ FIRST(β) != ∅
                    if len(list(set(first_r[grammar[key][i]]) & set(first_r[grammar[key][j]]))) != 0:
                        return False
                    # A->α|β，若β=>*ε，贼FIRST(α) ∩ FOLLOW(A) != ∅
                    if 'ε' in first_r[grammar[key][i]]:
                        if len(set(first_r[grammar[key][j]]) & set(follow[key])) != 0:
                            return False
                    if 'ε' in first_r[grammar[key][j]]:
                        if len(set(first_r[grammar[key][i]]) & set(follow[key])) != 0:
                            return False
    return True


def ll_1_analysis(table, start, info, vn, vt):
    """LL(1)分析器"""
    analysis_stack = ['#', start]
    info_stack = []
    for value in info:
        info_stack.append(value)
    info_stack.append('#')
    # 记录步骤
    step = 0
    success = False
    log = []
    record_al(log, 'step', 'analysis_stack', 'input_string', 'production_used')
    while True:
        expression = ''
        step += 1
        log_analysis = ''
        for elm1 in analysis_stack:
            log_analysis += elm1
        log_info = ''
        for elm2 in info_stack:
            log_info += elm2
        analysis_sign = analysis_stack[-1]
        last_info = info_stack[0]
        if last_info != '#' and last_info not in vt:
            expression = "FAILURE"
            record_al(log, step, log_analysis, log_info, expression)
            break
        if analysis_sign in vn:
            if len(table[analysis_sign][last_info]) != 0:
                analysis_stack.pop()
                pointer = len(table[analysis_sign][last_info][0]) - 1
                if table[analysis_sign][last_info][0] != 'ε':
                    while pointer >= 0:
                        if table[analysis_sign][last_info][0][pointer] == "'":
                            tmp = table[analysis_sign][last_info][0][pointer - 1] + "'"
                            pointer -= 1
                        else:
                            tmp = table[analysis_sign][last_info][0][pointer]
                        analysis_stack.append(tmp)
                        pointer -= 1
                expression = analysis_sign + '->' + table[analysis_sign][last_info][0]
            else:
                expression = "FAILURE"
                record_al(log, step, log_analysis, log_info, expression)
                break
        elif analysis_sign == last_info:
            success = (analysis_sign == '#')
            if success:
                expression = "SUCCESS"
                record_al(log, step, log_analysis, log_info, expression)
                break
            else:
                analysis_stack.pop()
                del info_stack[0]
                expression = ''
        else:
            expression = "FAILURE"
            record_al(log, step, log_analysis, log_info, expression)
            break
        record_al(log, step, log_analysis, log_info, expression)
    return success, log


def w_to_file(log, filename):
    # 将所有分析信息存入文件
    fw = open(filename, mode='w', encoding='utf-8')
    for log_info in log:
        fw.write(log_info + '\n')


def record_g(log, grammar):
    """记录语法信息"""
    for key in grammar.keys():
        tmp = key + '->'
        for i in range(len(grammar[key])):
            if i == len(grammar[key]) - 1:
                tmp += grammar[key][i]
            else:
                tmp += grammar[key][i] + "|"
        log.append(tmp)


def record_v(log, v, name):
    """记录VN/VT信息"""
    tmp = name + '={'
    for i in range(len(v)):
        if i == len(v) - 1:
            tmp += v[i] + '}'
        else:
            tmp += v[i] + ','
    log.append(tmp)


def record_f(log, my_set, name):
    """记录FIRST集/FOLLOW集的信息"""
    for key in my_set.keys():
        tmp = name + '(' + key + ')={'
        for i in range(len(my_set[key])):
            if i == len(my_set[key]) - 1:
                tmp += my_set[key][i] + '}'
            else:
                tmp += my_set[key][i] + ','
        log.append(tmp)


def record_t(log, table):
    """记录分析表信息"""
    tmp = ''
    for key in table.keys():
        tmp += '{: ^10}'.format(' ')
        for key1 in table[key].keys():
            tmp += '{: ^10}'.format(key1)
        break
    log.append(tmp)
    for n_key in table.keys():
        tmp = ''
        tmp += '{: ^10}'.format(n_key)
        for t_key in table[n_key].keys():
            if len(table[n_key][t_key]) > 0:
                for val in table[n_key][t_key]:
                    tmp += '{: ^10}'.format(n_key + '->' + val)
            else:
                tmp += '{: ^10}'.format(' ')
        log.append(tmp)


def transform_input(input_string):
    """对文法的输入进行转换，但仅转换正整数"""
    result = ''
    tmp = ''
    index = 0
    while index < len(input_string):
        if input_string[index].isdigit():
            tmp += input_string[index]
            index += 1
            if index == len(input_string):
                result += 'i'
                tmp = ''
            continue
        else:
            if len(tmp) != 0:
                result += 'i'
                tmp = ''
            result += input_string[index]
        index += 1
    return result


def auto_ll1(grammar_file, input_str, log_file):
    result = False
    total_log = ['Original grammar:']
    # 获得最初的语法，文法的开始符号，非终结符号集，终结符号集
    my_grammar, start, vn, vt = get_grammar(grammar_file)
    # 记录信息
    record_g(total_log, my_grammar)
    record_v(total_log, vn, "VN")
    record_v(total_log, vt, "VT")
    total_log.append('Grammar after eliminate_left_recursion:')
    # 对文法进行左递归消除
    correct_grammar, correct_vn, correct_vt = eliminate_left_recursion(my_grammar)
    # 记录信息
    record_g(total_log, correct_grammar)
    record_v(total_log, correct_vn, "VN")
    record_v(total_log, correct_vt, "VT")
    # 获取所有符号的FIRST集，所有产生式有部的FIRST集
    my_first, my_first_r = get_first(correct_grammar, correct_vn, correct_vt)
    # 记录信息
    total_log.append('Create FIRST:')
    record_f(total_log, my_first, "FIRST")
    record_f(total_log, my_first_r, "FIRST")
    # 获取所有非终结符号的FOLLOW集
    my_follow = get_follow(correct_grammar, start, my_first, correct_vn)
    # 记录信息
    total_log.append('Create FOLLOW:')
    record_f(total_log, my_follow, "FOLLOW")

    # 判断是否为LL(1)文法
    if is_ll1(correct_grammar, my_first_r, my_follow):
        # 创建分析表
        my_table = create_table(correct_grammar, my_first_r, my_follow, correct_vn, correct_vt)
        # 记录信息
        total_log.append("Perform the analysis process:")
        total_log.append("Analysis Table:")
        record_t(total_log, my_table)
        # 获得分析结果和分析过程
        result, my_log = ll_1_analysis(my_table, start, input_str, correct_vn, correct_vt)
        total_log.append("Process of Analysis:")
        for value in my_log:
            total_log.append(value)
        if result:
            total_log.append('Analysis Result: The input string ' + '"' +
                             input_str + '"' + " is a sentence of the grammar")
        else:
            total_log.append('Analysis Result: The input string ' + '"' +
                             input_str + '"' + "is not a sentence of the grammar")
    else:
        total_log.append("Non-LL(1) grammar, analysis stops")
    # 将获得分析信息写入指定文件
    w_to_file(total_log, log_file)
    return total_log, result


# input_s = transform_input('98+99+80')
# input_s = transform_input('(106-80(*95)')
input_s = 'a*b+b'

analysis_log_info, analysis_result = auto_ll1('grammar.txt', input_s, 'Log.txt')
# print(transform_input('(106-80(*95)'))
print(analysis_result)

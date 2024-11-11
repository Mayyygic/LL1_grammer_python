def get_predefined_content(filename):
    """获得预先定义的关键字，界限符和运算符"""
    fr = open(filename, encoding='utf-8')
    array_of_lines = fr.readlines()
    return_dict = {}
    # 按行进行读取
    for line in array_of_lines:
        # 去除所读行的前后空格
        line = line.strip()
        # 获得以\t进行分割的列表
        list_from_line = line.split('\t')
        # 将读取的内容加入对应的字典的键的值中
        if list_from_line[1] not in return_dict:
            return_dict[list_from_line[1]] = []
        return_dict[list_from_line[1]].append(list_from_line[2])
    return return_dict


def lexical_analysis(filename, pre):
    """词法分析"""
    """pre为get_predefined_content函数返回的字典"""
    fr = open(filename, encoding='utf-8')
    array_of_lines = fr.readlines()
    # token用于拼接单词
    token = ''
    # result为字典类型，添加获得的token到对应的键值对中
    result = {'KeyWord': [], 'Separator': [], 'Operator': [], 'Identifier': [], 'Constant': []}
    # 按行进行读写文件
    for line in array_of_lines:
        line = line.strip()
        index = 0
        while index < len(line):
            # 判断是不是标识符
            if 'a' <= line[index] <= 'z' or 'A' <= line[index] <= 'Z' or line[index] == '_':
                while index < len(line) and ('a' <= line[index] <= 'z' or 'A' <= line[index] <= 'Z'
                                             or line[index].isdigit() or line[index] == '_'):
                    token += line[index]
                    index += 1
                # 判断token是不是预定义的KeyWord
                if token in pre['KeyWord']:
                    result['KeyWord'].append(token)
                else:
                    result['Identifier'].append(token)
                # 结束后token要置位空
                token = ''
            # 判断token是不是一个数字常量
            elif line[index].isdigit():
                while index < len(line) and line[index].isdigit():
                    token += line[index]
                    index += 1
                result['Constant'].append(token)
                token = ''
            # 判断是否是运算符
            elif line[index] in pre['Operator']:
                # 判断是否已经是最后一个
                if index + 1 < len(line):
                    # 判断是不是双符号运算符
                    if line[index] + line[index + 1] in pre['Operator']:
                        result['Operator'].append(line[index] + line[index + 1])
                        # 注释后面的内容不进行分析
                        if line[index] + line[index + 1] == '//':
                            break
                        index += 2
                    else:
                        result['Operator'].append(line[index])
                        index += 1
                else:
                    result['Operator'].append(line[index])
                    index += 1
            # 判断是不是分隔符
            else:
                if line[index] in pre['Separator']:
                    result['Separator'].append(line[index])
                index += 1
    return result


def output_analysis(filename, result):
    fw = open(filename, mode='w', encoding='utf-8')
    for elem in result.keys():
        for value in result[elem]:
            fw.write(elem+'\t'+value+'\n')


predefined = get_predefined_content("predefined_content.txt")
analysis_result = lexical_analysis("main.txt", predefined)
output_analysis("result_file.txt", analysis_result)


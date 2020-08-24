import json


def read_json_file(file_name):
    '''读取 json 文件中的数据
    Args:
        file_name: 文件名
    return:
        dict
    '''
    with open(file_name, 'r', encoding='utf-8') as f:
        content = json.load(f)
    return content


def write_json_file(file_name, data_dict):
    '''将字典类型的数据写入 json 文件中
    Args:
        file_name: 文件名
    return:
        none
    '''
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False)

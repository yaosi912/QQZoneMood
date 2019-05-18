from flask import send_from_directory, Blueprint, session
import json
from src.util.constant import *
import os

from src.web.entity.UserInfo import UserInfo
from src.web.web_util.web_util import check_password, get_redis_conn

data = Blueprint('data',__name__)

@data.route('/download_file/<QQ>/<password>/<file_type>')
def download_excel(QQ, password, file_type):
    pool_flag = session.get(POOL_FLAG)
    conn = get_redis_conn(pool_flag)
    if not check_password(conn, QQ, password):
        return json.dumps(dict(finish="QQ号与识别码不匹配"), ensure_ascii=False)

    else:
        if file_type == 'mood':
            path = BASE_DIR + QQ + "/data/result"
            if os.path.isfile(os.path.join(path, 'mood_data.xlsx')):
                print(os.path.join(path, 'mood_data.xlsx'))
                return send_from_directory(path, 'mood_data.xlsx', as_attachment=True)
            else:
                return json.dumps(dict(finish="文件不存在"), ensure_ascii=False)
        elif file_type == 'friend':
            path = BASE_DIR + QQ + "/friend"
            if os.path.isfile(os.path.join(path, 'friend_detail_list.xlsx')):
                return send_from_directory(path, 'friend_detail_list.xlsx', as_attachment=True)
            else:
                return json.dumps(dict(finish="文件不存在"), ensure_ascii=False)


@data.route('/clear_cache/<QQ>/<password>')
def clear_cache(QQ, password):
    pool_flag = session.get(POOL_FLAG)
    conn = get_redis_conn(pool_flag)
    if not check_password(conn, QQ, password):
        return json.dumps(dict(finish="QQ号与识别码不匹配"), ensure_ascii=False)
    else:
        try:
            DATA_DIR_KEY = BASE_DIR + QQ + '/'
            if os.path.exists(DATA_DIR_KEY):
                # 删除有QQ号的所有key
                delete_cmd = "redis-cli KEYS \"*" + QQ + "*\"|xargs redis-cli DEL"
                print(delete_cmd)
                os.system(delete_cmd)
                # 删除 该路径下所有文件
                os.system("rm -rf " + DATA_DIR_KEY)
                conn.hdel(USER_MAP_KEY, QQ)
                # os.removedirs(os.path.join(BASE_DIR, QQ))
                finish = 1
            else:
                finish = 2
            return json.dumps(dict(finish=finish), ensure_ascii=False)
        except BaseException as e:
            finish = 0
            print(e)
            return json.dumps(dict(info="未知错误：" + str(e), finish=finish), ensure_ascii=False)

@data.route('/get_history/<QQ>/<name>/<password>')
def get_history(QQ, name, password):
    pool_flag = session.get(POOL_FLAG)
    conn = get_redis_conn(pool_flag)
    result = {}
    if not check_password(conn, QQ, password):
        result['finish'] = 0
        return json.dumps(result)

    history = conn.get(BASE_DIR + QQ + '/friend/' + 'history_like_list.json')
    if history:
        history_json = json.loads(history)
        result['finish'] = 1
        result['data'] = history_json
    else:
        result['finish'] = -1
    return json.dumps(result, ensure_ascii=False)

@data.route('/userinfo/<QQ>/<name>/<password>')
def userinfo(QQ, name, password):
    pool_flag = session.get(POOL_FLAG)
    conn = get_redis_conn(pool_flag)
    if check_password(conn, QQ, password):
        user = UserInfo(QQ)
        user.load()
        result = dict(finish=1, user=user.to_dict())
        return json.dumps(result, ensure_ascii=False)
    else:
        result = dict(finish=0)
        return json.dumps(result, ensure_ascii=False)

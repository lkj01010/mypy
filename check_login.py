class CheckLogin(object):
    def __init__(self):
        self.user_cache = dict()
        self.user_expire_holder = [None] * 10000
        pass

    def check_info(self, user_id, user_key):
        if user_id in self.user_cache:
            return True
        else:
            '''should check from tencent server'''
            self.user_cache[user_id] = user_key
            self.user_expire_holder.append(user_id)
            expired = self.user_expire_holder.pop(0)
            if expired:
                del self.user_cache[expired]
            return True

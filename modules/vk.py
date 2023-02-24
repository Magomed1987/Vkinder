import vk_api
import datetime
from random import randrange
from vk_api.longpoll import VkLongPoll

from util.database import UsersDB
from config import user_token, comm_token

class VKBot:
    def __init__(self):
        self.vk = vk_api.VkApi(token=comm_token)
        self.user = vk_api.VkApi(token=user_token)
        self.longpoll = VkLongPoll(self.vk)
        self.db = UsersDB()

    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7)})

    def start_function(self, user_id: str):
        user_name, user_sex, birth_date, city, status = self.get_user_info(user_id=user_id)
        if not self.db.get(user_id, "*"):
            self.db.add_user(user_name, user_id)

        sex_changer = 1 if user_sex == 1 else -1
        user_sex += sex_changer

        db_age_from, db_city = self.db.get(id=user_id, queries="ageFrom, city")

        year_info = str(birth_date).split(".")
        if len(year_info) < 3 and not db_age_from:
            self.db.update(id=user_id, queries="valueAwaiter = 'ageFrom'")
            return self.write_msg(user_id, 'Введите ваш возраст (min - 16, max - 65): ')

        age_value = db_age_from if len(year_info) < 3 else int(datetime.date.today().year) - int(year_info[2])

        if not city and not db_city:
            self.write_msg(user_id=user_id, message='Введите название вашего города: ')
            return self.db.update(id=user_id, queries="valueAwaiter = 'city'")

        city_id = self.cities(db_city) if db_city and not city else city["id"]
        status = status or 6

        self.find_user(user_id, user_sex, age_value, city_id, status)
        self.write_msg(user_id, f'Привет, {user_name}.\nСписок пользователей собран, нажми кнопку "Вперёд"')

    def get_user_info(self, user_id):
        request = self.vk.method('users.get', {'user_ids': user_id,
                                               'fields': 'sex, bdate, city, relation'})

        return request[0]["first_name"], request[0]["sex"], request[0].get("bdate"), request[0].get("city"), request[0].get("relation")

    def cities(self, city_name):
        request = self.user.method('database.getCities', {'country_id': 1,
                                                          'q': city_name,
                                                          'need_all': 0,
                                                          'count': 1000})

        for i in request["items"]:
            if i.get('title') == city_name:
                return int(i.get('id'))

    def find_user(self, user_id, sex, age, city, relation):
        request = self.user.method('users.search', 
                                   {'sex': sex,
                                    'age_from': age,
                                    'age_to': age,
                                    'city': city,
                                    'relation': relation,
                                    'fields': 'is_closed, id, first_name, last_name',
                                    'status': '1' or '6',
                                    'count': 500})

        users = []
        for person in request["items"]:
            if person.get('is_closed'): continue

            first_name = person.get('first_name')
            last_name = person.get('last_name')
            vk_id = str(person.get('id'))
            users.append(f"{first_name}_{last_name}_{vk_id}")

        users_list = "\n".join(users)
        self.db.update(id=user_id, queries=f'userList = "{users_list}"')

    def show_users(self, user_id: str):
        users = self.db.get(id=user_id, queries="userList")[0].split("\n")
        if not users[0]:
            return self.write_msg(user_id=user_id, message="Нажмите кнопку 'Начать поиск', чтобы найти пользователей")

        target_id = users[0].split("_")[2]
        pictures = self.get_photos_id(target_id)
        attachments = [
            f'photo{target_id}_{pictures[i][1]}'
            for i in range(3 if len(pictures) > 3 else len(pictures))
        ]

        self.vk.method('messages.send', {'user_id': user_id,
                                        'message': "vk.com/id" + target_id,
                                        'attachment': ",".join(attachments),
                                        'random_id': 0})

        users.pop(0)
        users = "\n".join(users)
        self.db.update(id=user_id, queries=f'userList = "{users}"')

    def get_photos_id(self, user_id):
        request = self.user.method('photos.getAll', {'type': 'album',
                                                    'owner_id': user_id,
                                                    'extended': 1,
                                                    'count': 25})

        dict_photos = {}
        for i in request["items"]:
            if i.get('likes').get('count'):
                likes = i.get('likes').get('count')
                dict_photos[likes] = str(i.get('id'))

        return sorted(dict_photos.items(), reverse=True)
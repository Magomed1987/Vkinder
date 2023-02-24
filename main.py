from modules.vk import VKBot
from resources.keyboard import keyboard
from vk_api.longpoll import VkEventType

bot = VKBot()

commands = {
    'Вперёд': bot.show_users,
    'Начать поиск': bot.start_function,
}

for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        if event.text in commands:
            commands[event.text](user_id=event.user_id)
            continue
        
        if not bot.db.get(event.user_id, "*"):
            bot.db.add_user(bot.get_user_info(user_id=event.user_id)[0], event.user_id)
            
        value_awaiter = bot.db.get(event.user_id, "valueAwaiter")[0]
        if value_awaiter:
            change_value = event.message
            if value_awaiter == "ageFrom":
                try:
                    change_value = int(change_value)
                except:
                    bot.write_msg(user_id=event.user_id, message="Возраст неверного формата, пришлите пожалуйста число: ")
                    continue
            
            bot.db.update(id=event.user_id, queries=f"{value_awaiter} = '{change_value}', valueAwaiter = ''")
            bot.start_function(user_id=event.user_id)
            continue

        bot.vk.method('messages.send', {'user_id': event.user_id,
                                        'message': 'Добро пожаловать',
                                        'random_id': 0,
                                        'keyboard': keyboard})
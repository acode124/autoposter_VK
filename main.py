try:
    import time
    import os
    import vk_api
    import random
    import configparser

    parser = configparser.ConfigParser()
    parser.read('settings.ini')
    number = parser.get('account', 'number')
    password = parser.get('account', 'password')

    print('Загрузили переменные!')

    print('Подключаемся к ВК..')
    vk_session = vk_api.VkApi(number, password)
    vk_session.auth()

    vk = vk_session.get_api()
    uploader = vk_api.upload.VkUpload(vk)
    user_id = vk.users.get()[0]['id']
    print('Подключились к ВК!')

    while True:
        parser.read('settings.ini')
        count_user = int(parser.get('other', 'count_user'))
        timewait = int(parser.get('other', 'time'))

        print('Выбираем пост..')
        with open('posts.txt', 'r', encoding='utf-8') as file:
            links = file.readlines()

        link = random.choice(links).strip()

        try:
            right_part = link.split('wall')[1]
            owner_id, post_id = right_part.split('_')
        except:
            print('Некорректная ссылка')
            input()

        print('Выбрали пост..')
        comments = vk.wall.getComments(owner_id=owner_id, post_id=post_id, count=100)
        if 'count' not in comments and 'items' not in comments:
            print('Ошибка при получении комментариев с поста..')
            input()

        count = comments['count']
        items = []
        off = 0
        while True:
            comments = vk.wall.getComments(owner_id=owner_id, post_id=post_id, count=100, offset=off)
            if len(comments['items']) == 0:
                break
            off += 100
            items += comments['items']
            print(f'Загружаем еще комментариев..')
            time.sleep(0.5)

        if count < count_user:
            print(f'Кол-во комментариев на посту {link} меньше чем count_user!')
            input()

        users = []
        while len(users) < count_user:
            com = random.choice(items)
            if com['from_id'] in users:
                items.remove(com)
                continue
            users.append(com['from_id'])
            items.remove(com)
            print(f'Пользователь #{len(users)} добавлен для отметки в посте!')

        print('Получили юзеров!')

        name_photo = random.choice(os.listdir('images'))
        if not name_photo.startswith('[used]'):
            print('Новая фотка!')
            random_photo = 'images/' + name_photo
            photo = uploader.photo_wall(random_photo, user_id)
            media_id = photo[0]['id']
            owner_id = photo[0]['owner_id']
            attach = f'photo{owner_id}_{media_id}'
        else:
            print('Загрузка фото!')
            attach = name_photo.split('[used]')[1]

        with open('text.txt', 'r', encoding='utf-8') as file:
            text = file.read()

        text += '\n'
        for i in users:
            text += f'\n@id{i}'

        vk.wall.post(attachments=attach, message=text)
        print('Пост загружен!')
        if not name_photo.startswith('[used]'):
            os.rename(random_photo, f'images/[used]{attach}.{name_photo.split(".")[-1]}')
            print('Фотография помечена как добавленная в альбом!')

        print(f'Ожидаем {timewait} сек...')
        time.sleep(timewait)
except Exception as error:
    print('Ошибка')
    print(error)
    input()

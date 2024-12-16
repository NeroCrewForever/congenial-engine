blade_quests = {
    "start": {
        "text": "Ты на заброшенном кладбище. Блейд сидит в центре. Что ты делаешь?",
        "image": "https://i.pinimg.com/736x/10/96/c1/1096c1e592ee676a6e8bc1c4cc93bc0b.jpg",
        "options": [
            ("Поговорить с ним", "blade_talk"),
            ("Оставить его в покое", "blade_leave")
        ]
    },
    "blade_talk": {
        "text": "Ты начинаешь разговор с Блейдом. Он смотрит с подозрением. Спрашиваешь о прошлом или о настоящем?",
         "image": "https://sun9-76.userapi.com/impg/6PwAT_exDdVGUUm6dshtgAT37oRBPtkAS614RA/D4JuH2SN2iw.jpg?size=1280x791&quality=95&sign=6047b7d395a4b30bb0ac2361dd9a6b58&c_uniq_tag=472Q78q2i_iYs3CqZ8YtNU_iKvbkcmoOU-wp2v5wl5A&type=album",
        "options": [
            ("Спросить о прошлом", "blade_past"),
            ("Поговорить о настоящем", "blade_present")
        ]
    },
    "blade_leave": {
        "text": "Ты оставил Блейда. Он кивнул и продолжил размышлять. Ты уходишь ни с чем.",
         "image": "https://cs13.pikabu.ru/post_img/2024/05/27/10/og_og_1716826129287938874.jpg",
        "options": [
          ("Завершить", "blade_end_bad")
        ]
    },
    "blade_past": {
        "text": "Блейд рассказывает о боли и утратах. Ты предложишь помощь или сочувствие?",
        "image": "https://avatars.mds.yandex.net/i?id=149080c1a369a4ecbefc26eb2716c219_l-12316895-images-thumbs&n=13",
        "options": [
            ("Предложить помощь", "blade_help"),
            ("Сочувствовать", "blade_sympathy")
        ]
    },
    "blade_present": {
        "text": "Вы говорите о настоящем. Блейд расслаблен. Предложишь занятие или оставишь его?",
         "image": "https://i.pinimg.com/736x/10/96/c1/1096c1e592ee676a6e8bc1c4cc93bc0b.jpg",
        "options": [
            ("Предложить занятие", "blade_activity"),
            ("Оставить его", "blade_leave_again")
        ]
    },
      "blade_leave_again": {
        "text": "Ты снова оставил Блейда. Он кивнул и продолжил размышлять. Ты уходишь ни с чем.",
         "image": "https://cs13.pikabu.ru/post_img/2024/05/27/10/og_og_1716826129287938874.jpg",
        "options": [
          ("Завершить", "blade_end_bad")
        ]
    },
    "blade_help": {
        "text": "Блейд принимает помощь, но просит не задавать вопросов. Готов помочь или отступишь?",
        "image": "https://sun9-76.userapi.com/impg/6PwAT_exDdVGUUm6dshtgAT37oRBPtkAS614RA/D4JuH2SN2iw.jpg?size=1280x791&quality=95&sign=6047b7d395a4b30bb0ac2361dd9a6b58&c_uniq_tag=472Q78q2i_iYs3CqZ8YtNU_iKvbkcmoOU-wp2v5wl5A&type=album",
        "options": [
            ("Помочь", "blade_help_confirm"),
            ("Отступить", "blade_end_bad")
        ]
    },
    "blade_sympathy": {
        "text": "Ты просто сочувствуешь, Блейду этого мало. Вы прощаетесь.",
         "image": "https://avatars.mds.yandex.net/i?id=149080c1a369a4ecbefc26eb2716c219_l-12316895-images-thumbs&n=13",
         "options": [
           ("Завершить", "blade_end_bad")
        ]
    },
   "blade_activity": {
      "text": "Блейд согласен на занятие. Вы провели время с пользой. Продолжим или попрощаемся?",
      "image": "https://i.pinimg.com/736x/10/96/c1/1096c1e592ee676a6e8bc1c4cc93bc0b.jpg",
        "options": [
            ("Продолжить", "blade_continue"),
            ("Попрощаться", "blade_end_good")
        ]
    },
   "blade_continue": {
       "text": "Вы продолжаете общение. Блейд доволен. Расстаемся на позитивной ноте.",
         "image": "https://sun9-76.userapi.com/impg/6PwAT_exDdVGUUm6dshtgAT37oRBPtkAS614RA/D4JuH2SN2iw.jpg?size=1280x791&quality=95&sign=6047b7d395a4b30bb0ac2361dd9a6b58&c_uniq_tag=472Q78q2i_iYs3CqZ8YtNU_iKvbkcmoOU-wp2v5wl5A&type=album",
        "options": [
            ("Завершить", "blade_end_good")
        ]
   },
  "blade_help_confirm": {
        "text": "Ты помог Блейду. Он благодарен. Твоя помощь много значит для него.",
         "image": "https://cs13.pikabu.ru/post_img/2024/05/27/10/og_og_1716826129287938874.jpg",
        "options": [
           ("Завершить", "blade_end_good")
        ]
    },
    "blade_end_bad": {
        "text": "Квест завершен, но Блейд недоволен. Может, в другой раз.",
         "image": "https://i.pinimg.com/736x/10/96/c1/1096c1e592ee676a6e8bc1c4cc93bc0b.jpg",
        "options": [
          ("Завершить квест", "end")
        ]
    },
    "blade_end_good": {
        "text": "Квест завершен, Блейд доволен. Он благодарит тебя.\n\nХорошая работа!",
         "image": "https://avatars.mds.yandex.net/i?id=149080c1a369a4ecbefc26eb2716c219_l-12316895-images-thumbs&n=13",
         "options": [
           ("Завершить квест", "end")
        ]
    }
}
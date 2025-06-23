# 🎵 Playlist Manager

Удобный API для управления любимыми треками.

## 📦 Как запустить
1. Установить Docker и Docker Compose
2. Cкачать папку с проектом и перейти в неё в терминале:
```bash
cd playlist-manager
```
3. Запустить проект:
```bash
docker-compose up --build -d
```
4. Открыть в браузере:
    - Веб-интерфейс: [http://localhost:8000/ui](http://localhost:8000/ui)
    - Документация API (со Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
5. Чтобы остановить проект:
```bash
docker-compose down
```


## 🛠️ Что внутри
- FastAPI — Python-фреймворк для API
- MySQL — база данных для хранения треков
- SQLAlchemy — позволяет работать с базой данных через объекты и классы
- Docker + docker-compose — контейнеры для удобного запуска
- wait_for_it.sh — скрипт, который ждёт, пока база поднимется 

## 👀 Доступные эндпоинты

| Метод |  URL  | Описание |
|-------|-------------|-------------|
| GET   | /songs   | Получить все песни   |
| GET   | /songs/{song_id}    | Получить песню по id |
| GET   | /songs        |      Добав       |
| GET   | /songs/filter?genre=&liked=      | Фильтрация по жанру / понравившимся |
| POST  | /songs     | Добавить песню |
| DELETE | /songs/{song_id} | Удалить песню |
| PATCH | /songs/{song_id}/like | Отметить как любимую |
import os
import webbrowser
import urllib.parse
from typing import Dict, Any

class MusicTool:
    """
    Интеллектуальный музыкальный центр Джарвиса:
    - Поддержка Яндекс Музыки (через официальный yandex-music API или веб-плеер)
    - Поддержка YouTube Music (поиск, открытие треков и воспроизведение)
    """

    @staticmethod
    def play_yandex_music(query: str = "") -> str:
        """Поиск и запуск трека или плейлиста в Яндекс Музыке"""
        token = os.getenv("YANDEX_MUSIC_TOKEN", "")
        if token:
            try:
                from yandex_music import Client
                client = Client(token).init()
                search_res = client.search(query, type_='track')
                if search_res and search_res.tracks and search_res.tracks.results:
                    track = search_res.tracks.results[0]
                    artists = ", ".join([a.name for a in track.artists])
                    url = f"https://music.yandex.ru/album/{track.albums[0].id}/track/{track.id}"
                    webbrowser.open(url)
                    return f"Включаю в Яндекс Музыке: {track.title} — {artists}"
            except Exception as e:
                print(f"[Yandex Music Error]: {e}")

        # Если токен не задан или ошибка — открываем прямой поиск в веб-версии
        encoded = urllib.parse.quote(query)
        target_url = f"https://music.yandex.ru/search?text={encoded}" if query else "https://music.yandex.ru"
        webbrowser.open(target_url)
        return f"Открыл Яндекс Музыку по запросу: «{query or 'Моя волна'}», сэр."

    @staticmethod
    def play_youtube_music(query: str) -> str:
        """Поиск и воспроизведение в YouTube Music"""
        try:
            from ytmusicapi import YTMusic
            yt = YTMusic()
            results = yt.search(query, filter="songs")
            if results:
                best = results[0]
                video_id = best.get("videoId")
                title = best.get("title")
                artists = ", ".join([a.get("name", "") for a in best.get("artists", [])])
                if video_id:
                    url = f"https://music.youtube.com/watch?v={video_id}"
                    webbrowser.open(url)
                    return f"Включаю в YouTube Music: {title} ({artists})"
        except Exception:
            pass

        encoded = urllib.parse.quote(query)
        webbrowser.open(f"https://music.youtube.com/search?q={encoded}")
        return f"Открыл YouTube Music по запросу: «{query}», сэр."

    @staticmethod
    def play_track(service: str, query: str) -> str:
        srv = service.lower().strip()
        if "yandex" in srv or "яндекс" in srv:
            return MusicTool.play_yandex_music(query)
        elif "youtube" in srv or "ютуб" in srv:
            return MusicTool.play_youtube_music(query)
        else:
            # По умолчанию Яндекс или YouTube
            return MusicTool.play_yandex_music(query)

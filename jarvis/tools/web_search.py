import warnings
warnings.filterwarnings("ignore")
import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from typing import Optional, List, Dict

class WebSearchSkill:
    """
    Автономный интернет-агент для Джарвиса:
    - Поиск актуальной информации в реальном времени через DuckDuckGo (без API-ключей и лимитов).
    - Переход по ссылкам и очистка HTML-контента от рекламы, скриптов и мусора для извлечения чистой сути.
    - Поиск последних новостей, курсов валют, погоды, фактов.
    """

    @classmethod
    def search_web(cls, query: str, max_results: int = 5) -> str:
        """
        Ищет информацию в интернете по поисковому запросу.
        Возвращает заголовки, ссылки и сниппеты свежих результатов.
        """
        try:
            results = []
            with DDGS() as ddgs:
                search_gen = ddgs.text(query, region='ru-ru', safesearch='moderate', max_results=max_results)
                for r in search_gen:
                    results.append(r)

            if not results:
                # Попробуем без указания региона
                with DDGS() as ddgs:
                    for r in ddgs.text(query, max_results=max_results):
                        results.append(r)

            if not results:
                return f"По запросу «{query}» ничего не найдено в сети, сэр."

            formatted = [f"Результаты веб-поиска по запросу «{query}»:\n"]
            for i, item in enumerate(results, 1):
                title = item.get("title", "")
                link = item.get("href", "")
                snippet = item.get("body", "")
                formatted.append(f"{i}. {title}\n   Ссылка: {link}\n   Суть: {snippet}\n")

            return "\n".join(formatted)
        except Exception as e:
            return f"Ошибка при обращении к поисковому серверу: {str(e)[:150]}"

    @classmethod
    def search_news(cls, query: str = "последние новости", max_results: int = 5) -> str:
        """
        Ищет свежие горячие новости по теме в реальном времени.
        """
        try:
            results = []
            with DDGS() as ddgs:
                news_gen = ddgs.news(query, region='ru-ru', safesearch='moderate', max_results=max_results)
                for r in news_gen:
                    results.append(r)

            if not results:
                return cls.search_web(f"{query} новости сегодня", max_results=max_results)

            formatted = [f"Свежие новости по теме «{query}»:\n"]
            for i, item in enumerate(results, 1):
                title = item.get("title", "")
                source = item.get("source", "")
                date = item.get("date", "")
                snippet = item.get("body", "")
                formatted.append(f"{i}. [{source} | {date[:10]}] {title}\n   {snippet}\n")

            return "\n".join(formatted)
        except Exception as e:
            # Fallback на обычный поиск
            return cls.search_web(f"{query} новости", max_results=max_results)

    @classmethod
    def read_webpage(cls, url: str) -> str:
        """
        Открывает веб-страницу по URL, извлекает чистый текст статьи без рекламы и навигации.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            }
            with httpx.Client(timeout=10, follow_redirects=True, headers=headers) as client:
                resp = client.get(url)
                if resp.status_code != 200:
                    return f"Не удалось загрузить страницу (HTTP {resp.status_code}), сэр."

                html = resp.text

            soup = BeautifulSoup(html, "html.parser")

            # Удаляем скрипты, стили, шапки и подвалы с рекламой
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()

            # Получаем заголовок и основной текст
            title = soup.title.string.strip() if soup.title else "Без заголовка"
            paragraphs = []
            for p in soup.find_all(["p", "h1", "h2", "h3", "article"]):
                txt = p.get_text().strip()
                if len(txt) > 30 and txt not in paragraphs:
                    paragraphs.append(txt)

            article_text = "\n\n".join(paragraphs[:15])  # Берем главные 15 абзацев
            if not article_text:
                article_text = soup.get_text()[:2500]

            return f"Содержимое страницы «{title}» ({url}):\n\n{article_text[:3500]}"
        except Exception as e:
            return f"Ошибка при чтении веб-страницы: {str(e)[:150]}"

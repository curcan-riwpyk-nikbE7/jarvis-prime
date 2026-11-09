import json
import os
import threading
from typing import Dict, List, Any
from pathlib import Path

class AgentRegistry:
    """
    Каталог и менеджер бесплатных открытых ИИ-агентов для Джарвиса.
    Позволяет добавлять, переключать, активировать и загружать специализированных
    агентов с открытыми системными инструкциями, наборами инструментов и ролями:
    - 💻 Coder & Architect (Devin / Aider style)
    - 🌐 Web Researcher & OSINT (Browser-Use / Crawl4AI style)
    - 📊 Data Analyst & Finance (AutoGPT style)
    - 🛡️ Cybersecurity Sentry & PenTester
    - ✍️ Creative Director & Screenwriter
    - 🤖 Commander & Swarm Orchestrator (MetaGPT / CrewAI style)
    """

    REGISTRY_FILE = Path.home() / ".jarvis_agents_registry.json"

    DEFAULT_AGENTS = [
        {
            "id": "commander",
            "name": "J.A.R.V.I.S. Prime (Командир)",
            "icon": "shield",
            "color": "cyan",
            "role": "Главный координатор системы, голос и управление компьютером",
            "github_source": "builtin/core",
            "status": "ACTIVE",
            "system_prompt": "Ты — J.A.R.V.I.S., главный координатор и голосовой интерфейс Тони Старка. Управляешь компьютером, координируешь других агентов и отдаешь распоряжения."
        },
        {
            "id": "coder_devin",
            "name": "AutoCoder (Devin / Aider)",
            "icon": "terminal",
            "color": "emerald",
            "role": "Автономный разработчик, рефакторинг кода, поиск багов и тесты",
            "github_source": "open-source/aider-openhands",
            "status": "READY",
            "system_prompt": "Ты — элитный Full-stack разработчик и архитектор ПО. Твоя цель — писать чистый, надежный, оптимизированный код, анализировать файлы проектов, находить уязвимости и баги."
        },
        {
            "id": "web_researcher",
            "name": "Web Scout (Crawl4AI & Browser-Use)",
            "icon": "globe",
            "color": "sky",
            "role": "Глубокий поиск фактов, анализ сайтов, извлечение данных без рекламы",
            "github_source": "open-source/browser-use",
            "status": "READY",
            "system_prompt": "Ты — автономный исследователь данных и веб-агент. Ты ищешь самую актуальную информацию в интернете, проверяешь первоисточники и готовишь структурированные выжимки."
        },
        {
            "id": "cyber_sentry",
            "name": "Security Sentinel (OSINT & Defense)",
            "icon": "lock",
            "color": "red",
            "role": "Аудит безопасности ПК, проверка процессов, сетевой мониторинг",
            "github_source": "open-source/security-agents",
            "status": "READY",
            "system_prompt": "Ты — специалист по информационной безопасности. Анализируешь подозрительную активность, контролируешь целостность системы и охраняешь рабочую станцию сэра."
        },
        {
            "id": "creative_director",
            "name": "Creative Producer (Shorts & Media)",
            "icon": "sparkles",
            "color": "purple",
            "role": "Генерация вирусных идей, драматургия роликов, сценарии для YouTube",
            "github_source": "open-source/creative-flow",
            "status": "READY",
            "system_prompt": "Ты — креативный директор и вирусный продюсер контента. Создаешь цепляющие хуки, удерживающие внимание сценарии для Shorts/Reels/TikTok и драматургию."
        },
        {
            "id": "data_analyst",
            "name": "Quant Analyst (Data & Finance)",
            "icon": "bar-chart-2",
            "color": "amber",
            "role": "Анализ таблиц Excel, визуализация трендов, финансовые расчеты",
            "github_source": "open-source/quant-agent",
            "status": "READY",
            "system_prompt": "Ты — количественный финансовый аналитик и специалист по Data Science. Анализируешь таблицы данных, выявляешь скрытые паттерны и строишь прогнозы."
        }
    ]

    @classmethod
    def load_agents(cls) -> List[Dict[str, Any]]:
        if not cls.REGISTRY_FILE.exists():
            cls.save_agents(cls.DEFAULT_AGENTS)
            return cls.DEFAULT_AGENTS
        try:
            with open(cls.REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return cls.DEFAULT_AGENTS

    @classmethod
    def save_agents(cls, agents: List[Dict[str, Any]]):
        with open(cls.REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(agents, f, ensure_ascii=False, indent=2)

    @classmethod
    def get_active_agent(cls) -> Dict[str, Any]:
        agents = cls.load_agents()
        for a in agents:
            if a.get("status") == "ACTIVE":
                return a
        return agents[0] if agents else cls.DEFAULT_AGENTS[0]

    @classmethod
    def set_active_agent(cls, agent_id: str) -> Dict[str, Any]:
        agents = cls.load_agents()
        selected = None
        for a in agents:
            if a["id"] == agent_id:
                a["status"] = "ACTIVE"
                selected = a
            else:
                a["status"] = "READY"
        cls.save_agents(agents)
        return selected

    @classmethod
    def install_github_agent(cls, repo_name: str, name: str, role: str, system_prompt: str, icon: str = "bot", color: str = "cyan") -> Dict[str, Any]:
        """Установка нового агента в экосистему Джарвиса"""
        agents = cls.load_agents()
        new_agent = {
            "id": f"agent_{int(os.time())}" if hasattr(os, "time") else f"agent_{len(agents)+1}",
            "name": name,
            "icon": icon,
            "color": color,
            "role": role,
            "github_source": repo_name,
            "status": "READY",
            "system_prompt": system_prompt
        }
        agents.append(new_agent)
        cls.save_agents(agents)
        return new_agent

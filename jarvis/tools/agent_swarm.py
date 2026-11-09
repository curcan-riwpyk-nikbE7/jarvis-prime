from jarvis.agents.registry import AgentRegistry

class AgentSwarmSkill:
    """
    Инструмент вызова и оркестрации агентов.
    Позволяет Джарвису привлекать специализированных бесплатных агентов (Кодер, Веб-исследователь,
    Аналитик данных, Охранник) под конкретные запросы сэра.
    """

    @classmethod
    def list_agents(cls) -> list:
        return AgentRegistry.load_agents()

    @classmethod
    def switch_agent(cls, agent_id: str) -> dict:
        agent = AgentRegistry.set_active_agent(agent_id)
        if agent:
            return {
                "status": "success",
                "message": f"Специализированный агент «{agent['name']}» активирован, сэр. Роль: {agent['role']}.",
                "agent": agent
            }
        return {"status": "error", "message": f"Агент {agent_id} не найден в реестре."}

    @classmethod
    def consult_agent(cls, agent_id: str, prompt: str) -> dict:
        """
        Делегирует сложную задачу конкретному агенту (например, код — AutoCoder'у, новости — Web Scout'у)
        """
        agents = AgentRegistry.load_agents()
        target = next((a for a in agents if a["id"] == agent_id), None)
        if not target:
            target = AgentRegistry.get_active_agent()

        return {
            "status": "delegated",
            "agent_name": target["name"],
            "role": target["role"],
            "instruction": f"Используй профиль «{target['name']}» ({target['system_prompt']}) для исчерпывающего ответа на запрос: {prompt}"
        }

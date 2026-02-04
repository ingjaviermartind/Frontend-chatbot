from Models.Worker import Worker
from Models.Analiyst import AnalystWorker
from Models.Technician import TechnicianWorker

class WorkerFactory:
    @staticmethod
    def create(role: str, data: dict) -> Worker:
        if role == "Analista":
            return AnalystWorker(data)
        if role == "Técnico":
            return TechnicianWorker(data)
        raise ValueError(f"Rol desconocido: {role}")
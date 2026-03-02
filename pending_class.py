from dataclasses import dataclass, field
from time import monotonic

@dataclass
class PendingClassUpdate:
    class_update: dict | None = None
    aura_p: dict | None = None
    s_act: dict | None = None
    last_update: float = field(default_factory=monotonic)

    def ready(self) -> bool:
        return self.class_update is not None and self.aura_p is not None and self.s_act is not None
        

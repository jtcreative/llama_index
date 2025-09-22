from llama_index.core.llms import MessageRole, ChatMessage
import json
import redis

class RedisChatMemory:
    """Redis-backed chat memory that is compatible with LlamaIndex and with your manual append(role, msg)."""

    class _ShimChatMessage:
        """A tiny shim so returned items look like ChatMessage (have .role and .content)."""
        def __init__(self, role, content):
            self.role = role
            self.content = content
        def __repr__(self):
            return f"<ShimChatMessage role={self.role!r} content={self.content!r}>"

    def __init__(self, redis_client: redis.Redis, key: str, ttl: int = 1800):
        self.r = redis_client
        self.key = key
        self.ttl = ttl

    # This is the method LlamaIndex may call: .put(ChatMessage(...))
    def put(self, message):
        """
        Accepts:
          - an object with .role and .content attributes (ChatMessage-like),
          - or a dict with {"role":..., "content":...},
          - or a plain string (treated as assistant content).
        """
        # extract role/content from possible types
        role = None
        content = None

        # Case 1: ChatMessage-like object (has .role and .content)
        if hasattr(message, "content") and hasattr(message, "role"):
            # handle enums like MessageRole: try .value fallback
            role_obj = message.role
            role = getattr(role_obj, "value", role_obj if role_obj is not None else "unknown")
            content = message.content

        # Case 2: dict
        elif isinstance(message, dict):
            role = message.get("role", "unknown")
            content = message.get("content", message.get("message", ""))

        # Case 3: plain string
        else:
            role = "assistant"
            content = str(message)

        entry = json.dumps({"role": str(role), "content": str(content)})
        self.r.rpush(self.key, entry)
        self.r.expire(self.key, self.ttl)

    # This is your manual convenience method — keep calling this in your code.
    def append(self, role: str, message: str):
        """
        Keep your existing append(role, message) calls.
        This wraps into put by passing a dict (put is the canonical entry point).
        """
        self.put({"role": role, "content": message})

    def get(self, input=None, **kwargs):
        data = self.r.lrange(self.key, 0, -1)
        out = []
        for raw in data:
            try:
                obj = json.loads(raw)
                role_str = obj.get("role", "assistant")
                content = obj.get("content", "")
                # reconstruct as real ChatMessage
                role_enum = (
                    MessageRole(role_str)
                    if role_str in [r.value for r in MessageRole]
                    else MessageRole.ASSISTANT
                )
                out.append(ChatMessage(role=role_enum, content=content))
            except Exception as e:
                # fallback if something goes wrong
                out.append(ChatMessage(role=MessageRole.ASSISTANT, content=str(raw)))
        return out

    def reset(self):
        self.r.delete(self.key)
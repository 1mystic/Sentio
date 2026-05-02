import os
from supabase import create_client, Client

_client: Client | None = None


def get_supabase() -> Client:
    """Return a singleton Supabase client.

    Uses the service-role key so that server-side operations can bypass
    Row Level Security where needed.  Never expose this key to the frontend.
    """
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in the environment"
            )
        _client = create_client(url, key)
    return _client

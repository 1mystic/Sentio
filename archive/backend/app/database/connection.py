from supabase import create_client, Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Global Supabase client
supabase_client: Client = None

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    global supabase_client
    
    if supabase_client is None:
        try:
            supabase_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
            logger.info("✅ Supabase client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    return supabase_client

async def init_db():
    """Initialize database connection and run any startup tasks"""
    try:
        client = get_supabase_client()
        
        # Test connection
        response = client.table("users").select("count", count="exact").limit(1).execute()
        logger.info("✅ Database connection successful")
        
        # Run any database migrations or setup here
        await create_tables_if_not_exist()
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def create_tables_if_not_exist():
    """Create tables if they don't exist"""
    client = get_supabase_client()
    
    # This would typically be handled by Supabase migrations
    # For now, we'll assume tables are created via Supabase dashboard or SQL migrations
    logger.info("📝 Table creation handled by Supabase migrations")

def get_db():
    """Database dependency for FastAPI"""
    return get_supabase_client()

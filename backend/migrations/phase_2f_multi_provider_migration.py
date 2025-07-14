"""
Database Migration Script for Phase 2f: Multi-Provider AI Architecture
LearnOnTheGo - Week 1 Implementation

This migration adds new tables and columns for multi-provider AI support.
"""

import asyncio
import logging
from sqlalchemy import text
from models.database import async_engine, create_tables_async
from models.lecture_orm import (
    UserAIPreferences, AIProviderConfig,
    LLMProvider, TTSProvider, QualityTier
)

logger = logging.getLogger(__name__)


async def run_migration():
    """Execute the database migration for multi-provider AI"""
    
    logger.info("Starting Phase 2f database migration...")
    
    try:
        # Create new tables
        await create_tables_async()
        logger.info("✅ Created new database tables")
        
        # Add new columns to existing tables
        await add_lecture_columns()
        logger.info("✅ Added new columns to lectures table")
        
        # Add new columns to user_api_keys table
        await add_api_key_columns()
        logger.info("✅ Added new columns to user_api_keys table")
        
        # Insert default AI provider configurations
        await insert_default_provider_configs()
        logger.info("✅ Inserted default AI provider configurations")
        
        # Create default AI preferences for existing users
        await create_default_user_preferences()
        logger.info("✅ Created default AI preferences for existing users")
        
        logger.info("🎉 Phase 2f database migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise


async def add_lecture_columns():
    """Add new columns to the lectures table"""
    
    async with async_engine.begin() as conn:
        # Check if columns already exist to avoid errors
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'lectures' AND table_schema = 'public'
        """))
        existing_columns = [row[0] for row in result.fetchall()]
        
        # Add new columns if they don't exist
        new_columns = [
            ("llm_provider_used", "VARCHAR(50)"),
            ("llm_model_name", "VARCHAR(100)"),
            ("tts_provider_used", "VARCHAR(50)"),
            ("quality_tier_used", "VARCHAR(20)"),
            ("llm_cost_usd", "DECIMAL(8,4)"),
            ("tts_cost_usd", "DECIMAL(8,4)"),
            ("total_ai_cost_usd", "DECIMAL(8,4)"),
            ("cost_optimization_used", "BOOLEAN DEFAULT FALSE"),
            ("llm_generation_time_ms", "INTEGER"),
            ("tts_generation_time_ms", "INTEGER"),
            ("total_generation_time_ms", "INTEGER"),
            ("cache_hit", "BOOLEAN DEFAULT FALSE")
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                await conn.execute(text(f"""
                    ALTER TABLE lectures 
                    ADD COLUMN {column_name} {column_type}
                """))
                logger.info(f"Added column {column_name} to lectures table")


async def add_api_key_columns():
    """Add new columns to the user_api_keys table"""
    
    async with async_engine.begin() as conn:
        # Check if columns already exist
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user_api_keys' AND table_schema = 'public'
        """))
        existing_columns = [row[0] for row in result.fetchall()]
        
        # Add new columns if they don't exist
        new_columns = [
            ("provider_type", "VARCHAR(20) DEFAULT 'llm'"),
            ("provider_tier", "VARCHAR(20)"),
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("free_tier_remaining", "INTEGER"),
            ("free_tier_reset_date", "TIMESTAMP WITH TIME ZONE"),
            ("monthly_usage_limit", "INTEGER"),
            ("monthly_cost_usd", "DECIMAL(8,4) DEFAULT 0.0"),
            ("cost_alert_threshold", "DECIMAL(8,4)"),
            ("avg_response_time_ms", "INTEGER"),
            ("success_rate_percent", "FLOAT"),
            ("total_requests", "INTEGER DEFAULT 0"),
            ("failed_requests", "INTEGER DEFAULT 0")
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                await conn.execute(text(f"""
                    ALTER TABLE user_api_keys 
                    ADD COLUMN {column_name} {column_type}
                """))
                logger.info(f"Added column {column_name} to user_api_keys table")


async def insert_default_provider_configs():
    """Insert default AI provider configurations"""
    
    async with async_engine.begin() as conn:
        # Check if configs already exist
        result = await conn.execute(text("""
            SELECT COUNT(*) FROM ai_provider_configs
        """))
        config_count = result.scalar()
        
        if config_count > 0:
            logger.info("AI provider configs already exist, skipping insertion")
            return
        
        # TTS Provider configurations
        tts_configs = [
            {
                "provider_name": "google_standard",
                "provider_type": "tts",
                "display_name": "Google Cloud Text-to-Speech (Standard)",
                "description": "High-quality TTS with 4M free characters per month",
                "cost_per_1k_chars": 0.004,
                "free_tier_limit": 4000000,
                "free_tier_reset_period": "monthly",
                "quality_score": 6.5,
                "reliability_score": 9.5,
                "speed_score": 8.5,
                "is_free_tier_available": True,
                "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "hi", "ar"],
                "requests_per_minute": 300,
                "concurrent_requests": 10
            },
            {
                "provider_name": "google_neural",
                "provider_type": "tts",
                "display_name": "Google Cloud Text-to-Speech (Neural2)",
                "description": "Premium neural TTS with 1M free characters per month",
                "cost_per_1k_chars": 0.016,
                "free_tier_limit": 1000000,
                "free_tier_reset_period": "monthly",
                "quality_score": 8.0,
                "reliability_score": 9.5,
                "speed_score": 8.0,
                "is_free_tier_available": True,
                "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                "requests_per_minute": 300,
                "concurrent_requests": 8
            },
            {
                "provider_name": "openai_tts",
                "provider_type": "tts",
                "display_name": "OpenAI Text-to-Speech",
                "description": "High-quality TTS with 6 voice options",
                "cost_per_1k_chars": 0.015,
                "quality_score": 8.5,
                "reliability_score": 9.0,
                "speed_score": 7.5,
                "is_free_tier_available": False,
                "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                "requests_per_minute": 50,
                "concurrent_requests": 5
            },
            {
                "provider_name": "elevenlabs",
                "provider_type": "tts",
                "display_name": "ElevenLabs",
                "description": "Premium quality TTS with voice cloning capabilities",
                "cost_per_1k_chars": 0.165,
                "free_tier_limit": 10000,
                "free_tier_reset_period": "monthly",
                "quality_score": 9.5,
                "reliability_score": 8.5,
                "speed_score": 6.5,
                "is_free_tier_available": True,
                "supported_languages": ["en", "es", "fr", "de", "it", "pt", "hi"],
                "requests_per_minute": 20,
                "concurrent_requests": 3
            },
            {
                "provider_name": "unreal_speech",
                "provider_type": "tts",
                "display_name": "Unreal Speech",
                "description": "Cost-effective TTS for English content",
                "cost_per_1k_chars": 0.002,
                "quality_score": 7.0,
                "reliability_score": 8.0,
                "speed_score": 9.0,
                "is_free_tier_available": False,
                "supported_languages": ["en"],
                "requests_per_minute": 100,
                "concurrent_requests": 5
            }
        ]
        
        # LLM Provider configurations
        llm_configs = [
            {
                "provider_name": "openrouter",
                "provider_type": "llm",
                "display_name": "OpenRouter",
                "description": "Multi-model hub with access to latest LLMs",
                "cost_per_1k_tokens": 0.02,
                "quality_score": 8.5,
                "reliability_score": 9.0,
                "speed_score": 8.0,
                "is_free_tier_available": False,
                "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                "requests_per_minute": 60,
                "concurrent_requests": 5
            },
            {
                "provider_name": "openai_direct",
                "provider_type": "llm",
                "display_name": "OpenAI GPT",
                "description": "Direct access to OpenAI's GPT models",
                "cost_per_1k_tokens": 0.03,
                "quality_score": 9.5,
                "reliability_score": 9.5,
                "speed_score": 8.5,
                "is_free_tier_available": False,
                "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                "requests_per_minute": 60,
                "concurrent_requests": 3
            },
            {
                "provider_name": "anthropic_direct",
                "provider_type": "llm",
                "display_name": "Anthropic Claude",
                "description": "Direct access to Claude models",
                "cost_per_1k_tokens": 0.025,
                "quality_score": 9.0,
                "reliability_score": 9.0,
                "speed_score": 7.5,
                "is_free_tier_available": False,
                "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                "requests_per_minute": 50,
                "concurrent_requests": 3
            }
        ]
        
        # Insert all configurations
        all_configs = tts_configs + llm_configs
        
        for config in all_configs:
            await conn.execute(text("""
                INSERT INTO ai_provider_configs (
                    provider_name, provider_type, display_name, description,
                    cost_per_1k_tokens, cost_per_1k_chars, free_tier_limit, 
                    free_tier_reset_period, quality_score, reliability_score, 
                    speed_score, is_free_tier_available, supported_languages,
                    requests_per_minute, concurrent_requests, is_enabled
                ) VALUES (
                    :provider_name, :provider_type, :display_name, :description,
                    :cost_per_1k_tokens, :cost_per_1k_chars, :free_tier_limit,
                    :free_tier_reset_period, :quality_score, :reliability_score,
                    :speed_score, :is_free_tier_available, :supported_languages,
                    :requests_per_minute, :concurrent_requests, TRUE
                )
            """), {
                **config,
                "cost_per_1k_tokens": config.get("cost_per_1k_tokens"),
                "cost_per_1k_chars": config.get("cost_per_1k_chars"),
                "supported_languages": str(config["supported_languages"])  # Convert to string for storage
            })
        
        logger.info(f"Inserted {len(all_configs)} AI provider configurations")


async def create_default_user_preferences():
    """Create default AI preferences for existing users"""
    
    async with async_engine.begin() as conn:
        # Get all users who don't have AI preferences yet
        result = await conn.execute(text("""
            SELECT u.id 
            FROM users u 
            LEFT JOIN user_ai_preferences uap ON u.id = uap.user_id 
            WHERE uap.user_id IS NULL
        """))
        
        user_ids = [row[0] for row in result.fetchall()]
        
        if not user_ids:
            logger.info("No users need default AI preferences")
            return
        
        # Create default preferences for each user
        for user_id in user_ids:
            await conn.execute(text("""
                INSERT INTO user_ai_preferences (
                    user_id, default_quality_tier, enable_cost_optimization,
                    enable_smart_routing, enable_caching, llm_creativity_level,
                    llm_max_tokens, preferred_language, voice_speed,
                    voice_stability, voice_clarity, cost_alert_percentage,
                    prefer_free_tier, max_generation_time_seconds,
                    require_high_success_rate, content_style,
                    include_examples, include_summary, preferred_content_length
                ) VALUES (
                    :user_id, 'standard', TRUE, TRUE, TRUE, 0.7, 4000, 'en', 1.0,
                    0.75, 0.75, 80, TRUE, 120, TRUE, 'educational',
                    TRUE, TRUE, 'standard'
                )
            """), {"user_id": user_id})
        
        logger.info(f"Created default AI preferences for {len(user_ids)} users")


async def verify_migration():
    """Verify the migration was successful"""
    
    async with async_engine.begin() as conn:
        # Check new tables exist
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('user_ai_preferences', 'ai_provider_configs')
        """))
        
        tables = [row[0] for row in result.fetchall()]
        
        if len(tables) == 2:
            logger.info("✅ New tables created successfully")
        else:
            logger.error(f"❌ Missing tables: {set(['user_ai_preferences', 'ai_provider_configs']) - set(tables)}")
        
        # Check provider configs
        result = await conn.execute(text("SELECT COUNT(*) FROM ai_provider_configs"))
        config_count = result.scalar()
        logger.info(f"✅ AI provider configs: {config_count}")
        
        # Check user preferences
        result = await conn.execute(text("SELECT COUNT(*) FROM user_ai_preferences"))
        pref_count = result.scalar()
        logger.info(f"✅ User AI preferences: {pref_count}")


if __name__ == "__main__":
    async def main():
        await run_migration()
        await verify_migration()
    
    asyncio.run(main())

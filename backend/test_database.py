#!/usr/bin/env python3
"""
Simple database connectivity test for Phase 2a validation.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from models.database import get_async_db, check_database_health, get_database_info, create_tables_async
from models.user_orm import User


async def test_database_setup():
    """Test database initialization and basic operations."""
    print("🔄 Testing database setup...")
    
    try:
        # Test database connection
        print("1. Testing database connection...")
        connection_result = await check_database_health()
        print(f"   ✅ Database connection: {'Healthy' if connection_result else 'Failed'}")
        
        if not connection_result:
            print("   ❌ Cannot proceed without database connection")
            return False
        
        # Get database info
        print("2. Getting database information...")
        db_info = get_database_info()
        print(f"   📊 Database URL: {db_info['database_url']}")
        print(f"   🔧 Debug mode: {db_info['debug_mode']}")
        
        # Initialize database tables
        print("3. Initializing database tables...")
        await create_tables_async()
        print("   ✅ Database tables created successfully")
        
        # Test basic user operations
        print("4. Testing user CRUD operations...")
        async for session in get_async_db():
            try:
                # Create test user
                import random
                random_id = random.randint(1000, 9999)
                test_email = f"test{random_id}@example.com"
                
                test_user = User.create_from_registration(
                    email=test_email,
                    password_hash="$2b$12$dummy_hash",
                    full_name="Test User"
                )
                session.add(test_user)
                await session.commit()
                await session.refresh(test_user)
                print(f"   ✅ Created user: {test_user.full_name} (ID: {test_user.id})")
                
                # Query user
                from sqlalchemy import select
                result = await session.execute(select(User).where(User.email == test_email))
                found_user = result.scalar_one_or_none()
                
                if found_user:
                    print(f"   ✅ Found user: {found_user.full_name} with tier: {found_user.subscription_tier.value}")
                else:
                    print("   ❌ User not found after creation")
                    return False
                
                # Clean up test user
                await session.delete(found_user)
                await session.commit()
                print("   ✅ Test user cleaned up")
                break  # Exit the async generator after first session
                
            except Exception as session_error:
                print(f"   ❌ Session error: {session_error}")
                raise
        
        print("\n🎉 Database setup test completed successfully!")
        print("📊 Summary:")
        print("   - Database connection: Working")
        print("   - Table creation: Working") 
        print("   - User CRUD operations: Working")
        print("   - SQLAlchemy ORM: Working")
        print("   - Async sessions: Working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test runner."""
    print("=" * 60)
    print("Phase 2a Database Foundation Test")
    print("=" * 60)
    
    success = await test_database_setup()
    
    if success:
        print("\n✅ Phase 2a database foundation is ready!")
        print("Next: Test user API endpoints")
        sys.exit(0)
    else:
        print("\n❌ Phase 2a database foundation needs attention")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

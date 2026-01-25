import pytest
from datetime import datetime, timedelta
from social_bot.models import Post

def test_post_serialization():
    """Verifica que el modelo Post se cree correctamente."""
    data = {
        "id": "test-1",
        "text": "Hello test",
        "channels": ["test"],
        "scheduled_at": "2026-01-01T10:00:00",
        "published": False
    }
    post = Post(**data)
    assert post.id == "test-1"
    assert post.published is False

def test_should_publish_logic():
    """Verifica la lógica de tiempo del bot."""
    now = datetime.now()
    
    # Post futuro
    future_post = Post(
        id="f", text="f", 
        scheduled_at=now + timedelta(hours=1)
    )
    assert future_post.should_publish(now) is False
    
    # Post pasado
    past_post = Post(
        id="p", text="p", 
        scheduled_at=now - timedelta(hours=1)
    )
    assert past_post.should_publish(now) is True
    
    # Post ya publicado
    already_published = Post(
        id="a", text="a", 
        scheduled_at=now - timedelta(hours=1),
        published=True
    )
    assert already_published.should_publish(now) is False

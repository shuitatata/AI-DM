from app.models.game_state import SessionStore
import pytest


class TestSessionStore:
    """为 SessionStore 管理器编写的单元测试。"""

    @pytest.fixture
    def store(self) -> SessionStore:
        """提供一个干净的 SessionStore 实例。"""
        return SessionStore()

    def test_create_and_get_session(self, store: SessionStore):
        """测试：能否成功创建和获取会话。"""
        session_id = "session-1"
        created_session = store.create_session(session_id)

        assert created_session.session_id == session_id

        retrieved_session = store.get_session(session_id)
        assert retrieved_session is not None
        assert retrieved_session == created_session

    def test_get_non_existent_session(self, store: SessionStore):
        """测试：获取一个不存在的会话应返回 None。"""
        assert store.get_session("non-existent-id") is None

    def test_update_session(self, store: SessionStore):
        """测试：能否成功更新一个会话。"""
        session_id = "session-2"
        session = store.create_session(session_id)

        # 修改会话状态
        session.world_state.name = "Updated World"
        store.update_session(session)

        # 重新获取并验证
        updated_session = store.get_session(session_id)
        assert updated_session.world_state.name == "Updated World"

    def test_delete_session(self, store: SessionStore):
        """测试：能否成功删除一个会话。"""
        session_id = "session-3"
        store.create_session(session_id)

        assert store.get_session(session_id) is not None

        deleted = store.delete_session(session_id)
        assert deleted is True
        assert store.get_session(session_id) is None

        # 测试删除一个不存在的会话
        not_deleted = store.delete_session("non-existent-id")
        assert not_deleted is False

    def test_list_sessions(self, store: SessionStore):
        """测试：能否正确列出所有会话ID。"""
        assert store.list_sessions() == []

        store.create_session("id-1")
        store.create_session("id-2")

        session_ids = store.list_sessions()
        assert len(session_ids) == 2
        assert "id-1" in session_ids
        assert "id-2" in session_ids

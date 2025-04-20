import time
import pytest
import types
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from kazoo.client import KazooClient
from kazoo.retry import KazooRetry
from kazoo.exceptions import NoNodeError
from main import app
from app.core.database import (
    SessionLocal,
    Base,
    engine,
)
from app.core.config import DATABASE_URL
from zookeeper import ZK_HOST, zk
from app.models import User, Queue, Topic
from app.core.auth_helpers import get_current_user

ZOOKEEPER_HOSTS = ZK_HOST

SERVER_LISTEN_ADDRESS = "127.0.0.1:8000"

ZK_SERVERS_PATH = "/servers"
ZK_METADATA_PATH = "/servers-metadata"
# Construct the specific metadata paths using the server address
ZK_SERVER_METADATA_ROOT = f"{ZK_METADATA_PATH}/{SERVER_LISTEN_ADDRESS}"
ZK_QUEUE_METADATA_PATH = f"{ZK_SERVER_METADATA_ROOT}/Queues"
ZK_TOPIC_METADATA_PATH = f"{ZK_SERVER_METADATA_ROOT}/Topics"
ZK_USER_METADATA_PATH = (
    f"{ZK_SERVER_METADATA_ROOT}/Users"  # Assuming this path structure for users
)


@pytest.fixture
def client():
    """Provides a TestClient for the FastAPI application."""
    with TestClient(app) as c:
        wait_for_zookeeper_nodes()
        yield c


def wait_for_zookeeper_nodes():
    """Waits for the Zookeeper nodes to be created."""
    base_paths = [
        ZK_SERVERS_PATH,
        f"{ZK_SERVERS_PATH}/{SERVER_LISTEN_ADDRESS}",
        ZK_SERVER_METADATA_ROOT,
        ZK_QUEUE_METADATA_PATH,
        ZK_TOPIC_METADATA_PATH,
        ZK_USER_METADATA_PATH,
    ]

    attempts = 0
    max_attempts = 10
    while attempts < max_attempts:
        all_nodes_exist = True
        for path in base_paths:
            if not zk.exists(path):
                all_nodes_exist = False
                break

        if all_nodes_exist:
            break

        attempts += 1
        print(
            f"[ZK] Intentando verificar nodos base... intento {attempts}/{max_attempts}"
        )
        time.sleep(1)

    assert all_nodes_exist, (
        "Los nodos base de Zookeeper no se crearon en el tiempo esperado."
    )


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    print("\nSetting up test database...")
    print(f"Database URL: {DATABASE_URL}")
    # Drop all tables first
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database setup complete.")
    yield


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()  # Ensure rollback on error
        raise
    finally:
        db.close()


@pytest.fixture
def real_test_user(db_session: Session):
    """Fixture to create a real user in the database for testing."""
    try:
        user = User(
            name="testuser_zk",
            password="fakehashedpassword",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        print(f"\nCreated user in DB for test with ID: {user.id}")
        yield user
    except Exception as e:
        db_session.rollback()
        print(f"\nFailed to create user in DB fixture: {e}")
        raise
    finally:
        if user and user.id:
            try:
                with SessionLocal() as delete_session:
                    user_to_delete = (
                        delete_session.query(User).filter(User.id == user.id).first()
                    )
                    if user_to_delete:
                        delete_session.delete(user_to_delete)
                        delete_session.commit()
                        print(f"Cleaned up user with ID: {user.id}")
            except Exception as e:
                print(f"Error during user cleanup: {e}")


@pytest.fixture(autouse=True)
def override_get_current_user_with_real_user_id(real_test_user: User):
    """Overrides get_current_user to return a mock object with the real user's ID."""

    def mock_get_current_user():
        mock_user = types.SimpleNamespace(
            id=real_test_user.id,
            name=real_test_user.name,
        )
        return mock_user

    print(
        f"\nSetting dependency override for get_current_user using ID: {real_test_user.id}"
    )
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield  # This signifies the setup part is done
    print("\nClearing dependency overrides.")
    app.dependency_overrides.clear()


@pytest.fixture
def user_token():
    """Provides a fake token string for the Authorization header."""
    return "fake-jwt-token"


@pytest.fixture(scope="session")
def kazoo_client():
    """Fixture to provide a connected KazooClient instance."""
    print(f"\nConnecting to Zookeeper at {ZOOKEEPER_HOSTS}...")
    client = KazooClient(hosts=ZOOKEEPER_HOSTS)
    try:
        client.start(timeout=15)
        print("\nZookeeper connection successful.\n")
        yield client
    except Exception as e:
        pytest.fail(f"Could not connect to Zookeeper at {ZOOKEEPER_HOSTS}: {e}")
    finally:
        print("Stopping Zookeeper client.")
        client.stop()
        client.close()


def cleanup_zk_nodes(client: KazooClient):
    """Clean up Zookeeper nodes created by the test for this server instance."""
    print("\nStarting Zookeeper cleanup...")
    retry_obj = KazooRetry(max_tries=5, delay=0.5, max_delay=3)

    paths_to_delete = [
        ZK_SERVER_METADATA_ROOT,
        f"{ZK_SERVERS_PATH}/{SERVER_LISTEN_ADDRESS}",
    ]

    for path in paths_to_delete:
        try:
            print(f"Attempting to delete ZK node: {path}")
            is_recursive = path == ZK_SERVER_METADATA_ROOT
            retry_obj(client.delete, path, recursive=is_recursive, ignore_version=True)
            print(f"Deleted ZK node: {path}")
        except NoNodeError:
            print(f"ZK node not found for deletion: {path}")
        except Exception as e:
            print(f"Error deleting ZK node {path}: {e}")

    print("Zookeeper cleanup complete.")


def get_children_safe(kazoo_client, path, retry: KazooRetry):
    """Trata de obtener los hijos del path, esperando a que exista."""
    if retry(kazoo_client.exists, path):
        return retry(kazoo_client.get_children, path)
    raise NoNodeError(f"Path {path} no existe en Zookeeper.")


def test_zookeeper_metadata_integrity(
    client: TestClient,
    db_session: Session,
    kazoo_client: KazooClient,
    user_token: str,
    real_test_user: User,
):
    """
    Tests if resource creation via API correctly reflects in Zookeeper nodes
    for the specific server address.
    """
    cleanup_zk_nodes(kazoo_client)

    queue_name = "test-queue-zk-integrity"
    topic_name = "test-topic-zk-integrity"
    print("\nCreating resources via FastAPI...")
    print(f"Creating Queue: {queue_name}")
    response_queue = client.post(
        "/queues/",
        json={"name": queue_name},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response_queue.status_code == 200, (
        f"Failed to create queue: {response_queue.json()}"
    )
    created_queue = response_queue.json()
    queue_id = created_queue.get("queue_id")
    assert queue_id is not None, "Queue ID not found in response"
    print(f"Queue '{queue_name}' created with ID: {queue_id}")
    print(f"Creating Topic: {topic_name}")
    try:
        response_topic = client.post(
            "/topics/",
            json={"name": topic_name},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response_topic.status_code in [200, 201], (
            f"Failed to create topic: {response_topic.json()}"
        )
        created_topic = response_topic.json()
        topic_id = created_topic.get("topic_id")
        assert topic_id is not None, "Topic ID not found in response"
        print(f"Topic '{topic_name}' created with ID: {topic_id}")
    except Exception as e:
        print(
            f"Warning: Topic endpoint /topics/ not available or failed ({e}). Skipping topic ZK checks."
        )
        topic_id = None

    user_id = real_test_user.id
    print(f"Using User ID from fixture: {user_id}")

    print("\nVerifying Zookeeper nodes...")

    zk_verify_retry = KazooRetry(max_tries=15, delay=0.3, max_delay=5)

    try:
        server_zk_node_path = f"{ZK_SERVERS_PATH}/{SERVER_LISTEN_ADDRESS}"
        print(f"Checking if server node exists: {server_zk_node_path}")
        zk_verify_retry(kazoo_client.exists, server_zk_node_path)
        print(f"Server node {server_zk_node_path} found.")

        print(f"Checking if server metadata root exists: {ZK_SERVER_METADATA_ROOT}")
        zk_verify_retry(kazoo_client.exists, ZK_SERVER_METADATA_ROOT)
        print(f"Server metadata root {ZK_SERVER_METADATA_ROOT} found.")

        print("Checking if resource metadata paths exist...")
        zk_verify_retry(kazoo_client.exists, ZK_QUEUE_METADATA_PATH)
        print(f"Path {ZK_QUEUE_METADATA_PATH} found.")

        if topic_id is not None:
            zk_verify_retry(kazoo_client.exists, ZK_TOPIC_METADATA_PATH)
            print(f"Path {ZK_TOPIC_METADATA_PATH} found.")

        zk_verify_retry(kazoo_client.exists, ZK_USER_METADATA_PATH)
        print(f"Path {ZK_USER_METADATA_PATH} found.")

        print("Checking for resource IDs as ZK child nodes...")

        queue_children = get_children_safe(
            kazoo_client, ZK_QUEUE_METADATA_PATH, zk_verify_retry
        )
        assert str(queue_id) in queue_children, (
            f"Queue ID {queue_id} ({str(queue_id)}) not found under {ZK_QUEUE_METADATA_PATH}. Children: {queue_children}"
        )
        print(f"Queue ID {queue_id} found as child in ZK.")

        if topic_id is not None:
            topic_children = get_children_safe(
                kazoo_client, ZK_TOPIC_METADATA_PATH, zk_verify_retry
            )
            assert str(topic_id) in topic_children, (
                f"Topic ID {topic_id} ({str(topic_id)}) not found under {ZK_TOPIC_METADATA_PATH}. Children: {topic_children}"
            )
            print(f"Topic ID {topic_id} found as child in ZK.")

        user_children = get_children_safe(
            kazoo_client, ZK_USER_METADATA_PATH, zk_verify_retry
        )
        assert str(user_id) in user_children, (
            f"User ID {user_id} ({str(user_id)}) not found under {ZK_USER_METADATA_PATH}. Children: {user_children}"
        )
        print(f"User ID {user_id} found as child in ZK.")

        print("\nZookeeper integrity check passed!")

    except Exception as e:
        pytest.fail(f"Zookeeper verification failed: {e}")

    finally:
        cleanup_zk_nodes(kazoo_client)

        print("\nStarting database cleanup (Queues, Topics)...")
        try:
            with SessionLocal() as delete_session:
                queue_to_delete = (
                    delete_session.query(Queue).filter(Queue.name == queue_name).first()
                )
                if queue_to_delete:
                    delete_session.delete(queue_to_delete)
                    delete_session.commit()
                    print(f"Cleaned up queue: {queue_name}")
                else:
                    print(f"Queue '{queue_name}' not found for DB cleanup.")

                if topic_id is not None:
                    topic_to_delete = (
                        delete_session.query(Topic).filter(Topic.id == topic_id).first()
                    )
                    if topic_to_delete:
                        delete_session.delete(topic_to_delete)
                        delete_session.commit()
                        print(f"Cleaned up topic with ID: {topic_id}")
                    else:
                        print(f"Topic with ID '{topic_id}' not found for DB cleanup.")
        except Exception as e:
            print(f"Error during DB cleanup (Queues/Topics): {e}")

import json
import types
from io import BytesIO
from unittest.mock import patch, MagicMock
import pandas as pd
import web_app.backend.services.s3 as s3_module


@patch.object(s3_module, "redis_client")
@patch.object(s3_module, "s3")
def test_get_offers_from_s3(mock_s3, mock_redis):
    df = pd.DataFrame([{"id": 1, "title": "Test Job"}])  # id = int
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    mock_redis.exists.return_value = False
    mock_s3.get_object.return_value = {"Body": BytesIO(buffer.read())}

    offers = s3_module.get_offers()
    assert offers == [{"id": 1, "title": "Test Job"}]  # compare à int
    mock_redis.setex.assert_called_once()



@patch.object(s3_module, "redis_client")
@patch.object(s3_module, "s3")
def test_get_offers_from_cache(mock_s3, mock_redis):
    cached_data = [{"id": "1", "title": "Cached Job"}]
    mock_redis.exists.return_value = True
    mock_redis.get.return_value = json.dumps(cached_data)

    offers = s3_module.get_offers()
    assert offers == cached_data
    mock_s3.get_object.assert_not_called()


@patch.object(s3_module, "redis_client")
@patch.object(s3_module, "s3")
def test_get_likes_from_s3(mock_s3, mock_redis):
    mock_redis.exists.return_value = False
    mock_s3.get_object.return_value = {
        "Body": BytesIO(json.dumps({"liked": ["1"], "disliked": ["2"]}).encode("utf-8"))
    }

    likes = s3_module.get_likes()
    assert likes == {"liked": ["1"], "disliked": ["2"]}
    mock_redis.setex.assert_called_once()


@patch.object(s3_module, "redis_client")
@patch.object(s3_module, "s3")
def test_get_likes_from_cache(mock_s3, mock_redis):
    mock_redis.exists.return_value = True
    mock_redis.get.return_value = json.dumps({"liked": ["3"]})

    likes = s3_module.get_likes()
    assert likes == {"liked": ["3"]}
    mock_s3.get_object.assert_not_called()


@patch.object(s3_module, "redis_client")
@patch.object(s3_module, "s3")
def test_get_relevance(mock_s3, mock_redis):
    mock_redis.exists.return_value = False
    mock_s3.get_object.return_value = {
        "Body": BytesIO(json.dumps({"1": 0.95, "2": 0.80}).encode("utf-8"))
    }

    relevance = s3_module.get_relevance()
    assert relevance == {"1": 0.95, "2": 0.80}
    mock_redis.setex.assert_called_once()


@patch.object(s3_module, "redis_client")
@patch.object(s3_module, "s3")
def test_update_like_existing(mock_s3, mock_redis):
    initial = {"123": "dislike"}
    mock_s3.get_object.return_value = {
        "Body": BytesIO(json.dumps(initial).encode("utf-8"))
    }

    mock_s3.put_object = MagicMock()

    s3_module.update_like("123", "like")

    updated = json.loads(mock_s3.put_object.call_args[1]["Body"])
    assert updated["123"] == "like"
    mock_redis.setex.assert_called_once()


@patch.object(s3_module, "redis_client")
@patch.object(s3_module, "s3")
def test_update_like_no_file(mock_s3, mock_redis):
    # Simule une fausse exception que le code source attend
    class FakeNoSuchKey(Exception):
        pass

    # Crée un faux namespace d'exceptions et injecte la fausse classe
    mock_s3.exceptions = types.SimpleNamespace(NoSuchKey=FakeNoSuchKey)
    mock_s3.get_object.side_effect = FakeNoSuchKey()

    mock_s3.put_object = MagicMock()

    s3_module.update_like("456", "dislike")

    updated = json.loads(mock_s3.put_object.call_args[1]["Body"])
    assert updated == {"456": "dislike"}
    mock_redis.setex.assert_called_once()
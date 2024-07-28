import pytest


@pytest.mark.asyncio
async def test_get_korean_card_not_found(client, data_in_db):
    response = await client.get("/get_korean_card", params={"front": "방학"})
    assert response.status_code == 404
    json_response = response.json()
    assert json_response == {"detail": "card not found"}


@pytest.mark.asyncio
async def test_get_korean_card(client, data_in_db):
    response = await client.get("/get_korean_card", params={"front": "아버지"})
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["front"] == "아버지"
    assert json_response["back"] == "父親"
    assert isinstance(json_response["vector"], list)


@pytest.mark.asyncio
async def test_find_similar(client, data_in_db):
    response = await client.get("/find_similar", params={"word": "아버지"})
    assert response.status_code == 200
    json_response = response.json()
    print(json_response["recommendation"])

    assert json_response["recommendation"][0]["word"] == "아빠"
    assert json_response["recommendation"][1]["word"] == "아가씨"
    assert json_response["recommendation"][2]["word"] == "오빠"

    for i in range(len(json_response["recommendation"])):
        assert json_response["recommendation"][i]["similarity"] > 0.5


@pytest.mark.asyncio
async def test_find_similar_not_found(client, data_in_db):
    response = await client.get("/find_similar", params={"word": "방학"})
    assert response.status_code == 404
    response_json = response.json()
    assert response_json == {"detail": "card not found"}


@pytest.mark.asyncio
async def test_find_similar_no_similar(client, data_in_db):
    response = await client.get("/find_similar", params={"word": "방탄소년단"})
    assert response.status_code == 405
    response_json = response.json()
    assert response_json == {"detail": "No similar word found"}

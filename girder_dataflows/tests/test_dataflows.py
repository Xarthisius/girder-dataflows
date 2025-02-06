import pytest
from pytest_girder.assertions import assertStatus

@pytest.mark.plugin("dataflows")
def test_dataflows(server, user):

    resp = server.request(
        path="/dataflow",
        method="POST",
        user=user,
        params={"name": "", "spec": {}},
    )
    assertStatus(resp, 400)
    assert resp.json["message"] == "Dataflow name must not be empty."


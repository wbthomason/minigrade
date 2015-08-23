defmodule Minigrade.AssignmentControllerTest do
  use Minigrade.ConnCase

  alias Minigrade.Assignment
  @valid_attrs %{build: "some content", description: "some content", name: "some content", open: true, points: "120.5", test: "some content"}
  @invalid_attrs %{}

  setup do
    conn = conn() |> put_req_header("accept", "application/json")
    {:ok, conn: conn}
  end

  test "lists all entries on index", %{conn: conn} do
    conn = get conn, assignment_path(conn, :index)
    assert json_response(conn, 200)["data"] == []
  end

  test "shows chosen resource", %{conn: conn} do
    assignment = Repo.insert! %Assignment{}
    conn = get conn, assignment_path(conn, :show, assignment)
    assert json_response(conn, 200)["data"] == %{
      "id" => assignment.id
    }
  end

  test "does not show resource and instead throw error when id is nonexistent", %{conn: conn} do
    assert_raise Ecto.NoResultsError, fn ->
      get conn, assignment_path(conn, :show, -1)
    end
  end

  test "creates and renders resource when data is valid", %{conn: conn} do
    conn = post conn, assignment_path(conn, :create), assignment: @valid_attrs
    assert json_response(conn, 201)["data"]["id"]
    assert Repo.get_by(Assignment, @valid_attrs)
  end

  test "does not create resource and renders errors when data is invalid", %{conn: conn} do
    conn = post conn, assignment_path(conn, :create), assignment: @invalid_attrs
    assert json_response(conn, 422)["errors"] != %{}
  end

  test "updates and renders chosen resource when data is valid", %{conn: conn} do
    assignment = Repo.insert! %Assignment{}
    conn = put conn, assignment_path(conn, :update, assignment), assignment: @valid_attrs
    assert json_response(conn, 200)["data"]["id"]
    assert Repo.get_by(Assignment, @valid_attrs)
  end

  test "does not update chosen resource and renders errors when data is invalid", %{conn: conn} do
    assignment = Repo.insert! %Assignment{}
    conn = put conn, assignment_path(conn, :update, assignment), assignment: @invalid_attrs
    assert json_response(conn, 422)["errors"] != %{}
  end

  test "deletes chosen resource", %{conn: conn} do
    assignment = Repo.insert! %Assignment{}
    conn = delete conn, assignment_path(conn, :delete, assignment)
    assert response(conn, 204)
    refute Repo.get(Assignment, assignment.id)
  end
end

defmodule Minigrade.AssignmentTest do
  use Minigrade.ModelCase

  alias Minigrade.Assignment

  @valid_attrs %{build: "some content", description: "some content", name: "some content", open: true, points: "120.5", test: "some content"}
  @invalid_attrs %{}

  test "changeset with valid attributes" do
    changeset = Assignment.changeset(%Assignment{}, @valid_attrs)
    assert changeset.valid?
  end

  test "changeset with invalid attributes" do
    changeset = Assignment.changeset(%Assignment{}, @invalid_attrs)
    refute changeset.valid?
  end
end

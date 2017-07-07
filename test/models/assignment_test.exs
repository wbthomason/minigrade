defmodule Minigrade.AssignmentTest do
  use Minigrade.ModelCase

  alias Minigrade.Assignment

  @valid_attrs %{description: "some content", name: "some content", submission_files: []}
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

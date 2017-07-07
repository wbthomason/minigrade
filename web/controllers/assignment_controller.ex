defmodule Minigrade.AssignmentController do
  use Minigrade.Web, :controller

  alias Minigrade.Assignment

  def index(conn, _params) do
    assignments = Repo.all(Assignment)
    render(conn, "index.html", assignments: assignments)
  end

  def show(conn, %{"id" => id}) do
    assignment = Repo.get!(Assignment, id)
    render(conn, "show.html", assignment: assignment)
  end
end

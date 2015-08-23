defmodule Minigrade.AssignmentController do
  use Minigrade.Web, :controller

  alias Minigrade.Assignment

  plug :scrub_params, "assignment" when action in [:create, :update]

  def index(conn, _params) do
    assignments = Repo.all(Assignment)
    render(conn, "index.json", assignments: assignments)
  end

  def create(conn, %{"assignment" => assignment_params}) do
    changeset = Assignment.changeset(%Assignment{}, assignment_params)

    case Repo.insert(changeset) do
      {:ok, assignment} ->
        conn
        |> put_status(:created)
        |> render("show.json", assignment: assignment)
      {:error, changeset} ->
        conn
        |> put_status(:unprocessable_entity)
        |> render(Minigrade.ChangesetView, "error.json", changeset: changeset)
    end
  end

  def show(conn, %{"id" => id}) do
    assignment = Repo.get!(Assignment, id)
    render conn, "show.json", assignment: assignment
  end

  def update(conn, %{"id" => id, "assignment" => assignment_params}) do
    assignment = Repo.get!(Assignment, id)
    changeset = Assignment.changeset(assignment, assignment_params)

    case Repo.update(changeset) do
      {:ok, assignment} ->
        render(conn, "show.json", assignment: assignment)
      {:error, changeset} ->
        conn
        |> put_status(:unprocessable_entity)
        |> render(Minigrade.ChangesetView, "error.json", changeset: changeset)
    end
  end

  def delete(conn, %{"id" => id}) do
    assignment = Repo.get!(Assignment, id)

    # Here we use delete! (with a bang) because we expect
    # it to always work (and if it does not, it will raise).
    assignment = Repo.delete!(assignment)

    send_resp(conn, :no_content, "")
  end
end

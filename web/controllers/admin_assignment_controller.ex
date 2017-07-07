defmodule Minigrade.Admin.AssignmentController do
  use Minigrade.Web, :controller

  alias Minigrade.Assignment

  def index(conn, _params) do
    assignments = Repo.all(Assignment)
    render(conn, "index.html", assignments: assignments)
  end

  def new(conn, _params) do
    changeset = Assignment.changeset(%Assignment{})
    render(conn, "new.html", changeset: changeset)
  end

  def create(conn, %{"assignment" => assignment_params}) do
    changeset = Assignment.changeset(%Assignment{}, assignment_params)

    case Repo.insert(changeset) do
      {:ok, _assignment} ->
        conn
        |> put_flash(:info, "Assignment created successfully.")
        |> redirect(to: assignment_path(conn, :index))
      {:error, changeset} ->
        render(conn, "new.html", changeset: changeset)
    end
  end

  def show(conn, %{"id" => id}) do
    assignment = Repo.get!(Assignment, id)
    render(conn, "show.html", assignment: assignment)
  end

  def edit(conn, %{"id" => id}) do
    assignment = Repo.get!(Assignment, id)
    changeset = Assignment.changeset(assignment)
    render(conn, "edit.html", assignment: assignment, changeset: changeset)
  end

  def update(conn, %{"id" => id, "assignment" => assignment_params}) do
    assignment_params = Map.put_new(assignment_params, "submission_files", nil)
    assignment = Repo.get!(Assignment, id)
    changeset = Assignment.changeset(assignment, assignment_params)

    case Repo.update(changeset) do
      {:ok, assignment} ->
        conn
        |> put_flash(:info, "Assignment updated successfully.")
        |> redirect(to: assignment_path(conn, :show, assignment))
      {:error, changeset} ->
        render(conn, "edit.html", assignment: assignment, changeset: changeset)
    end
  end

  def delete(conn, %{"id" => id}) do
    assignment = Repo.get!(Assignment, id)

    # Here we use delete! (with a bang) because we expect
    # it to always work (and if it does not, it will raise).
    Repo.delete!(assignment)

    conn
    |> put_flash(:info, "Assignment deleted successfully.")
    |> redirect(to: assignment_path(conn, :index))
  end
end

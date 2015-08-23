defmodule Minigrade.AssignmentView do
  use Minigrade.Web, :view

  def render("index.json", %{assignments: assignments}) do
    %{data: render_many(assignments, Minigrade.AssignmentView, "assignment.json")}
  end

  def render("show.json", %{assignment: assignment}) do
    %{data: render_one(assignment, Minigrade.AssignmentView, "assignment.json")}
  end

  def render("assignment.json", %{assignment: assignment}) do
    %{id: assignment.id
      name: assignment.name
      description: assignment.description
      points: assignment.points
      open: assignment.open
      build: assignment.build
      test: assignment.test
      course: assignment.course}
  end
end

defmodule Minigrade.AssignmentController do
  use Minigrade.Web, :controller

  def index(conn, _params) do
    render conn, "index.html"
  end

  def show(conn, _params) do
    render conn, "index.html"
  end
end
